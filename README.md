# Agri-Climate Risk & Global Environmental Analytics Platform

This repository houses the cloud-based analytics pipeline, database configurations, automated test suite, and Streamlit web dashboard for connecting crop yields with official weather stations and global NOAA observations.

---

## 📁 Repository Structure

```
agri-climate-risk-analytics-platform/
├── README.md                           # This quick start guide
├── documentation/
│   ├── Project_Documentation.md        # Consolidated project documentation
│   └── WORKFLOW.md                     # Full workflow guide (all module READMEs consolidated)
├── sql/
│   ├── schema/
│   │   └── create_tables.sql           # Database schema initialization DDL
│   └── analysis_queries/
│       ├── task_1_avg_profit_by_state_crop.sql
│       └── ... (10 query files)
├── pyspark/
│   └── transformation/
│       └── etl_job.py                  # Local PySpark ETL script (Pandas/PyArrow workaround)
├── aws/
│   ├── glue/
│   │   └── glue_job.py                 # Production AWS Glue PySpark script
│   └── lambda/
│       └── trigger_glue.py             # S3 PUT event handler trigger code
├── visualizations/
│   └── app.py                          # Streamlit web dashboard app
├── testing/
│   └── verify_tests.py                 # Automated verification script
└── datasets/
    └── raw/                            # Ingestion source CSVs
```

---

## 🚀 Quick Start Guide (Local Execution)

Follow these steps to run the pipeline, verify the test cases, and launch the web dashboard locally.

### Step 1: Environment Setup
Ensure you have Python 3.9+ and OpenJDK 11 installed, then set up your virtual environment:
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # On Windows use: .venv\Scripts\activate

# Install dependencies (including pyarrow for Windows Parquet support)
pip install pyspark==3.5.1 pandas matplotlib seaborn psycopg2-binary boto3 sqlalchemy pyarrow
```

### Step 2: Run the PySpark ETL Job
Execute the local transformation script to clean the raw data, perform exact/fallback weather station matching, and output curated Parquet files:
```bash
python pyspark/transformation/etl_job.py
```
This will output clean, partitioned Parquet tables in `datasets/curated/`.

### Step 3: Run the Automated Test Suite
Verify that all 15 test scenarios pass and output the QA audit log:
```bash
python testing/verify_tests.py
```
The results will print to the console and save to `testing/test_results_log.csv`.

### Step 4: Launch the Streamlit Dashboard
Launch the interactive web-based reporting dashboard:
```bash
streamlit run visualizations/app.py
```
This opens the dashboard in your web browser. You can view crop yields, reporting gaps, pest warnings, and global NOAA environmental observations dynamically!

---

## 💡 Developer Mindset Docs
See [documentation/WORKFLOW.md](documentation/WORKFLOW.md) for the full workflow guide, consolidating what used to be a separate `README.md` per directory, explaining:
- **Why** the code was written that way.
- **The flow of data** through each script.
- **Senior developer insights** regarding database indexing, column collisions, window functions, and serverless architectures.
