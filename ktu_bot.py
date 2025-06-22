import os
import time
import requests
import urllib3
from bs4 import BeautifulSoup

# Disable SSL warnings for ktu.edu.in
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Read environment variables
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# File to store last notice title
LAST_NOTICE_FILE = "last_notice.txt"

def save_last_notice(title):
    with open(LAST_NOTICE_FILE, 'w') as f:
        f.write(title)

def load_last_notice():
    try:
        with open(LAST_NOTICE_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    print("✅ Telegram response:", response.status_code)

def get_latest_notice():
    url = "https://ktu.edu.in/eu/core/announcements.htm"
    try:
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        notice = soup.find('td', class_='notice_title')
        title = notice.text.strip()
        href = notice.find('a')['href']
        full_link = f"https://ktu.edu.in{href}"
        return title, full_link
    except Exception as e:
        print(f"⚠ Error fetching notice: {e}")
        return None, None

last_notice = load_last_notice()
print(f"Last notice loaded: '{last_notice}'")

while True:
    print("🔄 Checking for new KTU notices...")
    title, link = get_latest_notice()

    if title and title != last_notice:
        message = f"📢 *New KTU Notice:*\n\n*{title}*\n\n👉 [Click here to view]({link})"
        send_to_telegram(message)
        last_notice = title
        save_last_notice(title)
        print(f"📨 Sent new notice: {title}")
    else:
        print("ℹ️ No new notice or already sent.")

    time.sleep(30)  # wait 5 minutes
