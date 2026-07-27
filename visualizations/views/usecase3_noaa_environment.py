import streamlit as st
import graphs
import graphs_insights

DROUGHT_ORDER = ["Low", "Medium", "High"]


def render(dfs):
    noaa_df = dfs["fact_global_climate_environment"]

    st.title("🌍 Use Case 3: Global Environmental Monitoring")
    st.subheader("Tracking atmospheric indicators and disaster risks across North American geographies")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("#### 1. Average Air Quality Index (AQI) by Country")
        if not noaa_df.empty:
            aqi_summary = noaa_df.groupby("country")["air_quality_index"].mean().reset_index()
            fig = graphs.plot_aqi_by_country(aqi_summary)
            st.pyplot(fig)
            st.caption(
                "All three bars land within one point of each other (106.7, 107.0, 106.2), so average "
                "air quality is effectively identical across the three countries. Country is not what "
                "drives AQI in this data — rainfall is, as the drought chart below shows."
            )
        else:
            st.warning("Data not available.")

    with col2:
        st.info(
            """
        ### 🔍 What We Notice (Readings):
        - **Regional AQI**: The bar chart lists the average Air Quality Index for Canada, Mexico, and the USA. Notice that higher AQI readings indicate poorer air quality.
        - **Drought and Disaster Risk**: The heatmap below details how disaster risk levels (Low, Medium, High) correlate with climate zones (Continental, Temperate, Polar, etc.).
        """
        )

    st.markdown("---")

    col3, col4 = st.columns([1, 2])

    with col3:
        st.info(
            """
        ### 💡 Business Direction & Value:
        - **Macro-Level Advisory**:
          Provides an independent environmental backdrop. Analyzing global indicators like CO2 (ppm) and Methane (ppb) allows global policy advisors to benchmark regional climate changes and predict long-term soil moisture trends.
        - **Difference It Makes**:
          Allows global crop insurers to set reinsurance premium rates based on the percentage of extreme-risk weather events occurring across climate zones.
        """
        )

    with col4:
        st.write("#### 2. Climate Zone × Disaster Risk Distribution")
        if not noaa_df.empty:
            pivot_risk = noaa_df.pivot_table(
                index="climate_zone", columns="disaster_risk", values="observation_id", aggfunc="count", fill_value=0
            )
            pivot_risk_pct = pivot_risk.div(pivot_risk.sum(axis=1), axis=0) * 100
            fig = graphs.plot_disaster_risk_heatmap(pivot_risk_pct)
            st.pyplot(fig)
            st.caption(
                "Every cell sits near 33%, meaning each climate zone splits evenly across Low, Medium "
                "and High risk. Climate zone carries no information about disaster risk in this "
                "dataset — the heatmap below uses the same chart type on variables that do relate."
            )
        else:
            st.warning("Data not available.")

    st.markdown("---")

    col5, col6 = st.columns([2, 1])

    with col5:
        st.write("#### 3. How the Environmental Measures Relate to Each Other")
        if not noaa_df.empty:
            fig = graphs_insights.plot_env_correlation_heatmap(noaa_df)
            st.pyplot(fig)
            st.caption(
                "Deep red squares are strong positive links, deep blue strong negative. Two real "
                "clusters appear: temperature drives evapotranspiration (r = +0.95), and rainfall "
                "raises humidity and soil moisture while washing pollutants out of the air (r = -0.74 "
                "against AQI)."
            )
        else:
            st.warning("Data not available.")

    with col6:
        st.write("#### 4. Drought Index Profile")
        if not noaa_df.empty:
            drought_summary = (
                noaa_df.groupby("drought_index")[["soil_moisture_percent", "precipitation_mm"]]
                .mean()
                .reindex(DROUGHT_ORDER)
                .reset_index()
            )
            fig = graphs_insights.plot_drought_profile(drought_summary)
            st.pyplot(fig)
            st.caption(
                "Both panels fall in step as drought severity rises: soil moisture drops from 43.9% to "
                "32.3% and rainfall from 30.5mm to 3.3mm. Unlike climate zone, the drought index is a "
                "genuine summary of local water availability."
            )
        else:
            st.warning("Data not available.")
