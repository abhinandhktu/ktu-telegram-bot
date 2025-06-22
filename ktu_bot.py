import os
import time
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import urllib3
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SENT_NOTICES_FILE = "sent_notices.txt"
URL = "https://ktu.edu.in/Menu/announcements"

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
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=data)
        print(f"✅ Telegram status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Failed to send Telegram message: {e}")

def get_announcements():
    chromedriver_autoinstaller.install()
    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    time.sleep(5)  # Let JS load

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    notices = []
    items = soup.select(".announcement-row")
    five_days_ago = datetime.now() - timedelta(days=5)

    for item in items:
        date_el = item.select_one(".ann-date")
        title_el = item.select_one(".ann-title")
        link_el = item.select_one("a")

        if not (date_el and title_el and link_el):
            continue

        date_text = date_el.text.strip()
        title = title_el.text.strip()
        link = "https://ktu.edu.in" + link_el['href']
        try:
            notice_date = datetime.strptime(date_text, "%d-%m-%Y")
        except:
            continue

        if notice_date < five_days_ago:
            continue

        notice_id = f"{title}-{date_text}"
        notices.append((notice_id, title, link, notice_date))

    print(f"🔎 Found {len(notices)} recent notices.")
    return notices

def main():
    print("🚀 Bot started!")
    sent = load_sent_notices()

    while True:
        print("🔍 Checking announcements...")
        try:
            notices = get_announcements()
        except Exception as e:
            print(f"❌ Error while fetching: {e}")
            time.sleep(60)
            continue

        for nid, title, link, ndate in notices:
            if nid in sent:
                continue
            message = (
                f"📢 *KTU Notice ({ndate.strftime('%d-%m-%Y')}):*\n\n"
                f"*{title}*\n👉 [View Notice]({link})"
            )
            send_to_telegram(message)
            save_sent_notice(nid)
            sent.add(nid)

        print("⏳ Sleeping 60 seconds...\n")
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
