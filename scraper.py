import requests
from bs4 import BeautifulSoup
import json

BASE_SITE = "https://bosssports276.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_real_hd_link(master_url):
    """
    Master m3u8 içine girer ve gerçek chunklist_hd.m3u8 linkini ayıklar.
    Bu, 'HLS işaretinde kalma' sorununu çözmek için en etkili yoldur.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "referer": "https://bosssports276.com/",
        "origin": "https://bosssports276.com"
    }
    try:
        # Master playlisti oku
        r = requests.get(master_url, headers=headers, timeout=10)
        if r.status_code == 200:
            lines = r.text.splitlines()
            for line in lines:
                # İçinde m3u8 geçen ama yorum satırı (#) olmayan gerçek linki bul
                if ".m3u8" in line and not line.startswith("#"):
                    if line.startswith("http"):
                        return line
                    else:
                        # Eğer link tam değilse, ana dizinle birleştir
                        base = master_url.rsplit('/', 1)[0]
                        return f"{base}/{line}"
        return master_url
    except:
        return master_url

def main():
    headers = {"User-Agent": USER_AGENT, "referer": BASE_SITE + "/"}
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
                    
                    # İlk aşama: Senin verdiğin worker link yapısı
                    master_m3u8 = f"https://bo.0155aac4739f3ffaae.workers.dev/f6e33e69e0fdec0a7780e174f3c8b2c2/-/{watch_id}/playlist.m3u8"
                    
                    # İkinci aşama: Gerçek HD yolu ayıkla
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

        output = {"list": {"service": "iptv", "title": "iptv", "item": items}}
        
        with open('matches.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        print(f"✅ Başarılı: {len(items)} maç güncellendi.")
            
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
