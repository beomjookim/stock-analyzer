import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, when
from pyspark.sql.window import Window

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("SP500_ShortTerm_Processing") \
    .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
    .config("spark.hadoop.fs.gs.auth.service.account.enable", "true") \
    .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "/opt/keys/gcs-key.json") \
    .getOrCreate()


# GCS 및 BigQuery 설정
GCS_BUCKET = "short-term"  # 기존 GCS 버킷 사용
BQ_DATASET = "short_term"
BQ_TABLE = "sp500_top50"

today = datetime.datetime.today().strftime('%Y%m%d')
GCS_INPUT_PATH = f"gs://{GCS_BUCKET}/collected/sp500_top50_{today}.csv"

# GCS에서 CSV 데이터 로드
df = spark.read.option("header", True).csv(GCS_INPUT_PATH)

# 데이터 변환 수행
window_spec = Window.partitionBy("Ticker").orderBy(col("Date").cast("timestamp")).rowsBetween(-4, 0)
df = df.withColumn("Moving_Avg", avg(col("Close")).over(window_spec))
df = df.withColumn("Daily_Change", ((col("High") - col("Low")) / col("Open") * 100))
df = df.withColumn("Volatility", when(col("Volatility").isNull(), 0).otherwise(col("Volatility")))

# BigQuery로 데이터 저장
df.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", 'short-term') \
    .option("table", "short_term.sp500_top50") \
    .mode("overwrite") \
    .save()

print(f"BigQuery 적재 완료: {BQ_DATASET}.{BQ_TABLE}")

# Spark 세션 종료
spark.stop()
