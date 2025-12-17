import requests
from bs4 import BeautifulSoup
import json
import re

BASE_SITE = "https://bosssports276.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_real_m3u8(master_url):
    """Master playlist içinden gerçek chunklist linkini ayıklar."""
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": "https://bosssports276.com/",
        "Origin": "https://bosssports276.com"
    }
    try:
        response = requests.get(master_url, headers=headers, timeout=5)
        if response.status_code == 200:
            # Satırları tara ve .m3u8 ile biten ilk gerçek linki bul
            lines = response.text.splitlines()
            for line in lines:
                if "chunklist" in line or ".m3u8" in line and not line.startswith("#"):
                    # Eğer link tam değilse (relative path), ana domaini ekle
                    if line.startswith("http"):
                        return line
                    else:
                        base_path = master_url.rsplit('/', 1)[0]
                        return f"{base_path}/{line}"
        return master_url # Bulamazsa eskisini dön
    except:
        return master_url

def get_matches():
    headers = {"User-Agent": USER_AGENT, "Referer": BASE_SITE + "/"}
    try:
        r = requests.get(BASE_SITE, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        football_tab = soup.find("div", id="pills-football")
        
        items = []
        if not football_tab: return items

        for block in football_tab.find_all("div", class_="match-block"):
            teams = block.find_all("div", class_="name")
            watch_id = block.get("data-watch")
            time_val = block.find("div", class_="time").text.strip() if block.find("div", class_="time") else "Canlı"

            if len(teams) >= 2 and watch_id:
                title = f"{teams[0].text.strip()} - {teams[1].text.strip()}"
                
                # 1. Aşama: Master Linki Oluştur
                master_m3u8 = f"https://bo.0155aac4739f3ffaae.workers.dev/f6e33e69e0fdec0a7780e174f3c8b2c2/-/{watch_id}/playlist.m3u8"
                
                # 2. Aşama: İçine gir ve Gerçek HD linki al
                real_url = get_real_m3u8(master_m3u8)

                items.append({
                    "service": "iptv",
                    "title": title,
                    "media_url": real_url,
                    "url": real_url,
                    "h1Key": "referer",
                    "h1Val": "https://bosssports276.com/",
                    "h2Key": "origin",
                    "h2Val": "https://bosssports276.com",
                    "h3Key": "0", "h3Val": "0",
                    "h4Key": "0", "h4Val": "0",
                    "h5Key": "0", "h5Val": "0",
                    "thumb_square": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjir66ltBgoXlUmzSvRCqal0NE-i7n9bx5k5nZBFW9gXqQHgHZFBF23HUpXBIgLzaa9AgSrbIeQGna2k3XbthGHvZtpqabB_PWOVRN8DM9FRu_MLjPpdKcRISB0yMQa0MEho8eZ1NHCVJXkjGlqroOSBzVR5KbzdhaRIqeTlY54NRifzwF0Bb8ZwDxsI0w/s1600/IMG_20211126_024249.png",
                    "group": time_val
                })
        return items
    except Exception as e:
        print(f"Hata: {e}")
        return []

def main():
    match_list = get_matches()
    final_json = {"list": {"service": "iptv", "title": "iptv", "item": match_list}}
    with open('matches.json', 'w', encoding='utf-8') as f:
        json.dump(final_json, f, ensure_ascii=False, indent=4)
    print(f"✅ {len(match_list)} maç için gerçek HD linkleri çekildi.")

if __name__ == "__main__":
    main()
