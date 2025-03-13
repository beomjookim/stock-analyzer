# 📊 S&P 500 Stock Data Pipeline

## 📌 프로젝트 개요

저는 재테크에 관심이 많습니다.  
저의 장기투자를 도와주는 여러 지표를 직접 모아서 계산하고, 자동화, 시각화하고자자 진행한 프로젝트입니다.

이 프로젝트는 **S&P 500 상위 50개 종목**의 지난 1년 간의 주가 데이터를 여러 경로를 통해 **추출**해서,  
1차 저장소에 **저장**하고, 가공을 통해 투자 판단에 필요한 정보들로 **변환**하여,  
결과적으로 3개의 **Data Mart**를 포함한 **Data Warehouse**를 구축하고,  
이를 Looker Studio로 **시각화**하는 **Batch성 ETL 파이프라인**을 다룹니다.

- **데이터 원천**: Yahoo Finance (yFinance API), 웹 크롤링
- **ETL 기술 스택** Python, Apache Spark, Google Cloud Storage (GCS)
- **DWH & Data Mart**: Google BigQuery
- **데이터 시각화**: Looker Studio
- **개발 환경**: Docker, Visual Studio Code, Linux

<여기에 draw.io ㄱㄱㄱ>

---

## 🚀 1. 프로젝트 구조

📂 stock-analyzer<br>
├── docker-compose.yml&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # docker 전반 환경 설정<br>
├── Dockerfile.spark&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # spark 관련 도커 환경 구축<br>
├── Dockerfile.bigquery &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# bigquery 관련 도커 환경 구축<br>
├── 📂 src/<br>
│ ├── 📂 data_fetching/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# (1) 데이터 수집 (Extract)<br>
│ │ ├── short_term/<br>
│ │ │ ├── fetch_tickers.py&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # S&P 500 상위 50개 종목 선정 - 웹 크롤링<br>
│ │ │ ├── fetch_stock_data.py&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # yFinance에서 지난 1년치 주가 데이터 추출 및 GCS에 raw 데이터 적재<br>
│ ├── 📂 data_processing/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # (2) 데이터 가공 (Transform) & (3) 데이터 적재 (Load)<br>
│ │ ├── short_term/<br>
│ │ │ ├── spark_transformation.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 데이터 변환 & 데이터 마트 생성 & BigQuery에 적재<br>
│ ├── 📂 bigquery/<br>
│ │ ├── bigquery_optimization.sql &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Partitioning & Clustering 최적화, maybe!<br>
│ │ ├── fact_stock_prices.sql&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # 데이터 마트 1<br>
│ │ ├── fact_fundamental_metrics.sql &nbsp;&nbsp;# 데이터 마트 2<br>
│ │ ├── fact_technical_indicators.sql&nbsp;&nbsp;&nbsp;&nbsp; # 데이터 마트 3<br>
│ ├── 📂 GCS/<br>
│ | ├── 📂 short-term<br>
│ | | ├── 📂 collected<br>
│ | | | ├── sp500_raw_data.csv<br>
│ | | ├── 📂 temp-load<br>
│ ├── 📂 visualization/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# (4) 데이터 시각화<br>
│ │ ├── looker_dashboard.json&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Looker Studio 대시보드 설정<br>
│ │ └── README.md&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 시각화 구성 설명<br>
│ └── README.md&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # 프로젝트 설명<br>

---

## 🔄 2. 데이터 파이프라인 흐름

### **📌 (1) 데이터 수집 (Extract)**

1️⃣ **S&P 500 상위 50개 종목 가져오기** (`fetch_tickers.py`)
2️⃣ **Yahoo Finance에서 주가 데이터 수집** (`fetch_stock_data.py`)
3️⃣ **GCS (Google Cloud Storage) 에 원본 데이터 저장**

✅ **결과:** GCS에 `sp500_top50_YYYYMMDD.csv` 파일이 저장됨

---

### **📌 (2) 데이터 변환 (Transform)**

🔥 **Apache Spark를 활용하여 데이터 정제 및 변환**  
1️⃣ 결측치 및 이상치 처리 (`spark_transformation.py`)
2️⃣ 이동평균(Moving Average), RSI(상대강도지수), 변동성(Volatility) 등 계산  
3️⃣ 변환된 데이터를 다시 GCS에 저장

✅ **결과:**

- GCS에 `transformed/sp500_top50_cleaned.parquet` 저장
- **BigQuery 테이블로 적재할 준비 완료!**

---

### **📌 (3) 데이터 웨어하우스 (DWH) 구축**

🔥 **BigQuery를 활용하여 Data Warehouse 설계 및 적재**  
1️⃣ `fact_stock_prices.sql` → **주가 데이터 테이블**
2️⃣ `fact_fundamental_metrics.sql` → **기업 재무 지표 테이블**
3️⃣ `fact_technical_indicators.sql` → **기술적 분석 지표 테이블**
4️⃣ **Partitioning & Clustering 적용** (`bigquery_optimization.sql`)

✅ **결과:**

- **DWH 구축 완료:** `fact_stock_prices`, `fact_fundamental_metrics`, `fact_technical_indicators` 테이블 생성
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

✅ **결과:** **Looker Studio 대시보드에서 실시간 데이터 분석 가능!**

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
