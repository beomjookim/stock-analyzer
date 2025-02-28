import yfinance as yf
import pandas as pd
import os
import datetime
from fetch_tickers import get_top_50_sp500_tickers

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
    tickers = get_top_50_sp500_tickers()
    stock_df = fetch_stock_data(tickers)

    save_dir = "data/short_term"
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"sp500_top50_{datetime.datetime.today().strftime('%Y%m%d')}.csv")
    stock_df.to_csv(save_path, index=False)
    print(f"Raw data saved to {save_path}")