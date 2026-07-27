import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

TABLE_NAMES = [
    "dim_farms",
    "dim_weather_stations",
    "fact_crop_yield",
    "fact_weather_observations",
    "fact_global_climate_environment",
]


@st.cache_data
def load_parquet_table(table_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "datasets", "curated", table_name)
    try:
        return pd.read_parquet(path)
    except Exception as e:
        st.error(f"Error loading local parquet table '{table_name}' at {path}: {e}")
        return pd.DataFrame()


def run_db_query(query, engine):
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Query execution failed: {e}")
        return pd.DataFrame()


def load_all_parquet():
    return {name: load_parquet_table(name) for name in TABLE_NAMES}


def load_all_from_db(engine):
    return {name: run_db_query(f"SELECT * FROM {name}", engine) for name in TABLE_NAMES}


def render_data_source_sidebar():
    """Renders the sidebar data-source controls and returns the loaded tables dict."""
    st.sidebar.title("🛠️ Platform Settings")
    data_source = st.sidebar.selectbox(
        "Choose Data Source",
        ["Local Parquet Files (Curated)", "AWS RDS PostgreSQL (Live)"],
    )

    if data_source != "AWS RDS PostgreSQL (Live)":
        return load_all_parquet()

    st.sidebar.subheader("RDS Connection Parameters")
    host = st.sidebar.text_input("Host Endpoint", "agri-climate-db.xxxx.ap-south-1.rds.amazonaws.com")
    port = st.sidebar.text_input("Port", "5432")
    db_name = st.sidebar.text_input("Database Name", "agri_climate")
    username = st.sidebar.text_input("Username", "postgres")
    password = st.sidebar.text_input("Password", type="password")

    if "db_engine" not in st.session_state:
        st.session_state.db_engine = None

    if st.sidebar.button("Connect to Database"):
        try:
            connection_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"
            engine = create_engine(connection_uri)
            with engine.connect():
                pass
            st.session_state.db_engine = engine
            st.sidebar.success("Successfully connected to RDS PostgreSQL!")
        except Exception as e:
            st.session_state.db_engine = None
            st.sidebar.error(f"Connection failed: {e}")

    if st.session_state.db_engine is not None:
        return load_all_from_db(st.session_state.db_engine)

    st.warning(
        "⚠️ Database is not connected yet. Please input credentials in the sidebar "
        "and click Connect. Displaying cached local Parquet data as a placeholder."
    )
    return load_all_parquet()
