import requests
import sys

# --- Ayarlar ---
API_URL = "https://bosssports1019.com/api/channels"
BASE_SITE = "https://bosssports1019.com/"
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# M3U içine yazılacak referer (Boss Sports)
REFERER = "https://bosssports1019.com/"

# Çıktı dosyası
OUTPUT_FILE = "boss.m3u"


def write_m3u(entries):
    """entries: (group_title, title, stream_url) tuple listesi"""
    lines = ["#EXTM3U"]
    for group_title, title, url in entries:
        lines.append(f'#EXTINF:-1 group-title="{group_title}",{title}')
        lines.append(f"#EXTVLCOPT:http-user-agent={USER_AGENT}")
        lines.append(f"#EXTVLCOPT:http-referrer={REFERER}")
        lines.append(url)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    headers = {
        "User-Agent": USER_AGENT,
        "referer": BASE_SITE,
        "accept": "application/json",
    }

    try:
        r = requests.get(API_URL, headers=headers, timeout=20)
    except Exception as e:
        print(f"❌ İstek hatası: {e}")
        write_m3u([])
        return

    # --- DEBUG ---
    print("=" * 50)
    print(f"Status Code     : {r.status_code}")
    print(f"İçerik uzunluğu : {len(r.text)}")
    print("=" * 50)

    if r.status_code != 200:
        print(f"❌ API 200 dönmedi (status={r.status_code}). Yanıtın başı:")
        print(r.text[:500])
        write_m3u([])
        return

    try:
        payload = r.json()
    except Exception as e:
        print(f"❌ JSON parse hatası: {e}")
        print("Yanıtın başı:", r.text[:500])
        write_m3u([])
        return

    if not payload.get("success"):
        print(f"⚠️  API success=false döndü. Payload: {str(payload)[:300]}")

    channels = payload.get("data", [])
    print(f"API'den gelen kanal sayısı: {len(channels)}")

    entries = []
    for ch in channels:
        title = (ch.get("home") or "").strip()

        # Yayın linkini bul: önce streams[].url (isPlayed öncelikli), olmazsa videoid
        stream_url = ""
        streams = ch.get("streams", [])
        if streams:
            played = next((s for s in streams if s.get("isPlayed")), None)
            chosen = played or streams[0]
            stream_url = chosen.get("url", "")
        if not stream_url:
            stream_url = ch.get("videoid", "")

        if not title or not stream_url:
            print(f"   ⚠️  Atlandı (title='{title}', url boş mu={not stream_url})")
            continue

        group = ch.get("league") or ch.get("category") or "7/24 Kanallar"
        entries.append((group, title, stream_url))

    write_m3u(entries)
    print(f"✅ Başarılı: {len(entries)} kanal M3U'ya yazıldı -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
