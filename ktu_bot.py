import os
import time
import requests
import urllib3
from bs4 import BeautifulSoup

# Disable SSL warnings (for ktu.edu.in)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Read environment variables from Railway
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# Telegram send function
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    print("✅ Telegram response:", response.status_code)

# Scrape KTU announcements
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

# Store last notice to avoid duplicates
last_notice = ""

# Loop forever (every 5 minutes)
while True:
    print("🔄 Checking for new KTU notices...")
    title, link = get_latest_notice()

    if title and title != last_notice:
        message = f"📢 *New KTU Notice:*\n\n*{title}*\n\n👉 [Click here to view]({link})"
        send_to_telegram(message)
        last_notice = title
        print(f"📨 Sent: {title}")
    else:
        print("ℹ️ No new notice.")

    time.sleep(30)  # wait 5 minutes
