from google.cloud import bigquery

# BigQuery 설정
BQ_DATASET = "short_term"
BQ_TABLE_SILVER = "fact_stock_prices_silver"

BQ_TABLE_STOCK_PRICES = "fact_stock_prices"
BQ_TABLE_TECHNICAL = "fact_technical_indicators"
BQ_TABLE_FUNDAMENTAL = "fact_fundamental_metrics"

# BigQuery 클라이언트 생성
client = bigquery.Client()

# Gold 데이터 마트 (Stock Prices) - 파티셔닝 & 클러스터링 적용
query_stock_prices = f"""
CREATE OR REPLACE TABLE `{BQ_DATASET}.{BQ_TABLE_STOCK_PRICES}`
PARTITION BY Date  -- 변환된 컬럼 사용
CLUSTER BY Ticker
AS
SELECT
    Ticker, DATE(TIMESTAMP(Date)) AS Date,  -- `Date` 컬럼을 변환해서 새로 만듦
    Open, High, Low, Close, Volume
FROM `{BQ_DATASET}.{BQ_TABLE_SILVER}`;
"""

# Gold 데이터 마트 (Technical Indicators) - 파티셔닝 & 클러스터링 적용
query_technical = f"""
CREATE OR REPLACE TABLE `{BQ_DATASET}.{BQ_TABLE_TECHNICAL}`
PARTITION BY Date
CLUSTER BY Ticker
AS
SELECT
    Ticker, DATE(TIMESTAMP(Date)) AS Date,
    Moving_Avg_5, Moving_Avg_20, Moving_Avg_50,
    Volatility_30d, RSI_14
FROM `{BQ_DATASET}.{BQ_TABLE_SILVER}`;
"""

# Gold 데이터 마트 (Fundamental Metrics) - 클러스터링 적용 (파티셔닝은 의미 없음)
query_fundamental = f"""
CREATE OR REPLACE TABLE `{BQ_DATASET}.{BQ_TABLE_FUNDAMENTAL}`
CLUSTER BY Ticker
AS
SELECT
    Ticker, Market_Cap, PE_Ratio, PB_Ratio, Dividend_Yield, EPS,
    `52_Week_High`, `52_Week_Low`
FROM `{BQ_DATASET}.{BQ_TABLE_SILVER}`;
"""

# SQL 실행
client.query(query_stock_prices).result()
print("Stock Prices Data Mart Created Successfully!")

client.query(query_technical).result()
print("Technical Indicators Data Mart Created Successfully!")

client.query(query_fundamental).result()
print("Fundamental Metrics Data Mart Created Successfully!")

print("All Gold Data Marts successfully created with Partitioning & Clustering!")
