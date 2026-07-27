"""Agri-Climate ETL: raw CSVs on S3 -> star schema in S3 Parquet + RDS Postgres.

Entry point only. The work lives in the sibling modules, which Terraform zips
and ships to Glue via --extra-py-files (see infra/glue.tf):
    glue_schemas.py     explicit CSV schemas
    glue_transforms.py  cleaning, dimensions, farm-station matching, facts
    glue_load.py        Parquet + JDBC writes
    glue_analytics.py   the analytics.* summary tables
"""

import sys
from types import ModuleType

# Python 3.12 removed distutils, but PySpark 3.5's toPandas() path still reaches
# for distutils.version.LooseVersion. Register a stand-in before pyspark loads.
if 'distutils' not in sys.modules:
    distutils = ModuleType('distutils')
    sys.modules['distutils'] = distutils
    distutils_version = ModuleType('distutils.version')
    sys.modules['distutils.version'] = distutils_version

    class LooseVersion:
        def __init__(self, version_str):
            self.version = version_str

        def __lt__(self, other):
            return False

        def __gt__(self, other):
            return False

        def __eq__(self, other):
            return True

    distutils_version.LooseVersion = LooseVersion

from pyspark.context import SparkContext
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job

import glue_schemas
import glue_transforms
import glue_load
import glue_analytics

RAW_FILES = {
    "agriculture": ("agriculture_crop_analysis.csv", glue_schemas.agriculture_schema),
    "imd": ("imd_weather_station_data.csv", glue_schemas.imd_schema),
    "noaa": ("noaa_climate_environmental_data.csv", glue_schemas.noaa_schema),
}


def main():
    args = getResolvedOptions(
        sys.argv,
        ['JOB_NAME', 'S3_BUCKET_NAME', 'RDS_HOST', 'RDS_PORT', 'RDS_DB', 'RDS_USER', 'RDS_PASSWORD'],
    )

    glue_context = GlueContext(SparkContext())
    spark = glue_context.spark_session
    job = Job(glue_context)
    job.init(args['JOB_NAME'], args)

    bucket = args['S3_BUCKET_NAME']
    raw_prefix = f"s3://{bucket}/raw"
    curated_prefix = f"s3://{bucket}/curated"

    # Extract
    raw = {
        name: spark.read.csv(f"{raw_prefix}/{filename}", header=True, schema=schema())
        for name, (filename, schema) in RAW_FILES.items()
    }

    # Transform
    ag_clean = glue_transforms.clean_agriculture(raw["agriculture"])
    imd_clean = glue_transforms.clean_imd(raw["imd"])
    noaa_clean = glue_transforms.clean_noaa(raw["noaa"])

    dim_farms, dim_weather_stations = glue_transforms.build_dimensions(ag_clean, imd_clean)
    matched_farms = glue_transforms.match_farms_to_stations(ag_clean, imd_clean, dim_weather_stations)

    tables = {
        "dim_farms": dim_farms,
        "dim_weather_stations": dim_weather_stations,
        "fact_crop_yield": glue_transforms.build_fact_crop_yield(matched_farms),
        "fact_weather_observations": glue_transforms.build_fact_weather_observations(imd_clean),
        "fact_global_climate_environment": noaa_clean,
    }

    # Load
    glue_load.write_curated_parquet(tables, curated_prefix)

    url, props = glue_load.jdbc_settings(args)
    glue_load.reset_tables(args)
    glue_load.load_star_schema(tables, url, props)

    summaries = glue_analytics.build_all(
        tables["fact_crop_yield"],
        tables["fact_weather_observations"],
        tables["fact_global_climate_environment"],
        dim_farms,
    )
    glue_analytics.load_all(summaries, url, props)

    job.commit()
    print("AWS Glue Job Execution Complete!")


if __name__ == "__main__":
    main()
