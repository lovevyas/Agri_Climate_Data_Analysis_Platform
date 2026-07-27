
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = SparkSession.builder \
    .appName("Explore") \
    .master("local[*]") \
    .getOrCreate()

csv_path = "datasets/raw/agriculture_crop_analysis.csv"

print("--- 1. Read with inferSchema=True ---")
df_infer = spark.read.csv(csv_path, header=True, inferSchema=True)
df_infer.printSchema()

print("--- 2. Read with explicit schema ---")
explicit_schema = StructType([
    StructField("farm_id", StringType(), True),
    StructField("state", StringType(), True),
    StructField("district", StringType(), True),
    StructField("crop", StringType(), True),
    StructField("soil_ph", DoubleType(), True),
    StructField("actual_yield_tonnes", DoubleType(), True),
    StructField("profit_loss_inr", DoubleType(), True)
])

df_explicit = spark.read.csv(csv_path, header=True, schema=explicit_schema)

print("--- Checkpoint ---")
print(f"Row count: {df_explicit.count()} (Expected: 2000)")

spark.stop()
