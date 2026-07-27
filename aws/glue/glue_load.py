"""Writes the curated tables out to S3 (Parquet) and RDS Postgres (JDBC)."""

# Installed via the Glue job's --additional-python-modules argument (see infra/glue.tf)
import psycopg2

# Truncating a table that other tables reference by foreign key is only allowed
# if every dependent is truncated in the same statement, hence one command for
# all eight. RESTART IDENTITY resets the analytics tables' SERIAL primary keys.
RESET_SQL = """
    TRUNCATE TABLE
        fact_crop_yield, fact_weather_observations, fact_global_climate_environment,
        dim_farms, dim_weather_stations,
        analytics.yield_weather_correlation, analytics.climate_risk_farms,
        analytics.global_environment_summary
    RESTART IDENTITY CASCADE;
"""


def jdbc_settings(args):
    """Build the JDBC url and connection properties from the job arguments."""
    url = f"jdbc:postgresql://{args['RDS_HOST']}:{args['RDS_PORT']}/{args['RDS_DB']}"
    props = {
        "user": args["RDS_USER"],
        "password": args["RDS_PASSWORD"],
        "driver": "org.postgresql.Driver",
    }
    return url, props


def write_curated_parquet(tables, curated_prefix):
    """Write each table to the S3 curated zone, partitioned where it helps."""
    partition_by = {
        "fact_crop_yield": "season",
        "fact_weather_observations": "season",
        "fact_global_climate_environment": "country",
    }

    for name, df in tables.items():
        writer = df.write.mode("overwrite")
        if name in partition_by:
            writer = writer.partitionBy(partition_by[name])
        writer.parquet(f"{curated_prefix}/{name}")


def reset_tables(args):
    """Empty every table so the run reloads from a clean slate.

    Spark's own mode="overwrite" issues DROP TABLE, which the foreign keys
    reject and which would discard the DECIMAL types from create_tables.sql in
    favour of Spark's inferred ones. Truncating first lets every write below
    use append against the already-correct schema.
    """
    print("Resetting tables before reload (TRUNCATE ... CASCADE)...")
    conn = psycopg2.connect(
        host=args["RDS_HOST"], port=args["RDS_PORT"], dbname=args["RDS_DB"],
        user=args["RDS_USER"], password=args["RDS_PASSWORD"],
    )
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(RESET_SQL)
    finally:
        conn.close()


def load_star_schema(tables, url, props):
    """Load dimensions before facts so the foreign keys resolve."""
    print("Loading Dimension Tables to RDS...")
    for name in ("dim_farms", "dim_weather_stations"):
        tables[name].write.jdbc(url=url, table=name, mode="append", properties=props)

    print("Loading Fact Tables to RDS...")
    for name in ("fact_crop_yield", "fact_weather_observations", "fact_global_climate_environment"):
        tables[name].write.jdbc(url=url, table=name, mode="append", properties=props)
