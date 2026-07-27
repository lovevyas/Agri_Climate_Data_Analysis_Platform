
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, row_number, rank, avg, lit

spark = SparkSession.builder \
    .appName("WindowFunctions") \
    .master("local[*]") \
    .getOrCreate()

df = spark.read.csv("datasets/raw/agriculture_crop_analysis.csv", header=True, inferSchema=True)

print("--- Deduplication Pattern ---")
window_dedup = Window.partitionBy("farm_id").orderBy(lit(1))
df_dedup = df.withColumn("rn", row_number().over(window_dedup)) \
    .filter(col("rn") == 1) \
    .drop("rn")

print(f"Deduplicated count: {df_dedup.count()} (Expected: 2000)")

print("--- Ranking: Best crop per state by sustainability score ---")
crop_scores = df.groupBy("state", "crop").agg(avg("sustainability_score").alias("avg_score"))

window_rank = Window.partitionBy("state").orderBy(col("avg_score").desc())
ranked_crops = crop_scores.withColumn("rank", rank().over(window_rank))

best_crops = ranked_crops.filter(col("rank") == 1)

print("--- Checkpoint ---")
best_crops.show(truncate=False)
print(f"Rows shown: {best_crops.count()} (Expected: 8, one per state)")

spark.stop()
