import yfinance as yf
import os

# 저장할 폴더
SAVE_PATH = "data/raw/"
os.makedirs(SAVE_PATH, exist_ok=True)

# 수집할 주식 리스트
STOCKS = ["AAPL", "GOOGL", "AMZN", "MSFT"]

def fetch_stock_data(symbol):
    stock = yf.Ticker(symbol)
    df = stock.history(period="5y")  # 과거 5년치 데이터 가져오기
    df.to_csv(f"{SAVE_PATH}{symbol}.csv")
    print(f"✅ {symbol} 데이터 저장 완료!")

if __name__ == "__main__":
    for stock in STOCKS: fetch_stock_data(stock)
    print("✅ 모든 데이터 저장 완료!")