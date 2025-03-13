# 📊 S&P 500 Stock Data Pipeline

## 📌 프로젝트 개요

저는 재테크에 관심이 많습니다.  
한동안 단기투자에 빠져서 단기이익을 좇다가 크게 데이고,  
장기투자에 눈을 뜨고 나서 저의 장기투자를 도와주는 여러 지표를 직접 만들고자 진행한 프로젝트입니다.  

이 프로젝트는 **S&P 500 상위 50개 종목**의 지난 1년 간의 주가 데이터를 여러 경로를 통해 **추출**해서,  
1차 저장소에 **저장**하고, 가공을 통해 투자 판단에 필요한 정보들로 **변환**하여,  
결과적으로 3개의 **Data Mart**를 포함한 **Data Warehouse**를 구축하고,  
이를 Looker Studio로 **시각화**하는 **Batch성 ETL 파이프라인**을 다룹니다.  

---

## 🚀 1. 프로젝트 구조

📂 stock-analyzer 
├── docker-compose.yml                                   # Spark 실행 환경 설정 
├── 📂 src/ 
│ ├── 📂 data_fetching/                                  # (1) 데이터 수집 (Extract) 
│ │ ├── short_term/ 
│ │ │ ├── fetch_tickers.py                               # S&P 500 상위 50개 종목 선정 - 웹 크롤링
│ │ │ ├── fetch_stock_data.py                            # yFinance에서 주가 데이터 가져와서 GCS에 raw 데이터 업로드
│ ├── 📂 data_processing/                                # (2) 데이터 변환 (Transform) 
│ │ ├── short_term/ 
│ │ │ ├── spark_transformation.py                        # GCS에서 데이터 가져와서 가공 후 BigQuery에 적재
│ ├── 📂 bigquery/                                       # (3) 데이터 마트 생성 (Transform) 
│ │ ├── bigquery_load.py # BigQuery에 데이터 적재 
│ │ ├── bigquery_optimization.sql # Partitioning & Clustering 최적화 
│ │ ├── queries/ # 분석용 SQL 쿼리 저장 
│ │ ├── fact_stock_prices.sql # 테이블 생성 쿼리 
│ │ ├── fact_fundamental_metrics.sql 
│ │ ├── fact_technical_indicators.sql 
│ │ └── README.md # DWH 구성 및 최적화 설명 
│ │ │ ├── 📂 visualization/ # (4) 데이터 시각화 
│ │ ├── looker_dashboard.json # Looker Studio 대시보드 설정 
│ │ ├── looker_queries.sql # 시각화용 SQL 쿼리 
│ │ └── README.md # 시각화 구성 설명 
│ ├── optimization_guide.md # 성능 최적화 가이드 
│ └── README.md # 프로젝트 설명

000000000000000000000000000000000000000


---

## 🔄 2. 데이터 파이프라인 ETL 흐름

### **📌 (1) 데이터 수집 (Extract)**
1️⃣ **S&P 500 상위 50개 종목 선정** - 웹 크롤링을 통해 오늘자 S&P 500의 주가 상위 50개 종목 선정 (`fetch_tickers.py`)  
2️⃣ **주가 데이터 수집** - YAHOO FINANCE 라이브러리 및 API 통해 해당 주식들의 지난 1년치 정보들 수집 (yFinance API, `fetch_stock_data.py`)  
3️⃣ **GCS (Google Cloud Storage) 에 원본 데이터 저장** (`fetch_stock_data.py`)  

✅ **결과:** GCS에 `sp500_top50_YYYYMMDD.csv` 원본 파일 저장  

---

### **📌 (2) 데이터 변환 (Transform)**
🔥 **Apache Spark를 활용하여 데이터 정제 및 변환**  
1️⃣ 결측치 및 이상치 처리 (`cleaning_functions.py`)  
2️⃣ 이동평균(Moving Average), RSI(상대강도지수), 변동성(Volatility) 등 계산  
3️⃣ 변환된 데이터를 다시 GCS에 저장  

✅ **결과:**  
- GCS에 `transformed/sp500_top50_cleaned.parquet` 저장  
- `Spark DataFrame`에서 `BigQuery`로 적재 준비 완료  

---

### **📌 (3) 데이터 웨어하우스 (DWH) 구축**
🔥 **BigQuery를 활용하여 Data Warehouse 설계 및 적재**  
1️⃣ `fact_stock_prices.sql` → **주가 데이터 테이블 생성**  
2️⃣ `fact_fundamental_metrics.sql` → **기업 재무 지표 테이블 생성**  
3️⃣ `fact_technical_indicators.sql` → **기술적 분석 지표 테이블 생성**  
4️⃣ **Partitioning & Clustering 적용** (`bigquery_optimization.sql`)  

✅ **결과:**  
- **DWH 구축 완료:** `short_term.fact_stock_prices` 등 3개 테이블 생성  
- **BigQuery 최적화 적용:** 날짜 기준 Partitioning + 종목(Ticker) 기준 Clustering  

---

### **📌 (4) 데이터 시각화 (Looker Studio)**
🔥 **Looker Studio에서 대시보드 구축**  
1️⃣ 주가 변동 추이 (`Close` 가격 & 이동평균)  
2️⃣ RSI 변동 vs 종가 비교  
3️⃣ 거래량 Bar Chart (Top 10)  
4️⃣ 변동성 Bar Chart (Top 10)  
5️⃣ 특정 주식의 30일/1년 주가 변동 추이 (S&P 500 평균과 비교)  
6️⃣ 트리맵 (시가총액 기준)  

✅ **결과:** **Looker Studio 대시보드에서 분석 가능!**  

---

## 🚀 3. 성능 최적화 (향후 개선 방향)
✅ **Apache Spark 최적화**
- `cache()` & `repartition()` 최적화
- `broadcast join` 활용하여 조인 속도 개선

✅ **BigQuery 최적화**
- `Partitioning & Clustering` 적용
- 불필요한 `SELECT *` 제거

✅ **GCS 저장 최적화**
- CSV 대신 **Parquet + Snappy 압축** 적용  
- 작은 파일 병합하여 **Spark 처리 속도 향상**

---

## 🎯 4. 최종 목표
✅ **실제 배포 가능한 데이터 파이프라인 구축**  
✅ **BigQuery 기반의 빠른 데이터 분석 환경 제공**  
✅ **Looker Studio에서 실시간 시각화 가능**  

📢 **이 프로젝트를 통해 신입 데이터 엔지니어로서 실무형 ETL & DWH 구축 역량을 입증할 수 있습니다!** 🚀  
