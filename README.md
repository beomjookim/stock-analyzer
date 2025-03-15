# 📊 S&P 500 Stock year-long analyzer


 
 ## 💎 프로젝트 개요

 
 저는 재테크에 관심이 많습니다.  
 저의 주식 장기투자를 도와주는 여러 지표를 직접 모아서 계산하고, 자동화, 시각화하고자 진행한 프로젝트입니다.
 
 이 프로젝트는 **S&P 500 상위 50개 종목**의 지난 1년 간의 주가 데이터를 여러 경로를 통해 **추출**해서,  
 1차 저장소에 **저장**하고, 가공을 통해 투자 판단에 필요한 정보들로 **변환**하여,  
 결과적으로 3개의 **Data Mart**를 포함한 **Data Warehouse**를 구축하고,  
 이를 Looker Studio로 **시각화**하는 **Batch성 ELT 파이프라인**을 다룹니다.

 스키마가 있는 데이터 웨어하우스이지만 최적화 과정에서 자연스레 **메달리온 모델**을 채택하게 되었습니다.
 
 - **데이터 원천**: Yahoo Finance (yFinance API), 웹 크롤링
 - **ETL 기술 스택** Python, Apache Spark, Google Cloud Storage (GCS)
 - **DWH & Data Mart**: Google BigQuery
 - **데이터 시각화**: Looker Studio
 - **개발 환경**: Docker, Visual Studio Code, Linux
 
 - **자동화 오케스트레이션**: Apache Airflow


### 최적화 적용 이후
<img src = "https://github.com/user-attachments/assets/57736086-2b86-405c-999e-c70a7704c633" height="500">

<details>
<summary>초기 버전(최적화 이전)</summary>

### 초기 버전(최적화 이전)
<img src = "https://github.com/user-attachments/assets/eda4b559-d291-493a-b365-0406031fa389" height="480">
</details>

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
 │ │ │ ├── augment_data.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 데이터 정제 및 변환 & BigQuery에 parquet 파일 적재<br>
 │ ├── 📂 bigquery/<br>
 │ │ ├── data_mart_creation.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 데이터 마트 구현 및 Partitioning & Clustering 최적화<br>
 │ │ ├── fact_stock_prices.sql&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # 데이터 마트 1<br>
 │ │ ├── fact_fundamental_metrics.sql &nbsp;&nbsp;&nbsp;# 데이터 마트 2<br>
 │ │ ├── fact_technical_indicators.sql&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # 데이터 마트 3<br>
 │ ├── 📂 GCS/<br>
 │ │ ├── 📂 short-term/collected<br>
 │ │ │ ├── 📂 sp500_raw_data.csv<br>
 │ │ ├── 📂 temp-load<br>
 │ ├── 📂 visualization/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# (4) 데이터 시각화<br>
 │ │ ├── looker_dashboard.json&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Looker Studio 대시보드 설정<br>
 │ └── README.md&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # 프로젝트 설명<br>
 
 ---

 
 ## 💎 2. 데이터 파이프라인 흐름

 
 ### **🔍 (1) 데이터 수집 (Extract)** -> Bronze Layer
 
 1️⃣ **오늘자 S&P 500 상위 50개 종목 리스트업** (`fetch_tickers.py`)  
 2️⃣ **Yahoo Finance에서 주가 데이터 수집** (`fetch_stock_data.py`)  
 3️⃣ **GCS (Google Cloud Storage) 에 원본 데이터 csv 형태로 저장** - **Bronze layer**  
 
 ---
 
 ### **🔍 (2) 데이터 변환 (Transform)** -> Silver Layer
 
 🔥 **Apache Spark를 활용하여 데이터 정제 및 변환**  
 1️⃣ 결측치 및 이상치 처리 (`augment_data.py`)  
 2️⃣ 이동평균(Moving Average), RSI(상대강도지수), 변동성(Volatility) 등 계산  
 3️⃣ parquet 형태로 변환 후 BigQuery에 적재
 
 ---
 
 ### **🔍 (3) 데이터 웨어하우스 (DWH) 구축** -> Gold Layer
 
 🔥 **BigQuery를 활용하여 Data Mart 설계 및 적재**  
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

## 💎 적용한 최적화 작업 리스트


### 1️⃣ 데이터 로드 최적화 (Data Ingestion Optimization)  
#### ✅ 병렬 API 호출 (ThreadPoolExecutor)  
YFinance API를 활용하여 데이터를 가져오는 과정에서, 멀티스레딩을 사용하여 병렬로 데이터를 수집하도록 최적화.   
ThreadPoolExecutor(max_workers=10)을 사용하여 최대 10개의 요청을 동시에 수행.      
👉 결과: 네트워크 대기 시간을 줄여 **데이터 수집 속도 54.7584s -> 14.4796s 으로 73.5% 단축**.  

### 2️⃣ 데이터 변환 최적화 (Data Transformation Optimization)  
#### ✅ Spark에서 컬럼 타입 변환 시 Null 값 보정  
원본 데이터의 NULL 값을 처리하지 않으면 Spark와 BigQuery에서 Type Mismatch 에러 발생 가능.  
조건절 구문을 사용하여 NULL 값을 적절한 기본값으로 변환.  
👉 결과: **데이터 정합성 유지 + BigQuery 적재 오류 감소**  

#### ✅ Spark Window Function 활용  
이평선, RSI 등 여러 기술적 지표 계산 시, Spark Window Function을 사용하여 성능을 최적화.  
👉 결과: **GroupBy보다 2배 이상 빠른 연산 수행**, 데이터 가공 속도 개선.  

#### ✅ 불필요한 컬럼 제거  
stock.info에서 가져온 재무 지표 중 사용하지 않는 컬럼을 제거하여 메모리 사용량 절감.  
👉 결과: 메모리 사용량 20% 감소, Spark 성능 향상.  

### 3️⃣ 데이터 적재 최적화 (Data Load Optimization)  
#### ✅ Parquet 대신 CSV 사용  
GCS에 데이터를 저장할 때, 원본 데이터는 CSV 형식으로 유지하여 호환성을 높이고 가독성을 유지.  
하지만, BigQuery 적재 시에는 Parquet을 활용하는 것이 더 적절할 수 있음.  

#### ✅ BigQuery 성능 최적화 - Partitioning & Clustering 적용  
데이터 적재 후, BigQuery 테이블을 파티셔닝 및 클러스터링하여 조회 속도를 최적화함.  
Partitioning	DATE(TIMESTAMP(Date)) 로 날짜별 파티셔닝 적용.  
Clustering	Ticker 기준으로 클러스터링 적용	특정 주식 검색 시 I/O 비용 절감.  
Column Pruning	SELECT 문에서 필요한 컬럼만 조회	쿼리 실행 속도 향상.  
👉 결과: **Looker에서의 데이터 조회 성능 기존 5.8342s -> 2.3546s로 59.64% 단축**.  

### 4️⃣ 메달리온 아키텍처 적용 (Bronze → Silver → Gold 계층화)  
데이터 처리 파이프라인을 Bronze → Silver → Gold 로 계층 분리.  
모듈화된 코드 구조로 유지보수성과 확장성을 강화.  
Silver 단계에서 데이터 정제 및 파생 변수 생성, Gold 단계에서 최적화된 분석 데이터 제공.  
 
 ---
 
 ## 📣 파이프라인 업그레이드 계획

 
 ### 📝 **Apache Airflow로 Batch 업무 자동화**  
 
 ### 📝 **Github action으로 CI/CD 자동화**
 

