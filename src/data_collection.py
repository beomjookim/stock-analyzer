import os
import requests
import pandas as pd
from dotenv import load_dotenv

# 📌 환경 변수 로드
load_dotenv()
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# 📌 Alpha Vantage API URL
BASE_URL = "https://www.alphavantage.co/query"

# 📌 저장할 폴더
SAVE_PATH = "data/raw/"
os.makedirs(SAVE_PATH, exist_ok=True)

# 📌 수집할 주식 리스트 - 개발용용
STOCKS = ["AAPL", "GOOGL", "AMZN", "MSFT"]

def fetch_stock_data(symbol):
    # Alpha Vantage에서 주식 데이터 가져오기
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "apikey": API_KEY,
        "outputsize": "full",
        "datatype": "json",
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "Time Series (Daily)" in data:
        df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
        df.columns = ["open", "high", "low", "close", "adjusted_close", "volume", "dividend_amount", "split_coefficient"]
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        df.to_csv(f"{SAVE_PATH}{symbol}.csv")
        print(f"✅ {symbol} 데이터 저장 완료!")
    else:
        print(f"❌ {symbol} 데이터 가져오기 실패: {data}")

if __name__ == "__main__":
    for stock in STOCKS:
        fetch_stock_data(stock)
    print("✅ 모든 데이터 저장 완료!")