

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, LongType

def extract_all(spark, raw_dir='datasets/raw'):

    ag_schema = StructType([
        StructField("farm_id", StringType(), False),
        StructField("state", StringType(), True),
        StructField("district", StringType(), True),
        StructField("village", StringType(), True),
        StructField("crop", StringType(), True),
        StructField("crop_variety", StringType(), True),
        StructField("sowing_date", StringType(), True),
        StructField("harvesting_date", StringType(), True),
        StructField("season", StringType(), True),
        StructField("land_area_acres", DoubleType(), True),
        StructField("soil_type", StringType(), True),
        StructField("soil_ph", DoubleType(), True),
        StructField("nitrogen_kg_ha", IntegerType(), True),
        StructField("phosphorus_kg_ha", IntegerType(), True),
        StructField("potassium_kg_ha", IntegerType(), True),
        StructField("fertilizer_used", StringType(), True),
        StructField("irrigation_method", StringType(), True),
        StructField("rainfall_mm", DoubleType(), True),
        StructField("avg_temperature_c", DoubleType(), True),
        StructField("humidity_percent", IntegerType(), True),
        StructField("pest_attack", StringType(), True),
        StructField("disease_name", StringType(), True),
        StructField("pesticide_used", StringType(), True),
        StructField("expected_yield_tonnes", DoubleType(), True),
        StructField("actual_yield_tonnes", DoubleType(), True),
        StructField("water_consumption_litres", DoubleType(), True),
        StructField("production_cost_inr", DoubleType(), True),
        StructField("market_price_inr", DoubleType(), True),
        StructField("profit_loss_inr", DoubleType(), True),
        StructField("crop_health_score", IntegerType(), True),
        StructField("sustainability_score", IntegerType(), True)
    ])

    imd_schema = StructType([
        StructField("station_code", StringType(), False),
        StructField("station_name", StringType(), True),
        StructField("state", StringType(), True),
        StructField("district", StringType(), True),
        StructField("observation_date", StringType(), True),
        StructField("season", StringType(), True),
        StructField("max_temp_c", DoubleType(), True),
        StructField("min_temp_c", DoubleType(), True),
        StructField("avg_temp_c", DoubleType(), True),
        StructField("rainfall_mm", DoubleType(), True),
        StructField("relative_humidity_percent", IntegerType(), True),
        StructField("wind_speed_kmh", DoubleType(), True),
        StructField("wind_direction", StringType(), True),
        StructField("visibility_km", DoubleType(), True),
        StructField("cloud_cover_percent", IntegerType(), True),
        StructField("sunshine_hours", DoubleType(), True),
        StructField("atmospheric_pressure_hpa", DoubleType(), True),
        StructField("soil_temperature_c", DoubleType(), True),
        StructField("heat_index_c", DoubleType(), True),
        StructField("dew_point_c", DoubleType(), True),
        StructField("flood_warning", StringType(), True),
        StructField("cyclone_alert", StringType(), True),
        StructField("rainfall_category", StringType(), True),
        StructField("weather_condition", StringType(), True)
    ])

    noaa_schema = StructType([
        StructField("observation_id", LongType(), False),
        StructField("date", StringType(), True),
        StructField("station_id", StringType(), True),
        StructField("country", StringType(), True),
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True),
        StructField("elevation_m", DoubleType(), True),
        StructField("avg_temperature_c", DoubleType(), True),
        StructField("max_temperature_c", DoubleType(), True),
        StructField("min_temperature_c", DoubleType(), True),
        StructField("precipitation_mm", DoubleType(), True),
        StructField("snowfall_cm", DoubleType(), True),
        StructField("humidity_percent", IntegerType(), True),
        StructField("wind_speed_kmh", DoubleType(), True),
        StructField("wind_direction", StringType(), True),
        StructField("solar_radiation_wm2", DoubleType(), True),
        StructField("atmospheric_pressure_hpa", DoubleType(), True),
        StructField("cloud_cover_percent", IntegerType(), True),
        StructField("uv_index", IntegerType(), True),
        StructField("soil_moisture_percent", DoubleType(), True),
        StructField("drought_index", StringType(), True),
        StructField("evapotranspiration_mm", DoubleType(), True),
        StructField("air_quality_index", IntegerType(), True),
        StructField("pm25", DoubleType(), True),
        StructField("pm10", DoubleType(), True),
        StructField("co2_ppm", DoubleType(), True),
        StructField("methane_ppb", DoubleType(), True),
        StructField("ozone_ppb", DoubleType(), True),
        StructField("climate_zone", StringType(), True),
        StructField("weather_event", StringType(), True),
        StructField("disaster_risk", StringType(), True)
    ])

    print("--- Phase 1: EXTRACTION ---")

    ag_df = spark.read.csv(f"{raw_dir}/agriculture_crop_analysis.csv", schema=ag_schema, header=True)
    imd_df = spark.read.csv(f"{raw_dir}/imd_weather_station_data.csv", schema=imd_schema, header=True)
    noaa_df = spark.read.csv(f"{raw_dir}/noaa_climate_environmental_data.csv", schema=noaa_schema, header=True)

    print(f"Extracted Agriculture Records: {ag_df.count()}")
    print(f"Extracted IMD Weather Records: {imd_df.count()}")
    print(f"Extracted NOAA Climate Records: {noaa_df.count()}")
    print("Extraction complete.\n")

    return ag_df, imd_df, noaa_df
