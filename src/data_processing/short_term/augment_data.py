from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, stddev, when, lag, lit, to_date
from pyspark.sql.window import Window
import datetime

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("Silver_Layer_Processing") \
    .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
    .config("spark.hadoop.fs.gs.auth.service.account.enable", "true") \
    .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "/opt/keys/gcs-key.json") \
    .getOrCreate()

today = datetime.datetime.today().strftime('%Y%m%d')

# GCS 설정
GCS_BUCKET = "short-term"
BRONZE_PATH = f"gs://{GCS_BUCKET}/collected/sp500_top50_{today}.csv"
BQ_DATASET = "short_term"
BQ_TABLE_SILVER = "fact_stock_prices_silver"

# Bronze 데이터 로드
df = spark.read.option("header", True).csv(BRONZE_PATH)

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

# NULL 값 처리 (보정)
df = df.withColumn("Market_Cap", when(col("Market_Cap").isNull(), 0).otherwise(col("Market_Cap"))) \
       .withColumn("PE_Ratio", when(col("PE_Ratio").isNull(), 0).otherwise(col("PE_Ratio"))) \
       .withColumn("PB_Ratio", when(col("PB_Ratio").isNull(), 0).otherwise(col("PB_Ratio"))) \
       .withColumn("Dividend_Yield", when(col("Dividend_Yield").isNull(), 0).otherwise(col("Dividend_Yield"))) \
       .withColumn("EPS", when(col("EPS").isNull(), 0).otherwise(col("EPS"))) \
       .withColumn("52_Week_High", when(col("52_Week_High").isNull(), col("Close")).otherwise(col("52_Week_High"))) \
       .withColumn("52_Week_Low", when(col("52_Week_Low").isNull(), col("Close")).otherwise(col("52_Week_Low")))

# 기술적 지표 계산 추가
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

# RSI(14일) 계산 추가
df = df.withColumn("Price_Change", col("Close") - lag("Close", 1).over(window_14)) \
       .withColumn("Gain", when(col("Price_Change") > 0, col("Price_Change")).otherwise(0)) \
       .withColumn("Loss", when(col("Price_Change") < 0, -col("Price_Change")).otherwise(0)) \
       .withColumn("Avg_Gain", avg(col("Gain")).over(window_14)) \
       .withColumn("Avg_Loss", avg(col("Loss")).over(window_14)) \
       .withColumn("RS", col("Avg_Gain") / when(col("Avg_Loss") == 0, lit(1)).otherwise(col("Avg_Loss"))) \
       .withColumn("RSI_14", 100 - (100 / (1 + col("RS")))) \
       .drop("Price_Change", "Gain", "Loss", "Avg_Gain", "Avg_Loss", "RS")

# 컬럼 순서 강제 정렬 (BigQuery 에러 방지)
expected_columns = [
    "Ticker", "Date", "Open", "High", "Low", "Close", "Volume",
    "Market_Cap", "PE_Ratio", "PB_Ratio", "Dividend_Yield", "EPS",
    "52_Week_High", "52_Week_Low", "Moving_Avg_5", "Moving_Avg_20",
    "Moving_Avg_50", "Volatility_30d", "RSI_14"
]
df = df.select(*expected_columns)

# BigQuery에 Silver 데이터 저장
df.write.format("bigquery") \
    .option("temporaryGcsBucket", GCS_BUCKET) \
    .option("table", f"{BQ_DATASET}.{BQ_TABLE_SILVER}") \
    .mode("overwrite") \
    .save()

print(f"Silver Data loaded into BigQuery with fixed column order: {BQ_DATASET}.{BQ_TABLE_SILVER}")

# Spark 세션 종료
spark.stop()
