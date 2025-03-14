# 📊 S&P 500 Stock year-long analyzer
 
 ## 💎 프로젝트 개요
 
 저는 재테크에 관심이 많습니다.  
 저의 주식 장기투자를 도와주는 여러 지표를 직접 모아서 계산하고, 자동화, 시각화하고자 진행한 프로젝트입니다.
 
 이 프로젝트는 **S&P 500 상위 50개 종목**의 지난 1년 간의 주가 데이터를 여러 경로를 통해 **추출**해서,  
 1차 저장소에 **저장**하고, 가공을 통해 투자 판단에 필요한 정보들로 **변환**하여,  
 결과적으로 3개의 **Data Mart**를 포함한 **Data Warehouse**를 구축하고,  
 이를 Looker Studio로 **시각화**하는 **Batch성 ETL 파이프라인**을 다룹니다.
 
 - **데이터 원천**: Yahoo Finance (yFinance API), 웹 크롤링
 - **ETL 기술 스택** Python, Apache Spark, Google Cloud Storage (GCS)
 - **DWH & Data Mart**: Google BigQuery
 - **데이터 시각화**: Looker Studio
 - **개발 환경**: Docker, Visual Studio Code, Linux
 
 - **자동화 오케스트레이션**: Apache Airflow
 
![diagram](https://github.com/user-attachments/assets/ca5862ba-db08-472d-8a0a-18750e5a269d)

 ---
 
 ## 💎 1. 프로젝트 구조
 
 📂 stock-analyzer<br>
 ├── docker-compose.yml&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # docker 전반 환경 설정<br>
 ├── Dockerfile.spark&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # spark 관련 도커 환경 구축<br>
 ├── Dockerfile.bigquery &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# bigquery 관련 도커 환경 구축<br>
 ├── 📂 src/<br>
 │ ├── 📂 data_fetching/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# (1) 데이터 수집 (Extract)<br>
 │ │ ├── short_term/<br>
 │ │ │ ├── fetch_tickers.py&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # S&P 500 상위 50개 종목 선정 - 웹 크롤링<br>
 │ │ │ ├── fetch_stock_data.py&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # yFinance에서 지난 1년치 주가 데이터 추출 및 GCS에 raw 데이터 적재<br>
 │ ├── 📂 data_processing/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # (2) 데이터 가공 (Transform) & (3) 데이터 적재 (Load)<br>
 │ │ ├── short_term/<br>
 │ │ │ ├── spark_transformation.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 데이터 변환 & 데이터 마트 생성 & BigQuery에 적재<br>
 │ ├── 📂 bigquery/<br>
 │ │ ├── bigquery_optimization.sql &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Partitioning & Clustering 최적화, maybe!<br>
 │ │ ├── fact_stock_prices.sql&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # 데이터 마트 1<br>
 │ │ ├── fact_fundamental_metrics.sql &nbsp;&nbsp;&nbsp;# 데이터 마트 2<br>
 │ │ ├── fact_technical_indicators.sql&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # 데이터 마트 3<br>
 │ ├── 📂 GCS/<br>
 │ │ ├── 📂 short-term/collected<br>
 │ │ │ ├── 📂 sp500_raw_data.csv<br>
 │ │ ├── 📂 temp-load<br>
 │ ├── 📂 visualization/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# (4) 데이터 시각화<br>
 │ │ ├── looker_dashboard.json&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Looker Studio 대시보드 설정<br>
 │ │ └── README.md&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 시각화 구성 설명<br>
 │ └── README.md&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # 프로젝트 설명<br>
 
 ---
 
 ## 💎 2. 데이터 파이프라인 흐름
 
 ### **🔍 (1) 데이터 수집 (Extract)**
 
 1️⃣ **S&P 500 상위 50개 종목 가져오기** (`fetch_tickers.py`)  
 2️⃣ **Yahoo Finance에서 주가 데이터 수집** (`fetch_stock_data.py`)  
 3️⃣ **GCS (Google Cloud Storage) 에 원본 데이터 저장**  
 
 
 ---
 
 ### **🔍 (2) 데이터 변환 (Transform)**
 
 🔥 **Apache Spark를 활용하여 데이터 정제 및 변환**  
 1️⃣ 결측치 및 이상치 처리 (`spark_transformation.py`)  
 2️⃣ 이동평균(Moving Average), RSI(상대강도지수), 변동성(Volatility) 등 계산  
 
 
 ---
 
 ### **🔍 (3) 데이터 웨어하우스 (DWH) 구축**
 
 🔥 **BigQuery를 활용하여 Data Warehouse(Data Mart) 설계 및 적재**  
 1️⃣ `fact_stock_prices.sql` → **주가 데이터 테이블**  
 2️⃣ `fact_fundamental_metrics.sql` → **기업 재무 지표 테이블**  
 3️⃣ `fact_technical_indicators.sql` → **기술적 분석 지표 테이블**  
 
 
 ---
 
 ### **🔍 (4) 데이터 시각화 (Looker Studio)**
 
 🔥 **Looker Studio에서 대시보드 구축**  
 1️⃣ 지난 1년 S&P 500 상위 50개 종목의 주가 추이 - 전체, 개별 종목 모두 지원  
 2️⃣ 지난 1년 가장 변동성 낮았던 top 5개 종목 추이 - 개별 종목 정보도 지원   
 3️⃣ PER vs. PBR 차트로 주가 상승여력 비교 - 개별 종목 비교 기능 지원  
 4️⃣ 시가총액 순으로 트리맵 형성 - 개별 종목들 비교 기능 지원  
 

  ---
 
 ## 💎 DEMO
 
https://lookerstudio.google.com/reporting/98c57f71-3abb-4be9-8472-c5b40505f3a9

![image](https://github.com/user-attachments/assets/7e701263-a9f3-4b89-aadb-85da7ebc5717)
 기본적으로는, 상위 50개 종목 전반을 다루는 차트가 디스플레이 됩니다.
 좌상단부터 시계방향으로, 주가 트렌드, PER vs. PBR 산점도, 시가총액 트리맵, 변동성 차트입니다.

 가운데의 드랍다운으로 특정 종목들을 지정하면, 해당 종목들만 필터링하여 위의 차트들이 업데이트됩니다.
 예를 들어, PLTR, TSLA, NVDA, AMAZN, AAPL의 5개 종목을 선정하면 아래와 같이 표현됩니다.
![image](https://github.com/user-attachments/assets/4dd0744e-58b3-49a7-b272-0001f830710a)

 
 ---
 
 ## 📣 추후 최적화 계획
 
 📝 **Apache Spark 최적화**
 
 - `cache()` & `repartition()` 최적화  
 - `broadcast join` 활용하여 조인 속도 개선  
 
 📝 **BigQuery 최적화**
 
 - `Partitioning & Clustering` 적용  
 - 불필요한 `SELECT *` 제거  
 
 📝 **GCS 저장 최적화**
 
 - CSV 대신 **Parquet + Snappy 압축** 적용  
 - 작은 파일 병합하여 **Spark 처리 속도 향상**  
 
 📝 **Apache Airflow로 Batch 업무 자동화**
 
 📝 **Github action으로 CI/CD 자동화**
 

