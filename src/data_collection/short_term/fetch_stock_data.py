import yfinance as yf
import pandas as pd
import os
import datetime
from fetch_tickers import get_top_50_sp500_tickers

def fetch_stock_data(tickers, period="5d"):  # ✅ 최근 5일간 데이터 가져오기
    stock_data = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)  # ✅ 변경: 1일 → 5일

            if not hist.empty:
                for date, row in hist.iterrows():
                    stock_data.append({
                        "Ticker": ticker,
                        "Date": date.date(),
                        "Open": row["Open"],
                        "High": row["High"],
                        "Low": row["Low"],
                        "Close": row["Close"],
                        "Volume": row["Volume"]
                    })
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    
    return pd.DataFrame(stock_data)

if __name__ == "__main__":
    tickers = get_top_50_sp500_tickers()
    stock_df = fetch_stock_data(tickers, period="5d")  # ✅ 최근 5일 데이터 가져옴

    save_dir = "data/short_term"
    os.makedirs(save_dir, exist_ok=True)

    today = datetime.datetime.today().strftime('%Y%m%d')
    save_path = os.path.join(save_dir, f"sp500_top50_{today}.csv")

    stock_df.to_csv(save_path, index=False)
    print(f"Data saved to {save_path}")