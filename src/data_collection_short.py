import yfinance as yf
import pandas as pd
import os

# 저장할 폴더 생성
SAVE_PATH = "data/short_term/"
os.makedirs(SAVE_PATH, exist_ok=True)

# S&P 500 종목 리스트 불러오기 (Yahoo Finance 제공 티커 활용)
SP500_TICKERS = [ticker for ticker in yf.Ticker("^GSPC").]

# 시가총액 기준 정렬
def get_market_cap(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.info.get("marketCap", 0)  # 시가총액 가져오기
    except:
        return 0

# 모든 종목의 시가총액 가져오기
market_caps = [(ticker, get_market_cap(ticker)) for ticker in SP500_TICKERS]
market_caps_sorted = sorted(market_caps, key=lambda x: x[1], reverse=True)  # 내림차순 정렬

# 상위 50개 종목 선택
top_50_tickers = [x[0] for x in market_caps_sorted[:50]]

# 데이터프레임 생성 후 CSV 저장
df = pd.DataFrame(market_caps_sorted[:50], columns=["Ticker", "Market Cap"])
df.to_csv(f"{SAVE_PATH}short_term_top50.csv", index=False)

print(f"✅ 단기 분석용 Top 50 종목 저장 완료! ({SAVE_PATH}short_term_top50.csv)")
