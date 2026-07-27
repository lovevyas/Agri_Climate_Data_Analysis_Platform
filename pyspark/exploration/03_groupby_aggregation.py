
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count, round

spark = SparkSession.builder \
    .appName("GroupByAggregation") \
    .master("local[*]") \
    .getOrCreate()

df = spark.read.csv("datasets/raw/agriculture_crop_analysis.csv", header=True, inferSchema=True)

print("--- Group by state ---")
state_summary = df.groupBy("state") \
    .agg(
        round(avg("profit_loss_inr"), 2).alias("avg_profit_loss"),
        count("*").alias("farm_count")
    ) \
    .orderBy("avg_profit_loss")

state_summary.show(truncate=False)

print("--- Group by state and crop ---")
state_crop_summary = df.groupBy("state", "crop") \
    .agg(round(avg("profit_loss_inr"), 2).alias("avg_profit_loss")) \
    .orderBy("state", "crop")

state_crop_summary.show(20, truncate=False)

print("--- Checkpoint ---")
print(f"Number of states shown: {state_summary.count()} (Expected: 8)")
print("Each state should have farm_count around 230-260.")

spark.stop()
