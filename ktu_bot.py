import requests
from bs4 import BeautifulSoup
import time
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
CHECK_INTERVAL = 30  # seconds

def fetch_latest():
    url = "https://ktu.edu.in/eu/core/announcements.htm"
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")
    link = soup.select_one(".panel-title a")
    title = link.get_text(strip=True) if link else None
    href = link["href"] if link else None
    return title, href

def send(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def main():
    last = None
    while True:
        try:
            title, href = fetch_latest()
            if title and (title != last):
                msg = f"📢 *New KTU Notice*\n{title}\n\n[View Notice](https://ktu.edu.in{href})"
                send(msg)
                last = title
        except Exception as e:
            send(f"⚠️ Bot error: `{e}`")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
