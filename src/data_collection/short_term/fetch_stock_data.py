from google.cloud import storage
import yfinance as yf
import pandas as pd
import os
import datetime
from fetch_tickers import get_top_50_sp500_tickers
from io import StringIO

# GCS 업로드 함수
def upload_to_gcs(bucket_name, destination_blob_name, dataframe):
    """Uploads a Pandas DataFrame to Google Cloud Storage directly from memory."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # DataFrame을 CSV 포맷으로 메모리에 저장한 후 업로드
    csv_buffer = StringIO()
    dataframe.to_csv(csv_buffer, index=False)
    blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")

    print(f"Data successfully uploaded to gs://{bucket_name}/{destination_blob_name}")

def fetch_stock_data(tickers, period="5d"):
    stock_data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

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
            print(f"⚠ Error fetching data for {ticker}: {e}")
    
    return pd.DataFrame(stock_data)

if __name__ == "__main__":
    tickers = get_top_50_sp500_tickers()
    stock_df = fetch_stock_data(tickers, period="5d")

    # 로컬 저장
    save_dir = "data/short_term/collected"
    os.makedirs(save_dir, exist_ok=True)

    today = datetime.datetime.today().strftime('%Y%m%d')
    save_path = os.path.join(save_dir, f"sp500_top50_{today}.csv")

    stock_df.to_csv(save_path, index=False)
    print(f"Data saved to {save_path}")

    # GCS 저장 경로 설정
    BUCKET_NAME = os.getenv("BUCKET_NAME", "your-bucket-name")  # 환경 변수에서 가져오기
    GCS_PATH = f"collected/sp500_top50_{today}.csv"  # GCS 내 저장 경로

    # GCS로 업로드
    upload_to_gcs(BUCKET_NAME, GCS_PATH, stock_df)