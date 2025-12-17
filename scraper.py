import requests
from bs4 import BeautifulSoup
import json

# Site Bilgileri
BASE_SITE = "https://bosssports276.com"
# Bot olarak algılanmamak için standart bir tarayıcı User-Agent'ı
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_matches():
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": BASE_SITE + "/"
    }
    
    try:
        response = requests.get(BASE_SITE, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        football_tab = soup.find("div", id="pills-football")
        
        items = []
        if not football_tab:
            print("❌ Futbol tablosu bulunamadı.")
            return items

        for block in football_tab.find_all("div", class_="match-block"):
            teams = block.find_all("div", class_="name")
            time_div = block.find("div", class_="time")
            watch_id = block.get("data-watch")

            if len(teams) >= 2 and watch_id:
                team_names = f"{teams[0].text.strip()} - {teams[1].text.strip()}"
                match_time = time_div.text.strip() if time_div else "Canlı"
                
                # Senin verdiğin worker link yapısı
                m3u8_url = f"https://bo.61c25179391c19fefc.workers.dev/f6e33e69e0fdec0a7780e174f3c8b2c2/-/{watch_id}/playlist.m3u8"
                
                # İzleme sayfası (Referer için kullanılır)
                watch_page = f"{BASE_SITE}/play.html?id={watch_id}"

                item = {
                    "service": "iptv",
                    "title": team_names,
                    "playlistURL": "",
                    "media_url": m3u8_url,
                    "url": m3u8_url,
                    "h1Key": "User-Agent",
                    "h1Val": USER_AGENT,
                    "h2Key": "referer",
                    "h2Val": watch_page,
                    "h3Key": "origin",
                    "h3Val": BASE_SITE,
                    "h4Key": "accept",
                    "h4Val": "*/*",
                    "h5Key": "0",
                    "h5Val": "0",
                    "thumb_square": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjir66ltBgoXlUmzSvRCqal0NE-i7n9bx5k5nZBFW9gXqQHgHZFBF23HUpXBIgLzaa9AgSrbIeQGna2k3XbthGHvZtpqabB_PWOVRN8DM9FRu_MLjPpdKcRISB0yMQa0MEho8eZ1NHCVJXkjGlqroOSBzVR5KbzdhaRIqeTlY54NRifzwF0Bb8ZwDxsI0w/s1600/IMG_20211126_024249.png",
                    "group": match_time
                }
                items.append(item)
        
        return items
    except Exception as e:
        print(f"Hata: {e}")
        return []

def main():
    match_list = get_matches()
    
    final_json = {
        "list": {
            "service": "iptv",
            "title": "Boss Sports Canlı Maçlar",
            "item": match_list
        }
    }

    with open('matches.json', 'w', encoding='utf-8') as f:
        json.dump(final_json, f, ensure_ascii=False, indent=4)
    print(f"✅ {len(match_list)} maç için JSON başarıyla güncellendi.")

if __name__ == "__main__":
    main()
