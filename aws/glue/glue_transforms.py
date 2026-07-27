"""Cleaning, dimension building, farm-to-station matching and fact construction.

The fact builders project down to exactly the columns declared in
sql/schema/create_tables.sql. That projection is load-bearing: the JDBC writes
run in append mode against pre-created tables, so any stray column here fails
the insert instead of silently reshaping the table.
"""

from pyspark.sql import Window
from pyspark.sql.functions import (
    col, lit, abs as spark_abs, datediff, row_number, to_date, upper
)

# Column lists mirroring create_tables.sql.
FACT_CROP_YIELD_COLS = [
    "farm_id", "sowing_date", "harvesting_date", "season",
    "nitrogen_kg_ha", "phosphorus_kg_ha", "potassium_kg_ha", "fertilizer_used",
    "farm_reported_rainfall_mm", "farm_reported_avg_temp_c", "farm_reported_humidity_pct",
    "pest_attack", "disease_name", "pesticide_used",
    "expected_yield_tonnes", "actual_yield_tonnes", "yield_gap_tonnes",
    "water_consumption_litres", "production_cost_inr", "market_price_inr", "profit_loss_inr",
    "crop_health_score", "sustainability_score", "matched_station_code", "match_type",
]

FACT_WEATHER_COLS = [
    "station_code", "observation_date", "season",
    "max_temp_c", "min_temp_c", "avg_temp_c", "rainfall_mm",
    "relative_humidity_percent", "wind_speed_kmh", "wind_direction", "visibility_km",
    "cloud_cover_percent", "sunshine_hours", "atmospheric_pressure_hpa",
    "soil_temperature_c", "heat_index_c", "dew_point_c",
    "flood_warning", "cyclone_alert", "rainfall_category", "weather_condition",
]


def deduplicate(df, unique_key_cols):
    """Keep one arbitrary but deterministic row per key."""
    keys = [unique_key_cols] if isinstance(unique_key_cols, str) else unique_key_cols
    window_spec = Window.partitionBy(*keys).orderBy(lit(1))
    return (
        df.withColumn("row_num", row_number().over(window_spec))
        .filter(col("row_num") == 1)
        .drop("row_num")
    )


def clean_agriculture(df):
    return (
        deduplicate(df, "farm_id")
        .withColumn("state", upper(col("state")))
        .withColumn("district", upper(col("district")))
        .withColumn("crop", upper(col("crop")))
        .withColumn("sowing_date", to_date(col("sowing_date"), "yyyy-MM-dd"))
        .withColumn("harvesting_date", to_date(col("harvesting_date"), "yyyy-MM-dd"))
    )


def clean_imd(df):
    return (
        deduplicate(df, ["station_code", "observation_date"])
        .withColumn("state", upper(col("state")))
        .withColumn("district", upper(col("district")))
        .withColumn("observation_date", to_date(col("observation_date"), "yyyy-MM-dd"))
    )


def clean_noaa(df):
    return (
        deduplicate(df, "observation_id")
        .withColumn("country", upper(col("country")))
        .withColumn("climate_zone", upper(col("climate_zone")))
        .withColumn("date", to_date(col("date"), "yyyy-MM-dd"))
    )


def build_dimensions(ag_clean, imd_clean):
    dim_farms = ag_clean.select(
        "farm_id", "state", "district", "village", "crop", "crop_variety",
        "soil_type", "soil_ph", "land_area_acres", "irrigation_method",
    ).dropDuplicates(["farm_id"])

    dim_weather_stations = imd_clean.select(
        "station_code", "station_name", "state", "district"
    ).dropDuplicates(["station_code"])

    return dim_farms, dim_weather_stations


def match_farms_to_stations(ag_clean, imd_clean, dim_weather_stations):
    """Resolve every farm to one weather station.

    Farms whose (state, district) matches a station take that station. The rest
    fall back to the station in the same state whose reading is closest in time
    to the sowing date.
    """
    keep_cols = ag_clean.columns + ["matched_station_code", "match_type"]

    exact_raw = (
        ag_clean.join(dim_weather_stations, on=["state", "district"], how="inner")
        .withColumn("matched_station_code", col("station_code"))
        .withColumn("match_type", lit("Exact District Match"))
    )
    # A district can hold several stations, which would fan one farm out into
    # several rows and collide with fact_crop_yield's farm_id primary key.
    exact_matches = (
        exact_raw
        .withColumn("_rn", row_number().over(Window.partitionBy("farm_id").orderBy("station_code")))
        .filter(col("_rn") == 1)
        .select(*keep_cols)
    )

    unmatched = ag_clean.join(dim_weather_stations, on=["state", "district"], how="left_anti")

    # Project to just the join keys: carrying all of imd_clean here would
    # duplicate column names (season, rainfall_mm...) and make later
    # references ambiguous.
    station_readings = imd_clean.select("station_code", "state", "observation_date")
    fallback = (
        unmatched.join(station_readings, on="state", how="inner")
        .withColumn("date_diff", spark_abs(datediff(col("sowing_date"), col("observation_date"))))
        .withColumn("_rn", row_number().over(
            Window.partitionBy("farm_id").orderBy("date_diff", "station_code")
        ))
        .filter(col("_rn") == 1)
        .withColumn("matched_station_code", col("station_code"))
        .withColumn("match_type", lit("Nearest In State"))
        .select(*keep_cols)
    )

    return exact_matches.unionByName(fallback)


def build_fact_crop_yield(matched_farms):
    return (
        matched_farms
        .withColumnRenamed("rainfall_mm", "farm_reported_rainfall_mm")
        .withColumnRenamed("avg_temperature_c", "farm_reported_avg_temp_c")
        .withColumnRenamed("humidity_percent", "farm_reported_humidity_pct")
        .withColumn("yield_gap_tonnes", col("expected_yield_tonnes") - col("actual_yield_tonnes"))
        .select(*FACT_CROP_YIELD_COLS)
    )


def build_fact_weather_observations(imd_clean):
    """One row per station: the table's primary key is station_code alone.

    Today's source data already holds exactly one observation per station, so
    this is a no-op guard -- it exists so a future file carrying several dates
    per station degrades to the latest reading instead of failing the insert.
    """
    latest = Window.partitionBy("station_code").orderBy(col("observation_date").desc())
    return (
        imd_clean
        .withColumn("_rn", row_number().over(latest))
        .filter(col("_rn") == 1)
        .select(*FACT_WEATHER_COLS)
    )
