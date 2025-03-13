# 📊 S&P 500 Stock year-long analyzer

## 📌 프로젝트 개요

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

<여기에 draw.io ㄱㄱㄱ>

---

## 🚀 1. 프로젝트 구조

📂 stock-analyzer<br>
├── docker-compose.yml&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # docker 전반 환경 설정<br>
├── Dockerfile.spark&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nb들

✅ **Apache Spark 최적화**

- `cache()` & `repartition()` 최적화  
- `broadcast join` 활용하여 조인 속도 개선  

✅ **BigQuery 최적화**

- `Partitioning & Clustering` 적용  
- 불필요한 `SELECT *` 제거  

✅ **GCS 저장 최적화**

- CSV 대신 **Parquet + Snappy 압축** 적용  
- 작은 파일 병합하여 **Spark 처리 속도 향상**  

✅ **Apache Airflow로 Batch 업무 자동화**

✅ **Github action으로 CI/CD 자동화**

---

## 🚀 DEMO

<링크>
