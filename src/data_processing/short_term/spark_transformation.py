import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, stddev, avg, when, lag, lit
from pyspark.sql.window import Window
from pyspark.sql.types import FloatType, IntegerType
import time

start_time = time.time()

# 🔹 Spark 세션 생성
spark = SparkSession.builder \
    .appName("SP500_Processing_Optimized") \
    .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
    .config("spark.hadoop.fs.gs.auth.service.account.enable", "true") \
    .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "/opt/keys/gcs-key.json") \
    .getOrCreate()

# 🔹 GCS 및 BigQuery 설정
GCS_BUCKET = "short-term"
BQ_DATASET = "short_term"
BQ_TABLE_STOCK_PRICES = "fact_stock_prices"
BQ_TABLE_TECHNICAL = "fact_technical_indicators"
BQ_TABLE_FUNDAMENTAL = "fact_fundamental_metrics"

# 🔹 데이터 로드
today = datetime.datetime.today().strftime('%Y%m%d')
df = spark.read.option("header", True).csv(f"gs://{GCS_BUCKET}/collected/sp500_top50_{today}.csv")

# 🔹 (1) 데이터 타입 변환 최적화
df = df.withColumn("Open", col("Open").cast(FloatType())) \
       .withColumn("High", col("High").cast(FloatType())) \
       .withColumn("Low", col("Low").cast(FloatType())) \
       .withColumn("Close", col("Close").cast(FloatType())) \
       .withColumn("Volume", col("Volume").cast(IntegerType())) \
       .withColumn("Market_Cap", col("Market_Cap").cast(FloatType())) \
       .withColumn("PE_Ratio", col("PE_Ratio").cast(FloatType())) \
       .withColumn("PB_Ratio", col("PB_Ratio").cast(FloatType())) \
       .withColumn("Dividend_Yield", col("Dividend_Yield").cast(FloatType())) \
       .withColumn("EPS", col("EPS").cast(FloatType())) \
       .withColumn("52_Week_High", col("52_Week_High").cast(FloatType())) \
       .withColumn("52_Week_Low", col("52_Week_Low").cast(FloatType()))

# 🔹 (2) `coalesce(5)` 적용 (Shuffling 방지)
df = df.coalesce(5)

# 🔹 (3) 데이터 캐싱 (반복 연산 속도 향상)
df = df.cache()

# 🔹 (4) 기술적 지표 계산 최적화
window_5 = Window.partitionBy("Ticker").orderBy(col("Date")).rowsBetween(-4, 0)
window_20 = Window.partitionBy("Ticker").orderBy(col("Date")).rowsBetween(-19, 0)
window_50 = Window.partitionBy("Ticker").orderBy(col("Date")).rowsBetween(-49, 0)
window_30 = Window.partitionBy("Ticker").orderBy(col("Date")).rowsBetween(-29, 0)
window_14 = Window.partitionBy("Ticker").orderBy(col("Date"))

df = df.withColumn("Moving_Avg_5", avg(col("Close")).over(window_5)) \
       .withColumn("Moving_Avg_20", avg(col("Close")).over(window_20)) \
       .withColumn("Moving_Avg_50", avg(col("Close")).over(window_50)) \
       .withColumn("Volatility_30d", stddev(col("Close")).over(window_30)) \
       .withColumn("Volatility_30d", when(col("Volatility_30d").isNull(), 0).otherwise(col("Volatility_30d")))

# 🔹 (5) RSI(14일) 계산 최적화
df = df.withColumn("Price_Change", col("Close") - lag("Close", 1).over(window_14)) \
       .withColumn("Gain", when(col("Price_Change") > 0, col("Price_Change")).otherwise(0)) \
       .withColumn("Loss", when(col("Price_Change") < 0, -col("Price_Change")).otherwise(0)) \
       .withColumn("Avg_Gain", avg(col("Gain")).over(window_14)) \
       .withColumn("Avg_Loss", avg(col("Loss")).over(window_14)) \
       .withColumn("RS", col("Avg_Gain") / when(col("Avg_Loss") == 0, lit(1)).otherwise(col("Avg_Loss"))) \
       .withColumn("RSI_14", 100 - (100 / (1 + col("RS")))) \
       .drop("Price_Change", "Gain", "Loss", "Avg_Gain", "Avg_Loss", "RS")

# 🔹 (6) 기술적 지표 데이터 저장 (fact_technical_indicators)
df_technical = df.select("Ticker", "Date", "Moving_Avg_5", "Moving_Avg_20", "Moving_Avg_50", "Volatility_30d", "RSI_14")

df_technical.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", GCS_BUCKET) \
    .option("table", f"{BQ_DATASET}.{BQ_TABLE_TECHNICAL}") \
    .mode("overwrite") \
    .save()

print(f"✅ BigQuery 적재 완료: {BQ_DATASET}.{BQ_TABLE_TECHNICAL}")

# 🔹 (7) 원본 데이터 저장 (fact_stock_prices)
df_stock_prices = df.select("Ticker", "Date", "Open", "High", "Low", "Close", "Volume")

df_stock_prices.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", GCS_BUCKET) \
    .option("table", f"{BQ_DATASET}.{BQ_TABLE_STOCK_PRICES}") \
    .mode("overwrite") \
    .save()

print(f"✅ BigQuery 적재 완료: {BQ_DATASET}.{BQ_TABLE_STOCK_PRICES}")

# 🔹 (8) 재무 지표 데이터 저장 (fact_fundamental_metrics)
df_fundamental = df.select("Ticker", "Market_Cap", "PE_Ratio", "PB_Ratio", "Dividend_Yield", "EPS", "52_Week_High", "52_Week_Low")

df_fundamental.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", GCS_BUCKET) \
    .option("table", f"{BQ_DATASET}.{BQ_TABLE_FUNDAMENTAL}") \
    .mode("overwrite") \
    .save()

print(f"✅ BigQuery 적재 완료: {BQ_DATASET}.{BQ_TABLE_FUNDAMENTAL}")

end_time = time.time()

print("execution time: " + str(end_time - start_time) + "s")

# 🔹 Spark 세션 종료
spark.stop()
