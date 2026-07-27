import streamlit as st
import pandas as pd


def render(dfs):
    farms_df = dfs["dim_farms"]
    stations_df = dfs["dim_weather_stations"]
    yield_df = dfs["fact_crop_yield"]
    noaa_df = dfs["fact_global_climate_environment"]

    st.title("🌾 Agri-Climate Risk & Global Environmental Analytics Platform")
    st.write(
        "Welcome to the command dashboard for regional advisory and environmental "
        "analytics. This dashboard combines crop yields across 8 Indian states, "
        "official India Meteorological Department (IMD) weather alerts, and global "
        "NOAA climate trends."
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Farms Profiled", len(yield_df))
    with col2:
        st.metric("Unique Crop Varieties", farms_df["crop_variety"].nunique() if not farms_df.empty else 0)
    with col3:
        if not yield_df.empty:
            loss_pct = (yield_df["profit_loss_inr"] < 0).mean() * 100
            st.metric("Farms Operating at Loss (%)", f"{loss_pct:.1f}%")
        else:
            st.metric("Farms Operating at Loss (%)", "N/A")
    with col4:
        # Count the stations farms were actually resolved to, not every station
        # in the dimension -- most stations are never matched to a farm.
        matched = yield_df["matched_station_code"].nunique() if not yield_df.empty else 0
        st.metric("Official Stations Matched", matched)

    st.markdown("---")

    st.subheader("📋 Dataset Samples Preview")
    tab1, tab2, tab3 = st.tabs(["Farms & Yields", "Official Weather Stations", "NOAA Climate Observations"])
    with tab1:
        st.write("Previewing first 5 rows of matched fact_crop_yield joined with dim_farms:")
        if not yield_df.empty and not farms_df.empty:
            preview = pd.merge(yield_df, farms_df, on="farm_id").head(5)
            st.dataframe(preview)
        else:
            st.write("No data loaded.")
    with tab2:
        st.write("Previewing official IMD stations:")
        if not stations_df.empty:
            st.dataframe(stations_df.head(5))
        else:
            st.write("No data loaded.")
    with tab3:
        st.write("Previewing global NOAA observations:")
        if not noaa_df.empty:
            st.dataframe(noaa_df.head(5))
        else:
            st.write("No data loaded.")
