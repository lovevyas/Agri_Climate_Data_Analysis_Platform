

from pyspark.sql.functions import col, lit, abs as spark_abs, datediff, row_number, to_date, upper, lower
from pyspark.sql import Window

def transform_all(ag_df, imd_df, noaa_df):

    print("--- Phases 2-5: TRANSFORMATION ---")

    print("Section 1: Deduplicating raw data...")
    ag_window = Window.partitionBy("farm_id").orderBy("farm_id")
    ag_clean = ag_df.withColumn("rn", row_number().over(ag_window)) \
                    .filter(col("rn") == 1).drop("rn")

    imd_window = Window.partitionBy("station_code", "observation_date").orderBy("station_code")
    imd_clean = imd_df.withColumn("rn", row_number().over(imd_window)) \
                      .filter(col("rn") == 1).drop("rn")

    noaa_window = Window.partitionBy("observation_id").orderBy("observation_id")
    noaa_clean = noaa_df.withColumn("rn", row_number().over(noaa_window)) \
                        .filter(col("rn") == 1).drop("rn")

    print("Section 2: Standardizing text and dates...")
    ag_clean = ag_clean.withColumn("state", upper(col("state"))) \
                       .withColumn("district", upper(col("district"))) \
                       .withColumn("crop", upper(col("crop"))) \
                       .withColumn("sowing_date", to_date(col("sowing_date"), "yyyy-MM-dd")) \
                       .withColumn("harvesting_date", to_date(col("harvesting_date"), "yyyy-MM-dd"))

    imd_clean = imd_clean.withColumn("state", upper(col("state"))) \
                         .withColumn("district", upper(col("district"))) \
                         .withColumn("observation_date", to_date(col("observation_date"), "yyyy-MM-dd"))

    noaa_clean = noaa_clean.withColumn("country", upper(col("country"))) \
                           .withColumn("climate_zone", upper(col("climate_zone"))) \
                           .withColumn("date", to_date(col("date"), "yyyy-MM-dd"))

    print("Section 3: Building Dimension Tables...")
    dim_farms = ag_clean.select(
        "farm_id", "state", "district", "village", "crop", "crop_variety",
        "soil_type", "soil_ph", "land_area_acres", "irrigation_method"
    ).dropDuplicates(["farm_id"])

    dim_weather_stations = imd_clean.select(
        "station_code", "station_name", "state", "district"
    ).dropDuplicates(["state", "district"])

    print(f"Dim Farms Count: {dim_farms.count()}")
    print(f"Dim Weather Stations Count: {dim_weather_stations.count()}")

    print("Section 4: Matching Farms to Weather Stations...")
    exact_match = ag_clean.join(
        dim_weather_stations.select("station_code", "state", "district"),
        on=["state", "district"],
        how="inner"
    ).withColumnRenamed("station_code", "matched_station_code") \
     .withColumn("match_type", lit("Exact District Match"))

    unmatched_farms = ag_clean.join(
        dim_weather_stations,
        on=["state", "district"],
        how="left_anti"
    )

    station_readings = imd_clean.select("station_code", "state", "observation_date") \
                                .dropDuplicates(["station_code", "observation_date"])

    fallback_candidates = unmatched_farms.join(
        station_readings,
        on=["state"],
        how="inner"
    )

    fallback_candidates = fallback_candidates.withColumn(
        "date_diff", spark_abs(datediff(col("sowing_date"), col("observation_date")))
    )

    closest_station_window = Window.partitionBy("farm_id").orderBy("date_diff")
    fallback_match = fallback_candidates.withColumn("rn", row_number().over(closest_station_window)) \
                                        .filter(col("rn") == 1) \
                                        .withColumnRenamed("station_code", "matched_station_code") \
                                        .withColumn("match_type", lit("Nearest In State")) \
                                        .drop("observation_date", "date_diff", "rn")

    fallback_match = fallback_match.select(exact_match.columns)

    matched_farms_df = exact_match.unionByName(fallback_match)

    exact_count = exact_match.count()
    fallback_count = fallback_match.count()
    print(f"Exact Matches: {exact_count}")
    print(f"Fallback Matches: {fallback_count}")
    print(f"Total Matched Farms: {matched_farms_df.count()} (Expected: 2000)")

    print("Section 5: Building Fact Tables...")
    fact_crop_yield = matched_farms_df.select(
        "farm_id", "sowing_date", "harvesting_date", "season",
        col("rainfall_mm").alias("farm_reported_rainfall_mm"),
        col("avg_temperature_c").alias("farm_reported_avg_temp_c"),
        col("humidity_percent").alias("farm_reported_humidity_pct"),
        "nitrogen_kg_ha", "phosphorus_kg_ha", "potassium_kg_ha", "fertilizer_used",
        "pest_attack", "disease_name", "pesticide_used",
        "expected_yield_tonnes", "actual_yield_tonnes",
        (col("expected_yield_tonnes") - col("actual_yield_tonnes")).alias("yield_gap_tonnes"),
        "water_consumption_litres", "production_cost_inr", "market_price_inr", "profit_loss_inr",
        "crop_health_score", "sustainability_score", "matched_station_code", "match_type"
    )

    fact_weather_observations = imd_clean.join(
        dim_weather_stations.select("station_code"),
        on="station_code",
        how="inner"
    )

    fact_global_climate_environment = noaa_clean

    print("Transformation complete.\n")
    return dim_farms, dim_weather_stations, fact_crop_yield, fact_weather_observations, fact_global_climate_environment
