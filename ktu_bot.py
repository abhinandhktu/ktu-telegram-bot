import os
import time
import requests
from datetime import datetime, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
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
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    resp = requests.post(url, data=payload)
    print("Telegram response:", resp.status_code)

def get_announcements():
    url = "https://api.ktu.edu.in/ktu-web-portal-api/anon/announcemnts"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def main():
    sent_notices = load_sent_notices()
    announcements = get_announcements()

    five_days_ago = datetime.now() - timedelta(days=5)

    for ann in announcements:
        # Check date field - adapt key name based on actual API response
        # For example, suppose 'date' field contains the date string
        date_str = ann.get('date') or ann.get('publishedDate') or ann.get('createdDate')
        if not date_str:
            continue

        # Example: API might return ISO date string like "2025-06-22T10:20:30Z"
        try:
            ann_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            print("Date parse error:", date_str)
            continue

        if ann_date >= five_days_ago:
            # Create a unique ID for tracking to avoid duplicates
            notice_id = ann.get('id') or ann.get('announcementId') or ann.get('title', '') + date_str
            if notice_id in sent_notices:
                print(f"Already sent: {ann.get('title')}")
                continue

            title = ann.get('title', 'No Title')
            link = ann.get('link', '#')  # use actual link key or construct if needed
            if not link.startswith('http'):
                # If link is relative or missing, fallback to main announcements page
                link = "https://ktu.edu.in/eu/core/announcements.htm"

            message = f"📢 *KTU Notice ({ann_date.strftime('%d-%m-%Y')}):*\n\n*{title}*\n\n👉 [View Notice]({link})"
            send_to_telegram(message)
            print(f"Sent: {title}")
            save_sent_notice(notice_id)

if __name__ == "__main__":
    main()
