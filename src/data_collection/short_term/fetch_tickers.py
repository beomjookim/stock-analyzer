import requests
from bs4 import BeautifulSoup

def get_top_50_sp500_tickers():
    url = "https://stockanalysis.com/list/sp-500-stocks/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Unable to fetch data (Status Code: {response.status_code})")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    table = soup.find("table")
    if not table:
        print("Error: Could not find the stock table on the page.")
        return []
    
    rows = table.find_all("tr")[1:]  # 첫 번째 행은 헤더이므로 제외
    
    tickers = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) > 1:
            ticker = cols[1].text.strip()  # 두 번째 열이 티커 정보
            tickers.append(ticker)
            if len(tickers) == 50:
                break  # 상위 50개까지만 가져오기
    
    return tickers

if __name__ == "__main__":
    tickers = get_top_50_sp500_tickers()
    print(tickers)