# Agri-Climate Risk & Global Environmental Analytics Platform

**[Live dashboard →](https://agriclimate.streamlit.app/)**

An end-to-end data platform that joins Indian farm crop-yield records to official
IMD weather-station readings and global NOAA climate observations, then serves the
result through a Streamlit dashboard.

The same pipeline runs two ways: **locally** with PySpark writing Parquet, and **on
AWS** as a serverless pipeline provisioned entirely by Terraform.

---

## Architecture (AWS)

```
CSV upload to s3://<bucket>/raw/
            |
            v
   S3 ObjectCreated event
            |
            v
   Lambda (trigger_glue.py)  --  starts the Glue job with RDS connection args
            |
            v
   Glue PySpark ETL
            |
            +--> s3://<bucket>/curated/   partitioned Parquet
            |
            +--> RDS PostgreSQL           queryable star schema
```

Everything above is defined in `infra/` as Terraform. `boto3` appears only inside
the Lambda, where it is the tool for the job; provisioning is not done imperatively.

---

## Data model

A star schema, created by `sql/schema/create_tables.sql` before any load runs.

**Dimensions** — `dim_farms`, `dim_weather_stations`

**Facts** — `fact_crop_yield`, `fact_weather_observations`, `fact_global_climate_environment`

**Analytics rollups** (schema `analytics`) — `yield_weather_correlation`,
`climate_risk_farms`, `global_environment_summary`

Two design points worth knowing before reading the ETL:

- **Farm-to-station matching.** A farm matching a station on `(state, district)`
  takes that station. Farms with no district match fall back to the station in the
  same state whose reading is closest in time to the sowing date. Because a district
  can hold several stations, the exact match is deduplicated to one station per farm —
  without that, one farm fans out into several rows and collides with
  `fact_crop_yield`'s primary key.

- **Loading order and reset strategy.** Spark's `mode="overwrite"` issues `DROP TABLE`,
  which the foreign keys reject and which would replace the DDL's `DECIMAL` types with
  Spark's inferred ones. Instead every table is emptied with one
  `TRUNCATE ... RESTART IDENTITY CASCADE` (Postgres only permits truncating an
  FK-referenced table if its dependents go in the same statement), then written with
  `mode="append"` — dimensions before facts.

---

## Repository structure

```
agri-climate-risk-analytics-platform/
├── infra/                              # Terraform: the whole AWS stack
│   ├── main.tf                         # S3 bucket, raw CSV upload, Glue script + module zip
│   ├── iam.tf                          # least-privilege roles for Glue and Lambda
│   ├── rds.tf                          # RDS Postgres (db.t3.micro, free tier)
│   ├── glue.tf                         # Glue job definition and job arguments
│   ├── lambda.tf                       # Lambda function, S3 event notification
│   ├── variables.tf / outputs.tf / providers.tf
│   ├── apply_schema.py                 # one-time: run create_tables.sql against RDS
│   └── test_glue_args.ps1              # start the Glue job with args from tf outputs
│
├── aws/
│   ├── glue/                           # production ETL, one concern per module
│   │   ├── glue_job.py                 #   entry point and orchestration
│   │   ├── glue_schemas.py             #   explicit schemas for the three CSVs
│   │   ├── glue_transforms.py          #   cleaning, dimensions, matching, facts
│   │   ├── glue_load.py                #   Parquet + JDBC writes, table reset
│   │   └── glue_analytics.py           #   the analytics.* rollups
│   └── lambda/
│       └── trigger_glue.py             # S3 event -> glue.start_job_run
│
├── pyspark/                            # local equivalent of the Glue job
│   ├── run_pipeline.py                 #   entry point
│   ├── extraction/extract_sources.py
│   ├── transformation/transform_pipeline.py
│   ├── loading/load_to_parquet.py
│   └── exploration/                    # standalone PySpark learning scripts
│
├── visualizations/                     # Streamlit dashboard
│   ├── app.py                          #   entry point: page config, sidebar, routing
│   ├── data_loader.py                  #   local Parquet or live RDS
│   ├── graphs.py                       #   charts required by the specification
│   ├── graphs_insights.py              #   additional charts (see "Reading the charts")
│   └── views/                          #   one module per dashboard page
│
├── sql/
│   ├── schema/create_tables.sql         # DDL: the star schema
│   └── analysis_queries/                # 10 standalone analysis queries
│
├── testing/verify_tests.py              # verification against the curated output
├── datasets/raw/                         # the three source CSVs
├── datasets/curated/                     # Parquet output (what the dashboard reads)
└── requirements.txt
```

Glue runs a single entry-point script, so the four modules `glue_job.py` imports
travel separately: Terraform zips them and passes the zip via `--extra-py-files`.
Adding a module to `aws/glue/` means adding it to `local.glue_modules` in
`infra/main.tf`, or Glue will fail with `ModuleNotFoundError`.

---

## Running it locally

Requires Python 3.9+ and a JDK (17 works; PySpark needs a JVM).

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

The local pipeline additionally needs PySpark, which is not in `requirements.txt`
because Glue supplies its own:

```bash
pip install pyspark==3.5.1
```

Run the pipeline, then the checks, then the dashboard:

```bash
python pyspark/run_pipeline.py     # raw CSVs -> datasets/curated/ Parquet
python testing/verify_tests.py     # writes testing/test_results_log.csv
streamlit run visualizations/app.py
```

The dashboard defaults to reading local Parquet, so it works with no AWS account.
Its sidebar can also connect to a live RDS instance if you have one running.

The [hosted copy](https://agriclimate.streamlit.app/) runs this same code on
Streamlit Community Cloud, reading the committed Parquet files. Its RDS option is
left unused there — connecting would mean typing a database password into a public
page, and the AWS side of the project is demonstrated by `infra/` instead.

---

## Deploying to AWS

Requires the AWS CLI configured (`aws configure`) and Terraform installed.

```bash
cd infra
terraform init
terraform apply
```

That provisions the S3 bucket, IAM roles, RDS instance, Glue job and Lambda, and
uploads the raw CSVs plus the ETL code. Then create the tables once:

```bash
# from infra/, with DB_HOST and DB_PASSWORD from `terraform output`
python apply_schema.py
```

From here the pipeline is event-driven — uploading a CSV to `raw/` starts the Glue
job automatically:

```bash
aws s3 cp ../datasets/raw/agriculture_crop_analysis.csv s3://<bucket>/raw/
```

To start a run directly instead:

```powershell
.\test_glue_args.ps1
```

### Cost

RDS is the only component billed by the hour; S3, Glue and Lambda are
pay-per-use and negligible at this volume. When you are finished:

```bash
terraform destroy
```

> **Note on the RDS configuration.** The database is deliberately
> `publicly_accessible = true` with ingress from `0.0.0.0/0`, so the dashboard can
> reach it from a laptop without a bastion host or VPN. It is protected only by a
> generated 20-character password. This is a demo convenience, not a pattern to
> copy — production would place RDS in a private subnet and reach it through a
> bastion, VPN, or a VPC-attached Lambda.

---

## Reading the charts

The dashboard implements the charts the specification asked for. On this dataset
several of them plot variables that turn out to be statistically independent:

| Chart | Result |
|---|---|
| Climate Zone × Disaster Risk | ~33% in every cell — zone carries no information about risk |
| Average AQI by Country | 106.7 / 107.0 / 106.2 — no separation |
| Pest rate, Alert vs No-Alert | 33.9% vs 32.2% — alerts do not predict pest attacks |
| Station rainfall vs profit | r = 0.05 |

Those charts are kept, and each carries a caption saying plainly that it shows no
relationship. Alongside each one sits a companion chart from `graphs_insights.py`
built on a relationship that does hold:

| Relationship | r |
|---|---|
| Temperature → evapotranspiration | +0.95 |
| Expected → actual yield | +0.97 |
| Precipitation → AQI | −0.74 |
| Production cost → profit | −0.89 |
| Pest attack → crop health | 77 → 45 (32-point drop) |

The strongest finding is that `profit_loss_inr` equals
`market_price_inr − production_cost_inr` exactly, and cost runs roughly twice
revenue throughout — which is why 95% of farms show a loss regardless of weather.
Profitability here is a cost-structure story, not a climate one.
