from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage
import yfinance as yf
import pandas as pd
import os
import datetime
from fetch_tickers import get_top_50_sp500_tickers
from io import StringIO
import time

# GCS 업로드 함수
def upload_to_gcs(bucket_name, destination_blob_name, dataframe):
    """Uploads a Pandas DataFrame to Google Cloud Storage directly from memory."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # 🔹 컬럼 순서 강제 정렬
    expected_columns = [
        "Ticker", "Date", "Open", "High", "Low", "Close", "Volume",
        "Market_Cap", "PE_Ratio", "PB_Ratio", "Dividend_Yield", "EPS",
        "52_Week_High", "52_Week_Low"
    ]
    dataframe = dataframe[expected_columns]

    # 🔹 Date 컬럼을 YYYY-MM-DD 포맷으로 변환
    dataframe["Date"] = pd.to_datetime(dataframe["Date"]).dt.strftime('%Y-%m-%d')


    # DataFrame을 CSV 포맷으로 메모리에 저장한 후 업로드
    csv_buffer = StringIO()
    dataframe.to_csv(csv_buffer, index=False)
    blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")

    print(f"✅ Data successfully uploaded to gs://{bucket_name}/{destination_blob_name}")

def fetch_single_stock(ticker, period="1y"):
    """Fetch stock data for a single ticker."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return None

        # 원본 데이터 저장 (불필요한 컬럼 제거)
        hist = hist[["Open", "High", "Low", "Close", "Volume"]]
        hist["Ticker"] = ticker
        hist.reset_index(inplace=True)

        # 원본 데이터에 유지해야 하는 재무 정보 추가
        info = stock.info
        hist["Market_Cap"] = info.get("marketCap", None)
        hist["PE_Ratio"] = info.get("trailingPE", None)
        hist["PB_Ratio"] = info.get("priceToBook", None)
        hist["Dividend_Yield"] = info.get("trailingAnnualDividendYield", None)
        hist["EPS"] = info.get("trailingEps", None)
        hist["52_Week_High"] = info.get("fiftyTwoWeekHigh", None)
        hist["52_Week_Low"] = info.get("fiftyTwoWeekLow", None)

        return hist

    except Exception as e:
        print(f"⚠ Error fetching data for {ticker}: {e}")
        return None

def fetch_stock_data(tickers, period="1y"):
    """Fetch stock data for multiple tickers using multi-threading."""
    stock_data = []

    # 🔹 ThreadPoolExecutor를 사용한 병렬 API 호출 (최대 10개 동시 실행)
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda t: fetch_single_stock(t, period), tickers))

    # None 값 제외 후 병합
    stock_data = [r for r in results if r is not None]

    if stock_data:
        df = pd.concat(stock_data, ignore_index=True)

        # 🔹 날짜 기준 정렬 (최신 데이터부터 순서대로)
        df.sort_values(by=["Ticker", "Date"], ascending=[True, True], inplace=True)

        return df

    return pd.DataFrame()  # 빈 데이터프레임 반환

if __name__ == "__main__":

    # start_time = time.time()  # 시작 시간 기록

    tickers = get_top_50_sp500_tickers()
    stock_df = fetch_stock_data(tickers, period="1y")
    today = datetime.datetime.today().strftime('%Y%m%d')

    if not stock_df.empty:
        # GCS 저장 경로 설정
        BUCKET_NAME = os.getenv("BUCKET_NAME")  # 환경 변수에서 가져오기
        GCS_PATH = f"collected/sp500_top50_{today}.csv"  # GCS 내 저장 경로

        # 원본 데이터만 GCS에 저장
        upload_to_gcs(BUCKET_NAME, GCS_PATH, stock_df)
    else:
        print("⚠ No data fetched. Check API availability.")

    # end_time = time.time()  # 종료 시간 기록
    # execution_time = end_time - start_time  # 실행 시간 계산
    # print(f"⏱ Execution Time: {execution_time:.4f} seconds")