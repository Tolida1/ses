import requests
import sys

# ==============================
# SABİT AYARLAR (BURADAN DEĞİŞTİR)
# ==============================
BASE_URL = "https://bosssports276.com"   # site
VIDEO_ID = "777"                         # maç / yayın id
OUT_FILE = "links.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "*/*",
    "Connection": "keep-alive"
}

# ==============================
# DOMAIN TOPLAMA
# ==============================
domains = set()

try:
    url = f"{BASE_URL.rstrip('/')}/x?id={VIDEO_ID}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()

    """
    Beklenen çıktı:
    [
      ["bo.61c25179391c19fefc.workers.dev"],
      ["bo.a91bfa9f3d.workers.dev"],
      ...
    ]
    """

    if isinstance(data, list):
        for row in data:
            if (
                isinstance(row, list)
                and len(row) > 0
                and isinstance(row[0], str)
                and row[0].startswith("bo.")
                and row[0].endswith(".workers.dev")
            ):
                domains.add(row[0])

except Exception as e:
    print("HATA: domainler alınamadı")
    print(e)
    sys.exit(1)

# ==============================
# LINK OLUŞTURMA
# FORMAT:
# https://bo.xxx.workers.dev/777/playlist.m3u8
# ==============================
links = []
for d in sorted(domains):
    links.append(f"https://{d}/{VIDEO_ID}/playlist.m3u8")

# ==============================
# DOSYAYA YAZ
# ==============================
try:
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")
except Exception as e:
    print("HATA: dosya yazılamadı")
    print(e)
    sys.exit(1)

# ==============================
# LOG
# ==============================
print("OLUŞAN LİNKLER:")
for link in links:
    print(link)

print(f"\nToplam link: {len(links)}")
print("links.txt oluşturuldu ✔")
