import requests
import json
import os

# ---------- AYARLAR ----------
_1 = os.getenv("SRC_1", "")
_2 = os.getenv("SRC_2", "")
_3 = int(os.getenv("VIDEO_ID", "0"))
BASE_URL = os.getenv("BASE_URL", "")  # örn: https://site.com
OUT_FILE = "links.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*"
}

links = set()

# ---------- CASE 1 (_3 > 10000) ----------
if _3 > 10000:
    data = {
        "AppId": "5000",
        "AppVer": "1",
        "VpcVer": "1.0.12",
        "Language": "en",
        "Token": "",
        "VideoId": _3
    }

    try:
        r = requests.post(
            "https://streamsport365.com/cinema",
            json=data,
            headers=HEADERS,
            timeout=10
        )
        j = r.json()
        if "URL" in j:
            links.add(j["URL"])
    except Exception as e:
        print("API error:", e)

else:
    # ---------- CASE 2 ----------
    try:
        r = requests.get(f"{BASE_URL}/x?id={_3}", headers=HEADERS, timeout=10)
        j = r.json()

        if isinstance(j, list):
            for row in j:
                if row and row[0]:
                    links.add(f"https://{row[0]}/{_2}/-/{_3}/playlist.m3u8")
    except Exception as e:
        print("X error:", e)

    # fallback
    if not links and _1:
        links.add(f"https://{_1}/{_2}/-/{_3}/playlist.m3u8")

# ---------- DOSYAYA YAZ ----------
with open(OUT_FILE, "w") as f:
    for link in sorted(links):
        f.write(link + "\n")
        print(link)
