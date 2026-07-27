
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder \
    .appName("FiltersAndColumns") \
    .master("local[*]") \
    .getOrCreate()

df = spark.read.csv("datasets/raw/agriculture_crop_analysis.csv", header=True, inferSchema=True)

df_selected = df.select("farm_id", "state", "crop", "profit_loss_inr", "expected_yield_tonnes", "actual_yield_tonnes")

loss_making_df = df_selected.filter(col("profit_loss_inr") < 0)
loss_count = loss_making_df.count()

profitable_df = df_selected.filter(col("profit_loss_inr") >= 0)
profitable_count = profitable_df.count()

print("--- Checkpoint ---")
print(f"Loss-making farms: {loss_count} (Expected: 1908)")
print(f"Profitable farms: {profitable_count} (Expected: 92)")

df_with_gap = df_selected.withColumn("yield_gap", col("expected_yield_tonnes") - col("actual_yield_tonnes"))

print("\n--- Show first 5 rows with yield_gap ---")
df_with_gap.select("farm_id", "expected_yield_tonnes", "actual_yield_tonnes", "yield_gap").show(5)

spark.stop()
