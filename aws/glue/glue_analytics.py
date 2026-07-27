"""Pre-aggregated summary tables backing the three dashboard use cases.

Computed here so the dashboard reads a small ready-made table instead of
aggregating the full fact tables on every page load.
"""

from pyspark.sql.functions import avg, col, count, expr, sum as spark_sum, when


def _merge_crop_and_weather(fact_crop_yield, fact_weather_observations, dim_farms):
    """Join each farm's yield row to its matched station reading.

    state and crop live on dim_farms (fact_crop_yield holds only the foreign
    key), so the dimension is joined back in to group by them.
    """
    crop_with_dims = fact_crop_yield.join(
        dim_farms.select("farm_id", "state", "crop"), on="farm_id", how="inner"
    )
    return crop_with_dims.join(
        fact_weather_observations,
        on=crop_with_dims["matched_station_code"] == fact_weather_observations["station_code"],
        how="inner",
    )


def build_all(fact_crop_yield, fact_weather_observations, fact_global_climate, dim_farms):
    """Return {table_name: dataframe} for every analytics.* table."""
    merged = _merge_crop_and_weather(fact_crop_yield, fact_weather_observations, dim_farms)

    yield_weather_correlation = merged.groupBy("state", "crop").agg(
        (avg(col("farm_reported_rainfall_mm") - col("rainfall_mm")) / avg(col("rainfall_mm")) * 100)
        .alias("rainfall_reporting_gap_pct"),
        avg(col("profit_loss_inr")).alias("avg_profit_loss_inr"),
        avg(col("yield_gap_tonnes")).alias("avg_yield_gap_tonnes"),
    )

    climate_risk_farms = (
        merged
        .withColumn("exposure_flag", expr(
            "CASE WHEN flood_warning = 'YES' OR cyclone_alert = 'YES' "
            "THEN 'Flood/Cyclone Alert' ELSE 'No Alert' END"
        ))
        .groupBy("state", "crop", "exposure_flag")
        .agg(
            (spark_sum(when(col("pest_attack") == "YES", 1).otherwise(0)) / count("*") * 100)
            .alias("pest_attack_rate_pct"),
            avg(col("crop_health_score")).alias("avg_crop_health_score"),
            avg(col("sustainability_score")).alias("avg_sustainability_score"),
        )
    )

    global_environment_summary = fact_global_climate.groupBy("country", "climate_zone").agg(
        avg(col("air_quality_index")).alias("avg_air_quality_index"),
        avg(col("co2_ppm")).alias("avg_co2_ppm"),
        avg(col("methane_ppb")).alias("avg_methane_ppb"),
        (spark_sum(when(col("disaster_risk") == "HIGH", 1).otherwise(0)) / count("*") * 100)
        .alias("high_disaster_risk_pct"),
    )

    return {
        "analytics.yield_weather_correlation": yield_weather_correlation,
        "analytics.climate_risk_farms": climate_risk_farms,
        "analytics.global_environment_summary": global_environment_summary,
    }


def load_all(summaries, url, props):
    print("Computing and Loading Analytics Tables to RDS...")
    for table, df in summaries.items():
        df.write.jdbc(url=url, table=table, mode="append", properties=props)
