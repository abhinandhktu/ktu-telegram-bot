import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SENT_NOTICES_FILE = "sent_notices.txt"

def load_sent_notices():
    try:
        with open(SENT_NOTICES_FILE, "r") as f:
            return set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        print("No sent notices file found, starting fresh.")
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
    try:
        response = requests.post(url, data=payload)
        print(f"Telegram API response: {response.status_code}")
        if response.status_code != 200:
            print(f"Telegram error response: {response.text}")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def get_latest_notices():
    url = "https://ktu.edu.in/eu/core/announcements.htm"
    try:
        print(f"Fetching notices from {url} ...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Network error while fetching notices: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    notices = []
    rows = soup.select("table table tr")
    five_days_ago = datetime.now() - timedelta(days=5)

    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 2:
            continue
        date_text = cols[0].text.strip()
        title_td = cols[1]

        try:
            notice_date = datetime.strptime(date_text, "%d-%m-%Y")
        except Exception as e:
            print(f"Skipping row with invalid date '{date_text}': {e}")
            continue

        if notice_date < five_days_ago:
            continue

        link_tag = title_td.find('a')
        if link_tag:
            link = "https://ktu.edu.in" + link_tag['href']
            title = link_tag.text.strip()
        else:
            title = title_td.text.strip()
            link = "https://ktu.edu.in/eu/core/announcements.htm"

        notice_id = f"{title}-{date_text}"
        notices.append((notice_id, title, link, notice_date))

    print(f"Found {len(notices)} notices from the last 5 days.")
    return notices

def main():
    print("Bot started!")
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
            print(f"Sent new notice: {title}")

        print("Sleeping for 60 seconds...\n")
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
