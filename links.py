import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

# ==================================================
# USER AGENT (TAM)
# ==================================================
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
    "Connection": "keep-alive"
}

# ==================================================
# 1️⃣ AKTİF SİTEYİ BUL (GENEL)
# ==================================================
def find_active_site(start=200, end=350):
    for i in range(start, end + 1):
        url = f"https://bosssports{i}.com/"
        try:
            r = requests.get(url, headers=HEADERS, timeout=6)
            if r.status_code == 200 and "match" in r.text.lower():
                print(f"✅ Aktif site: {url}")
                return url.rstrip("/")
        except:
            pass
    return None


BASE_SITE = find_active_site()
if not BASE_SITE:
    print("❌ Aktif site bulunamadı")
    exit()

REFERER = BASE_SITE + "/"
ORIGIN = BASE_SITE

# ==================================================
# 2️⃣ ANA SAYFA
# ==================================================
html = requests.get(BASE_SITE, headers=HEADERS, timeout=10).text
soup = BeautifulSoup(html, "html.parser")

football_tab = soup.find("div", id=lambda x: x and "football" in x.lower())
if not football_tab:
    print("❌ Football alanı bulunamadı")
    exit()

items = []

# ==================================================
# 3️⃣ MAÇLARI ÇEK
# ==================================================
for block in football_tab.find_all("div"):
    watch_id = block.get("data-watch")
    if not watch_id:
        continue

    names = block.find_all("div", class_="name")
    time_div = block.find("div", class_="time")

    if len(names) < 2 or not time_div:
        continue

    title = f"{names[0].text.strip()} - {names[1].text.strip()}"
    match_time = time_div.text.strip()

    # ------------------------------------------------
    # play.html PARAMETRELERİNİ OLUŞTUR
    # (x?id sadece domain için yardımcı)
    # ------------------------------------------------
    try:
        rx = requests.get(
            f"{BASE_SITE}/x?id={watch_id}",
            headers=HEADERS,
            timeout=8
        ).json()
    except:
        continue

    if not isinstance(rx, list) or not rx:
        continue

    real_links = []

    for row in rx:
        if not row or not isinstance(row[0], str):
            continue

        worker_domain = row[0]

        # ⚠️ play.html mantığındaki TETİK URL
        # path/hash sabit değil → redirect çözer
        trigger_url = f"https://{worker_domain}/trigger/{watch_id}"

        try:
            r = requests.get(
                trigger_url,
                headers=HEADERS,
                timeout=10,
                allow_redirects=True
            )

            if r.status_code == 200 and r.url.endswith("playlist.m3u8"):
                real_links.append(r.url)

        except:
            pass

    if not real_links:
        continue

    # ==================================================
    # JSON ITEM
    # ==================================================
    items.append({
        "service": "iptv",
        "title": title,
        "media_url": real_links[0],
        "url": real_links[0],
        "backup_links": real_links[1:],

        "h1Key": "user-agent",
        "h1Val": USER_AGENT,

        "h2Key": "referer",
        "h2Val": REFERER,

        "h3Key": "origin",
        "h3Val": ORIGIN,

        "h4Key": "accept",
        "h4Val": "*/*",

        "group": match_time
    })

    print(f"✔ {title} → gerçek m3u8 alındı")

# ==================================================
# 4️⃣ JSON YAZ
# ==================================================
output = {
    "list": {
        "service": "iptv",
        "title": "Auto Streams",
        "item": items
    }
}

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n🎯 output.json oluşturuldu ({len(items)} öğe)")
