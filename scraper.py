import requests
from bs4 import BeautifulSoup
import json
import sys

BASE_SITE = "https://bosssports1019.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def get_real_hd_link(master_url):
    """
    Master m3u8 içine girer ve gerçek chunklist_hd.m3u8 linkini ayıklar.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "referer": "https://bosssports276.com/",
        "origin": "https://bosssports276.com"
    }
    try:
        r = requests.get(master_url, headers=headers, timeout=10)
        if r.status_code == 200:
            lines = r.text.splitlines()
            for line in lines:
                if ".m3u8" in line and not line.startswith("#"):
                    if line.startswith("http"):
                        return line
                    else:
                        base = master_url.rsplit('/', 1)[0]
                        return f"{base}/{line}"
        else:
            print(f"   ⚠️  Master m3u8 status: {r.status_code} -> {master_url}")
        return master_url
    except Exception as e:
        print(f"   ⚠️  get_real_hd_link hata: {e}")
        return master_url


def main():
    headers = {"User-Agent": USER_AGENT, "referer": BASE_SITE}
    try:
        r = requests.get(BASE_SITE, headers=headers, timeout=15)

        # ---- DEBUG ÇIKTILARI ----
        print("=" * 50)
        print(f"Status Code       : {r.status_code}")
        print(f"HTML uzunluğu     : {len(r.text)}")
        print(f"match-block sayısı: {r.text.count('match-block')}")
        print(f"pills-football var mı: {'pills-football' in r.text}")
        print("=" * 50)

        # Status 200 değilse muhtemelen bot koruması / bloklanma
        if r.status_code != 200:
            print(f"❌ Site 200 dönmedi (status={r.status_code}). Muhtemelen bot koruması veya erişim engeli.")
            # Yine de debug için HTML'i kaydet
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(r.text)
            # Boş çıktı yaz ve çık
            _write_output([])
            return

        soup = BeautifulSoup(r.text, "html.parser")
        football_tab = soup.find("div", id="pills-football")

        # football_tab bulunamazsa uyar ve HTML'i incelemek için kaydet
        if not football_tab:
            print("❌ 'pills-football' bulunamadı. İçerik JS ile yükleniyor olabilir "
                  "veya id/class isimleri değişmiş olabilir.")
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(r.text)
            print("   -> debug.html kaydedildi, gerçek yapıyı buradan kontrol et.")
            _write_output([])
            return

        items = []
        blocks = football_tab.find_all("div", class_="match-block")
        print(f"Bulunan match-block sayısı (parse sonrası): {len(blocks)}")

        for block in blocks:
            teams = block.find_all("div", class_="name")
            watch_id = block.get("data-watch")
            time_div = block.find("div", class_="time")
            time_val = time_div.text.strip() if time_div else "Canlı"

            if len(teams) >= 2 and watch_id:
                title = f"{teams[0].text.strip()} - {teams[1].text.strip()}"

                master_m3u8 = (
                    f"https://bo.0155aac4739f3ffaae.workers.dev/"
                    f"f6e33e69e0fdec0a7780e174f3c8b2c2/-/{watch_id}/playlist.m3u8"
                )

                real_hd_url = get_real_hd_link(master_m3u8)

                items.append({
                    "service": "iptv",
                    "title": title,
                    "playlistURL": "",
                    "media_url": real_hd_url,
                    "url": real_hd_url,
                    "h1Key": "referer",
                    "h1Val": "https://bosssports276.com/",
                    "h2Key": "origin",
                    "h2Val": "https://bosssports276.com",
                    "h3Key": "User-Agent",
                    "h3Val": USER_AGENT,
                    "h4Key": "0",
                    "h4Val": "0",
                    "h5Key": "0",
                    "h5Val": "0",
                    "thumb_square": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjir66ltBgoXlUmzSvRCqal0NE-i7n9bx5k5nZBFW9gXqQHgHZFBF23HUpXBIgLzaa9AgSrbIeQGna2k3XbthGHvZtpqabB_PWOVRN8DM9FRu_MLjPpdKcRISB0yMQa0MEho8eZ1NHCVJXkjGlqroOSBzVR5KbzdhaRIqeTlY54NRifzwF0Bb8ZwDxsI0w/s1600/IMG_20211126_024249.png",
                    "group": time_val
                })
            else:
                print(f"   ⚠️  Atlandı (teams={len(teams)}, watch_id={watch_id})")

        _write_output(items)
        print(f"✅ Başarılı: {len(items)} maç güncellendi.")

    except Exception as e:
        print(f"❌ Hata: {e}")
        # Hata olsa bile boş dosya yaz ki workflow patlamasın
        _write_output([])


def _write_output(items):
    """Çıktıyı matches.json dosyasına yazar."""
    output = {"list": {"service": "iptv", "title": "iptv", "item": items}}
    with open('matches.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
