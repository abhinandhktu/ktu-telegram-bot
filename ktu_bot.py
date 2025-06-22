def get_latest_notices():
    url = "https://ktu.edu.in/eu/core/announcements.htm"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️ Network error fetching notices: {e}")
        return []  # Return empty list on error

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
        except Exception:
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

    return notices
