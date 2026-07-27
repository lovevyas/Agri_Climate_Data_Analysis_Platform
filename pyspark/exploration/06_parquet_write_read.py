
import os
import shutil
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count
import pandas as pd

spark = SparkSession.builder \
    .appName("ParquetWriteRead") \
    .master("local[*]") \
    .getOrCreate()

df = spark.read.csv("datasets/raw/agriculture_crop_analysis.csv", header=True, inferSchema=True)

summary_df = df.groupBy("state").agg(
    avg("profit_loss_inr").alias("avg_profit_loss"),
    count("*").alias("farm_count")
)

summary_pandas = summary_df.toPandas()

output_dir = "datasets/curated/exploration_test"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "summary.parquet")

print(f"--- Writing to Parquet at {output_path} ---")
summary_pandas.to_parquet(output_path, engine='pyarrow')

print("--- Reading back from Parquet ---")
read_back_pandas = pd.read_parquet(output_path, engine='pyarrow')

print("--- Checkpoint ---")
print(read_back_pandas)
print(f"\nRow count read back: {len(read_back_pandas)} (Expected: 8)")

print(f"\n--- Cleaning up {output_dir} ---")
shutil.rmtree(output_dir)

spark.stop()
