import requests
from bs4 import BeautifulSoup
import json

BASE_SITE = "https://bosssports276.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def main():
    headers = {"User-Agent": USER_AGENT, "Referer": BASE_SITE}
    try:
        r = requests.get(BASE_SITE, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        football_tab = soup.find("div", id="pills-football")
        
        items = []
        if football_tab:
            for block in football_tab.find_all("div", class_="match-block"):
                teams = block.find_all("div", class_="name")
                watch_id = block.get("data-watch")
                time_val = block.find("div", class_="time").text.strip() if block.find("div", class_="time") else "Canlı"

                if len(teams) >= 2 and watch_id:
                    title = f"{teams[0].text.strip()} - {teams[1].text.strip()}"
                    m3u8 = f"https://bo.61c25179391c19fefc.workers.dev/f6e33e69e0fdec0a7780e174f3c8b2c2/-/{watch_id}/playlist.m3u8"
                    
                    items.append({
                        "service": "iptv",
                        "title": title,
                        "media_url": m3u8,
                        "url": m3u8,
                        "h1Key": "User-Agent",
                        "h1Val": USER_AGENT,
                        "h2Key": "referer",
                        "h2Val": f"{BASE_SITE}/play.html?id={watch_id}",
                        "h3Key": "origin",
                        "h3Val": BASE_SITE,
                        "group": time_val
                        # Diğer boş keyleri (h4, h5) buraya ekleyebilirsin
                    })

        output = {"list": {"service": "iptv", "title": "Boss Sports", "item": items}}
        
        with open('matches.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
