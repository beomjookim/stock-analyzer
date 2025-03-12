from google.cloud import bigquery
import time

# BigQuery 클라이언트 생성
client = bigquery.Client()

# 프로젝트 ID & 데이터셋 이름
PROJECT_ID = "fluid-mix-452511-j3"
DATASET_ID = "short_term"
SOURCE_TABLE = f"{PROJECT_ID}.{DATASET_ID}.sp500_top50"
CONVERTED_TABLE = f"{PROJECT_ID}.{DATASET_ID}.sp500_top50_converted"
TARGET_TABLE = f"{PROJECT_ID}.{DATASET_ID}.sp500_top50_partitioned_clustered"

### 1. 데이터 타입 변환 (Date & Float 변환) ###
convert_query = f"""
CREATE OR REPLACE TABLE `{CONVERTED_TABLE}` AS
SELECT 
    Ticker,
    DATE(PARSE_DATE('%Y-%m-%d', Date)) AS Date,  -- String → Date 변환
    CAST(Open AS FLOAT64) AS Open,
    CAST(High AS FLOAT64) AS High,
    CAST(Low AS FLOAT64) AS Low,
    CAST(Close AS FLOAT64) AS Close,
    CAST(Volume AS FLOAT64) AS Volume,  -- INT64 대신 FLOAT64 사용
    Moving_Avg,
    Daily_Change,
    Volatility
FROM `{SOURCE_TABLE}`;
"""

# 변환 실행
print("데이터 타입 변환 중...")
query_job = client.query(convert_query)
query_job.result()  # 실행 완료 대기
print(f"변환된 테이블 `{CONVERTED_TABLE}` 생성 완료!")

### 2. 최적화 테이블 생성 (Partitioning & Clustering) ###
optimization_query = f"""
CREATE OR REPLACE TABLE `{TARGET_TABLE}`
PARTITION BY Date  -- `Date` 컬럼을 기준으로 파티셔닝
CLUSTER BY Ticker AS
SELECT * FROM `{CONVERTED_TABLE}`;
"""

# 최적화 테이블 생성 실행
print("최적화 테이블 생성 중...")
query_job = client.query(optimization_query)
query_job.result()  # 실행 완료 대기
print(f"최적화된 테이블 `{TARGET_TABLE}` 생성 완료!")

# materialized view 관련 작업 필

### 4. 기존 테이블과 최적화된 테이블 성능 비교 ###
# test_query = f"""
# SELECT COUNT(*) FROM `{SOURCE_TABLE}`
# WHERE Date BETWEEN '2025-03-01' AND '2025-03-10';
# """

# test_query_optimized = f"""
# SELECT COUNT(*) FROM `{TARGET_TABLE}`
# WHERE Date BETWEEN '2025-03-01' AND '2025-03-10';
# """

# # 기존 테이블 쿼리 실행 (속도 측정)
# print("\n기존존 테이블 쿼리 실행 중...")
# start_time = time.time()
# query_job = client.query(test_query)
# rows = query_job.result()
# end_time = time.time()
# print(f"기존 테이블 조회 소요 시간: {end_time - start_time:.4f}초")

# # 최적화된 테이블 쿼리 실행 (속도 측정)
# print("\n최적화된 테이블 쿼리 실행 중...")
# start_time = time.time()
# query_job = client.query(test_query_optimized)
# rows = query_job.result()
# end_time = time.time()
# print(f"최적화된 테이블 조회 소요 시간: {end_time - start_time:.4f}초")

# print("\n최적화 성능 비교 완료!")
