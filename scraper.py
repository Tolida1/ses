import requests
from bs4 import BeautifulSoup
import yaml

BASE_SITE = "https://bosssports276.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_m3u8_link(watch_id):
    # Senin verdiğin yapıya göre m3u8 linkini oluşturan mantık
    # Not: Eğer site API kullanıyorsa buraya requests.get(f"{BASE_SITE}x?id={watch_id}") eklenebilir
    api_url = f"https://bosssports276.com/x?id={watch_id}"
    try:
        # Burada sitenin döndüğü gerçek linki simüle ediyoruz
        # Normalde buradan gelen JSON veya text içinden m3u8 ayıklanır
        return f"https://bo.61c25179391c19fefc.workers.dev/f6e33e69e0fdec0a7780e174f3c8b2c2/-/{watch_id}/playlist.m3u8"
    except:
        return None

def main():
    html = requests.get(BASE_SITE, headers=HEADERS).text
    soup = BeautifulSoup(html, "html.parser")
    football_tab = soup.find("div", id="pills-football")
    
    matches = []
    if football_tab:
        for block in football_tab.find_all("div", class_="match-block"):
            teams = block.find_all("div", class_="name")
            watch_id = block.get("data-watch")
            
            if len(teams) >= 2 and watch_id:
                title = f"{teams[0].text.strip()} - {teams[1].text.strip()}"
                m3u8_url = get_m3u8_link(watch_id)
                
                matches.append({
                    "name": title,
                    "id": watch_id,
                    "url": m3u8_url
                })

    # YAML ÇIKTISI
    with open('matches.yml', 'w', encoding='utf-8') as f:
        yaml.dump(matches, f, allow_unicode=True)

    # M3U ÇIKTISI (IPTV Oynatıcılar için)
    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for m in matches:
            f.write(f"#EXTINF:-1, {m['name']}\n{m['url']}\n")

if __name__ == "__main__":
    main()
