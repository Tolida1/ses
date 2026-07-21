import requests
import json
import sys

# --- Ayarlar ---
API_URL = "https://bosssports1019.com/api/channels"
BASE_SITE = "https://bosssports1019.com/"
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Yayın linkleri için gönderilecek header'lar (player bunları bekliyor olabilir)
STREAM_REFERER = "https://bosssports1019.com/"
STREAM_ORIGIN = "https://bosssports1019.com"

DEFAULT_THUMB = "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjir66ltBgoXlUmzSvRCqal0NE-i7n9bx5k5nZBFW9gXqQHgHZFBF23HUpXBIgLzaa9AgSrbIeQGna2k3XbthGHvZtpqabB_PWOVRN8DM9FRu_MLjPpdKcRISB0yMQa0MEho8eZ1NHCVJXkjGlqroOSBzVR5KbzdhaRIqeTlY54NRifzwF0Bb8ZwDxsI0w/s1600/IMG_20211126_024249.png"


def _write_output(items):
    """Çıktıyı matches.json dosyasına yazar."""
    output = {"list": {"service": "iptv", "title": "iptv", "item": items}}
    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)


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
        _write_output([])
        return

    # --- DEBUG ---
    print("=" * 50)
    print(f"Status Code : {r.status_code}")
    print(f"İçerik uzunluğu : {len(r.text)}")
    print("=" * 50)

    if r.status_code != 200:
        print(f"❌ API 200 dönmedi (status={r.status_code}). Yanıtın başı:")
        print(r.text[:500])
        _write_output([])
        return

    try:
        payload = r.json()
    except Exception as e:
        print(f"❌ JSON parse hatası: {e}")
        print("Yanıtın başı:", r.text[:500])
        _write_output([])
        return

    if not payload.get("success"):
        print(f"⚠️  API success=false döndü. Payload: {str(payload)[:300]}")

    channels = payload.get("data", [])
    print(f"API'den gelen kanal sayısı: {len(channels)}")

    items = []
    for ch in channels:
        title = ch.get("home", "").strip()

        # Yayın linkini bul: önce streams[].url, olmazsa videoid
        stream_url = ""
        streams = ch.get("streams", [])
        if streams:
            # isPlayed=true olanı tercih et, yoksa ilkini al
            played = next((s for s in streams if s.get("isPlayed")), None)
            chosen = played or streams[0]
            stream_url = chosen.get("url", "")
        if not stream_url:
            stream_url = ch.get("videoid", "")

        # İsim veya link yoksa atla
        if not title or not stream_url:
            print(f"   ⚠️  Atlandı (title='{title}', url boş mu={not stream_url})")
            continue

        logo = ch.get("home_icon") or DEFAULT_THUMB
        group = ch.get("league") or ch.get("category") or "Live TV"

        items.append({
            "service": "iptv",
            "title": title,
            "playlistURL": "",
            "media_url": stream_url,
            "url": stream_url,
            "h1Key": "referer",
            "h1Val": STREAM_REFERER,
            "h2Key": "origin",
            "h2Val": STREAM_ORIGIN,
            "h3Key": "User-Agent",
            "h3Val": USER_AGENT,
            "h4Key": "0",
            "h4Val": "0",
            "h5Key": "0",
            "h5Val": "0",
            "thumb_square": logo,
            "group": group,
        })

    _write_output(items)
    print(f"✅ Başarılı: {len(items)} kanal güncellendi.")


if __name__ == "__main__":
    main()
