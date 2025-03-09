import os
import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, stddev
from pyspark.sql.window import Window

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("SP500_ShortTerm_Processing") \
    .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
    .config("spark.hadoop.fs.gs.auth.service.account.enable", "true") \
    .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "/opt/keys/gcs-key.json") \
    .getOrCreate()

# GCS 및 Local 경로 설정
GCS_BUCKET = "short-term"
today = datetime.datetime.today().strftime('%Y%m%d')

GCS_INPUT_PATH = f"gs://{GCS_BUCKET}/collected/sp500_top50_{today}.csv"   # 원본 CSV 위치 (GCS)
GCS_OUTPUT_PATH = f"gs://{GCS_BUCKET}/processed/sp500_top50_partitioned"  # 변환 후 저장 (GCS)
LOCAL_OUTPUT_PATH = f"data/short_term/processed/sp500_top50_partitioned"  # 변환 후 저장 (Local)

# GCS에서 CSV 데이터를 로드
df = spark.read.option("header", True).csv(GCS_INPUT_PATH)

# 데이터 변환 수행
window_spec = Window.partitionBy("Ticker").orderBy(col("Date").cast("timestamp")).rowsBetween(-4, 0)

df = df.withColumn("Moving_Avg", avg(col("Close")).over(window_spec))  # 이동 평균(5일 기준)
df = df.withColumn("Daily_Change", ((col("High") - col("Low")) / col("Open") * 100))  # 변동성 계산
df = df.withColumn("Volatility", stddev(col("Close")).over(window_spec))  # 표준편차(5일)

print(f"Short-term data successfully transformed and saved to:")

# 변환된 데이터를 GCS에 저장
df.write.mode("overwrite").format("parquet").partitionBy("Date").save(GCS_OUTPUT_PATH)
print(f"GCS → {GCS_OUTPUT_PATH}")

# 변환된 데이터를 Local에도 저장 (테스트용)
df.write.mode("overwrite").format("parquet").partitionBy("Date").save(LOCAL_OUTPUT_PATH)
print(f"Local → {LOCAL_OUTPUT_PATH}")

# Spark 세션 종료
spark.stop()
