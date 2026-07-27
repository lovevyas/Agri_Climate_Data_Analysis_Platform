
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("JoinsPractice") \
    .master("local[*]") \
    .getOrCreate()

agri_df = spark.read.csv("datasets/raw/agriculture_crop_analysis.csv", header=True, inferSchema=True)
imd_df = spark.read.csv("datasets/raw/imd_weather_stations.csv", header=True, inferSchema=True)

imd_unique = imd_df.select("station_code", "station_name", "state", "district") \
    .dropDuplicates(["state", "district"])

print("--- Inner Join ---")
matched_farms = agri_df.join(imd_unique, on=["state", "district"], how="inner")
print(f"Matched farms count: {matched_farms.count()}")

print("--- Left Anti Join (Unmatched Farms) ---")
unmatched_farms = agri_df.join(imd_unique, on=["state", "district"], how="left_anti")
unmatched_locations = unmatched_farms.select("state", "district").dropDuplicates()

print("--- Checkpoint ---")
unmatched_locations.show(truncate=False)
print("left_anti should surface ONLY farms in Belagavi and Kota districts.")

spark.stop()
