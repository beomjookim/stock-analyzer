import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, stddev
from pyspark.sql.window import Window

# Spark 세션 생성
spark = SparkSession.builder.appName("SP500_ShortTerm_Processing").getOrCreate()

# ✅ 가장 최근의 CSV 파일 찾기
def get_latest_csv(directory):
    files = [f for f in os.listdir(directory) if f.startswith("sp500_top50_") and f.endswith(".csv")]
    files.sort(reverse=True)  # 최신 날짜 순 정렬
    return os.path.join(directory, files[0]) if files else None

# ✅ Docker에서 공유된 폴더로 데이터 경로 변경
data_dir = "/opt/spark/data/short_term"  # ✅ 변경됨
latest_file = get_latest_csv(data_dir)

if latest_file:
    print(f"Processing latest file: {latest_file}")

    # CSV → Spark DataFrame 로드
    df = spark.read.csv(latest_file, header=True, inferSchema=True)

    # ✅ 이동 평균(Moving Average) 추가 (5일 기준)
    window_spec = Window.partitionBy("Ticker").orderBy(col("Date").cast("timestamp")).rowsBetween(-4, 0)
    df = df.withColumn("Moving_Avg", avg(col("Close")).over(window_spec))

    # ✅ 변동성(Daily Change) 계산
    df = df.withColumn("Daily_Change", ((col("High") - col("Low")) / col("Open") * 100))

    # ✅ 최근 5일간 표준편차(Volatility) 계산
    df = df.withColumn("Volatility", stddev(col("Close")).over(window_spec))

    # ✅ 날짜(Date) 기준으로 파티셔닝하여 Parquet 저장
    df.write.mode("overwrite").partitionBy("Date").parquet("/opt/spark/data/short_term/processed/sp500_top50_partitioned")

    print("Short-term data successfully transformed and saved.")

else:
    print("No CSV files found for processing.")

# df = spark.read.parquet("/opt/spark/data/short_term/processed/sp500_top50_partitioned/")
# df.show()
# 디버깅용