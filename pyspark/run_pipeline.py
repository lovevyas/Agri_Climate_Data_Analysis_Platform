

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyspark.sql import SparkSession
from extraction.extract_sources import extract_all
from transformation.transform_pipeline import transform_all
from loading.load_to_parquet import load_all

def main():
    print("Starting Agri-Climate ETL Pipeline...")

    spark = SparkSession.builder \
        .appName('AgriClimateETL') \
        .master('local[1]') \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    try:
        ag_df, imd_df, noaa_df = extract_all(spark, raw_dir='datasets/raw')

        dim_farms, dim_weather_stations, fact_crop_yield, fact_weather_observations, fact_global_climate_environment = transform_all(ag_df, imd_df, noaa_df)

        load_all(dim_farms, dim_weather_stations, fact_crop_yield, fact_weather_observations, fact_global_climate_environment, curated_dir='datasets/curated')

        print("Pipeline completed successfully!")

    except Exception as e:
        print(f"Pipeline failed: {e}")
        raise e
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
