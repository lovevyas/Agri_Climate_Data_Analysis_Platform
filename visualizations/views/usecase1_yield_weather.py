import streamlit as st
import pandas as pd
import graphs
import graphs_insights

# Label -> column for the "what drives profit?" x-axis picker.
PROFIT_DRIVERS = {
    "Official Station Rainfall (mm)": "rainfall_mm",
    "Production Cost (INR)": "production_cost_inr",
    "Land Area (acres)": "land_area_acres",
}


def _merge(yield_df, farms_df, weather_df):
    return pd.merge(yield_df, farms_df, on="farm_id").merge(
        weather_df, left_on="matched_station_code", right_on="station_code", suffixes=("", "_station")
    )


def _render_profit_explorer(merged):
    st.write("#### 3. Profit Driver Explorer (interactive)")

    all_crops = sorted(merged["crop"].unique())
    col_a, col_b = st.columns([1, 1])
    with col_a:
        crops = st.multiselect("Crops to compare", all_crops, default=all_crops[:4])
    with col_b:
        driver = st.radio("Compare profit against", list(PROFIT_DRIVERS), index=0)

    if not crops:
        st.info("Select at least one crop above to draw the chart.")
        return

    fig = graphs_insights.plot_profit_trend(merged, PROFIT_DRIVERS[driver], driver, crops)
    st.pyplot(fig)

    if PROFIT_DRIVERS[driver] == "rainfall_mm":
        st.caption(
            "Each line is close to flat, so rainfall recorded at the official station barely moves "
            "farm profitability (r = 0.05). Switch the selector to Production Cost or Land Area to "
            "see what actually does."
        )
    else:
        st.caption(
            f"Every crop line slopes steadily downward: as {driver} rises, average profit falls "
            "and never crosses back above break-even. Profit here is literally market price minus "
            "production cost, and cost outruns revenue on larger farms."
        )


def render(dfs):
    yield_df = dfs["fact_crop_yield"]
    farms_df = dfs["dim_farms"]
    weather_df = dfs["fact_weather_observations"]

    st.title("📈 Use Case 1: Yield vs. Official Weather Correlation")
    st.subheader("Analyzing the relationship between crop profitability and weather parameters")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("#### 1. Profitability vs. Official Station Rainfall")
        if not yield_df.empty and not farms_df.empty and not weather_df.empty:
            merged = _merge(yield_df, farms_df, weather_df)
            fig = graphs.plot_yield_vs_rainfall(merged)
            st.pyplot(fig)
            st.caption(
                "The points form one flat cloud with no left-to-right slope, and almost all of it sits "
                "below the break-even line: station rainfall does not separate profitable farms from "
                "unprofitable ones. See the interactive explorer below for the variable that does."
            )
        else:
            st.warning("Data not available to plot.")

    with col2:
        st.info(
            """
        ### 🔍 What We Notice (Readings):
        - **Profitability Threshold**: The red dashed line represents the break-even mark (0 INR). Notice that almost all dots (representing individual crop cycles) are scattered **below** the line.
        - **Crop Sensitivity**: Crops like *MAIZE* and *COTTON* require moderate to high rainfall but continue to show heavy losses even under optimal weather.
        - **Rainfall Clustering**: Profit and losses are highly clustered, suggesting that weather alone is not the sole cause of farm financial failure.
        """
        )

    st.markdown("---")

    col3, col4 = st.columns([1, 2])

    with col3:
        st.info(
            """
        ### 💡 Business Direction & Value:
        - **Exposing the reporting gap**:
          Agricultural advisors can now prove that farms self-report weather variables (like rainfall) with significant deviations from official IMD readings.
        - **Difference It Makes**:
          By cross-referencing crop insurance claims with official station rainfall (rather than subjective farm-reported values), insurers can reduce fraud and advisors can help farms optimize irrigation methods based on official water levels.
        """
        )

    with col4:
        st.write("#### 2. Average Rainfall Reporting Gap by State (Farm vs. Station)")
        if not yield_df.empty and not farms_df.empty and not weather_df.empty:
            merged = _merge(yield_df, farms_df, weather_df)
            merged["rainfall_gap_mm"] = merged["farm_reported_rainfall_mm"] - merged["rainfall_mm"]
            gap_summary = merged.groupby("state")["rainfall_gap_mm"].mean().reset_index()
            fig = graphs.plot_rainfall_gap(gap_summary)
            st.pyplot(fig)
            st.caption(
                "Bars above zero are states where farms self-report more rainfall than the official "
                "station recorded, below zero the reverse. The size of the gap is what matters here: "
                "it is the measurable disagreement between farmer-supplied and official weather data."
            )
        else:
            st.warning("Data not available to plot.")

    st.markdown("---")

    if not yield_df.empty and not farms_df.empty and not weather_df.empty:
        _render_profit_explorer(_merge(yield_df, farms_df, weather_df))
