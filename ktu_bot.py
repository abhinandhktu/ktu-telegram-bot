import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Telegram Bot Token and Chat ID from environment variables
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# File to keep track of sent notices
SENT_NOTICES_FILE = "sent_notices.txt"

def load_sent_notices():
    try:
        with open(SENT_NOTICES_FILE, "r") as f:
            return set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        return set()

def save_sent_notice(notice_id):
    with open(SENT_NOTICES_FILE, "a") as f:
        f.write(notice_id + "\n")

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    print(f"Telegram response status: {response.status_code}")

def get_latest_notices():
    url = "https://ktu.edu.in/eu/core/announcements.htm"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    notices = []
    rows = soup.select("table table tr")  # Selector for the announcements table rows
    five_days_ago = datetime.now() - timedelta(days=5)

    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 2:
            continue
        date_text = cols[0].text.strip()
        title_td = cols[1]

        try:
            notice_date = datetime.strptime(date_text, "%d-%m-%Y")
        except Exception:
            continue

        # Only consider notices within the last 5 days
        if notice_date < five_days_ago:
            continue

        link_tag = title_td.find('a')
        if link_tag:
            link = "https://ktu.edu.in" + link_tag['href']
            title = link_tag.text.strip()
        else:
            title = title_td.text.strip()
            link = "https://ktu.edu.in/eu/core/announcements.htm"

        # Unique ID for each notice
        notice_id = f"{title}-{date_text}"
        notices.append((notice_id, title, link, notice_date))

    return notices

def main():
    sent_notices = load_sent_notices()

    while True:
        print("Checking for new notices...")
        new_notices = get_latest_notices()

        for notice_id, title, link, notice_date in new_notices:
            if notice_id in sent_notices:
                print(f"Already sent: {title}")
                continue

            message = (
                f"📢 *KTU Notice ({notice_date.strftime('%d-%m-%Y')}):*\n\n"
                f"*{title}*\n\n"
                f"👉 [View Notice]({link})"
            )
            send_to_telegram(message)
            save_sent_notice(notice_id)
            sent_notices.add(notice_id)
            print(f"Sent: {title}")

        print("Sleeping for 60 seconds...\n")
        time.sleep(60)  # Wait for 1 minute before checking again

if __name__ == "__main__":
    main()
