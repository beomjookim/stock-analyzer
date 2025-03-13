import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, stddev, avg, when, lag, lit
from pyspark.sql.window import Window

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("SP500_Processing") \
    .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
    .config("spark.hadoop.fs.gs.auth.service.account.enable", "true") \
    .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "/opt/keys/gcs-key.json") \
    .getOrCreate()

# GCS 및 BigQuery 설정
GCS_BUCKET = "short-term"
BQ_DATASET = "short_term"
BQ_TABLE_STOCK_PRICES = "fact_stock_prices"
BQ_TABLE_TECHNICAL = "fact_technical_indicators"
BQ_TABLE_FUNDAMENTAL = "fact_fundamental_metrics"

# 데이터 로드
today = datetime.datetime.today().strftime('%Y%m%d')
df = spark.read.option("header", True).csv(f"gs://{GCS_BUCKET}/collected/sp500_top50_{today}.csv")

# 데이터 타입 변환 (STRING → FLOAT, INT)
df = df.withColumn("Open", col("Open").cast("FLOAT")) \
       .withColumn("High", col("High").cast("FLOAT")) \
       .withColumn("Low", col("Low").cast("FLOAT")) \
       .withColumn("Close", col("Close").cast("FLOAT")) \
       .withColumn("Volume", col("Volume").cast("INT")) \
       .withColumn("Market_Cap", col("Market_Cap").cast("FLOAT")) \
       .withColumn("PE_Ratio", col("PE_Ratio").cast("FLOAT")) \
       .withColumn("PB_Ratio", col("PB_Ratio").cast("FLOAT")) \
       .withColumn("Dividend_Yield", col("Dividend_Yield").cast("FLOAT")) \
       .withColumn("EPS", col("EPS").cast("FLOAT")) \
       .withColumn("52_Week_High", col("52_Week_High").cast("FLOAT")) \
       .withColumn("52_Week_Low", col("52_Week_Low").cast("FLOAT"))

# 기술적 지표 계산 추가
window_5 = Window.partitionBy("Ticker").orderBy(col("Date")).rowsBetween(-4, 0)
window_20 = Window.partitionBy("Ticker").orderBy(col("Date")).rowsBetween(-19, 0)
window_50 = Window.partitionBy("Ticker").orderBy(col("Date")).rowsBetween(-49, 0)
window_30 = Window.partitionBy("Ticker").orderBy(col("Date")).rowsBetween(-29, 0)

df = df.withColumn("Moving_Avg_5", avg(col("Close")).over(window_5)) \
       .withColumn("Moving_Avg_20", avg(col("Close")).over(window_20)) \
       .withColumn("Moving_Avg_50", avg(col("Close")).over(window_50)) \
       .withColumn("Volatility_30d", stddev(col("Close")).over(window_30)) \
       .withColumn("Volatility_30d", when(col("Volatility_30d").isNull(), 0).otherwise(col("Volatility_30d")))

# RSI(14일) 계산 추가
window_14 = Window.partitionBy("Ticker").orderBy(col("Date"))
df = df.withColumn("Price_Change", col("Close") - lag("Close", 1).over(window_14))
df = df.withColumn("Gain", when(col("Price_Change") > 0, col("Price_Change")).otherwise(0))
df = df.withColumn("Loss", when(col("Price_Change") < 0, -col("Price_Change")).otherwise(0))
df = df.withColumn("Avg_Gain", avg(col("Gain")).over(window_14))
df = df.withColumn("Avg_Loss", avg(col("Loss")).over(window_14))
df = df.withColumn("RS", col("Avg_Gain") / when(col("Avg_Loss") == 0, lit(1)).otherwise(col("Avg_Loss")))
df = df.withColumn("RSI_14", 100 - (100 / (1 + col("RS"))))
df = df.drop("Price_Change", "Gain", "Loss", "Avg_Gain", "Avg_Loss", "RS")

# 기술적 지표 데이터 저장 (fact_technical_indicators)
df_technical = df.select("Ticker", "Date", "Moving_Avg_5", "Moving_Avg_20", "Moving_Avg_50", "Volatility_30d", "RSI_14")

df_technical.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", GCS_BUCKET) \
    .option("table", f"{BQ_DATASET}.{BQ_TABLE_TECHNICAL}") \
    .mode("overwrite") \
    .save()

print(f"BigQuery 적재 완료: {BQ_DATASET}.{BQ_TABLE_TECHNICAL}")

# 원본 데이터 저장 (fact_stock_prices)
df_stock_prices = df.select("Ticker", "Date", "Open", "High", "Low", "Close", "Volume")

df_stock_prices.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", GCS_BUCKET) \
    .option("table", f"{BQ_DATASET}.{BQ_TABLE_STOCK_PRICES}") \
    .mode("overwrite") \
    .save()

print(f"BigQuery 적재 완료: {BQ_DATASET}.{BQ_TABLE_STOCK_PRICES}")

# 재무 지표 데이터 저장 (fact_fundamental_metrics)
df_fundamental = df.select("Ticker", "Market_Cap", "PE_Ratio", "PB_Ratio", "Dividend_Yield", "EPS", "52_Week_High", "52_Week_Low")

df_fundamental.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", GCS_BUCKET) \
    .option("table", f"{BQ_DATASET}.{BQ_TABLE_FUNDAMENTAL}") \
    .mode("overwrite") \
    .save()

print(f"BigQuery 적재 완료: {BQ_DATASET}.{BQ_TABLE_FUNDAMENTAL}")

# Spark 세션 종료
spark.stop()
