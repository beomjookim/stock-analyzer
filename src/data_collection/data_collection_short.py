import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import os

def get_top_50_sp500_tickers():
    url = "https://stockanalysis.com/list/sp-500-stocks/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Unable to fetch data (Status Code: {response.status_code})")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 티커 심볼들이 들어있는 테이블 찾기
    table = soup.find("table")
    if not table:
        print("Error: Could not find the stock table on the page.")
        return []
    
    # 테이블 안의 행들을 가져옴
    rows = table.find_all("tr")[1:]  # 첫 번째 행은 헤더이므로 제외
    
    tickers = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) > 1:  # 최소 두 개의 열이 있는지 확인
            ticker = cols[1].text.strip()  # 두 번째 열이 티커 정보일 가능성 높음
            tickers.append(ticker)
            if len(tickers) == 50:
                break  # 상위 50개까지만 가져오기
    
    return tickers

def fetch_stock_data(tickers):
    stock_data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if not hist.empty:
                latest_data = hist.iloc[-1]
                stock_data.append({
                    "Ticker": ticker,
                    "Date": latest_data.name.date(),
                    "Open": latest_data["Open"],
                    "High": latest_data["High"],
                    "Low": latest_data["Low"],
                    "Close": latest_data["Close"],
                    "Volume": latest_data["Volume"]
                })
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")

    return pd.DataFrame(stock_data)

if __name__ == "__main__":
    top_50_tickers = get_top_50_sp500_tickers()
    stock_df = fetch_stock_data(top_50_tickers)
    print(stock_df)

    # 저장할 폴더 경로 설정
    save_dir = "data/short_term"
    os.makedirs(save_dir, exist_ok=True)

    # 파일 저장
    save_path = os.path.join(save_dir, "sp500_top50_latest.csv")
    stock_df.to_csv(save_path, index=False)
    print(f"Data saved to {save_path}")
