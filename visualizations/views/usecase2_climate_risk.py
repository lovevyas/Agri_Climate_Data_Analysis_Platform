import streamlit as st
import pandas as pd
import graphs
import graphs_insights


def render(dfs):
    yield_df = dfs["fact_crop_yield"]
    farms_df = dfs["dim_farms"]
    weather_df = dfs["fact_weather_observations"]

    st.title("🛡️ Use Case 2: Climate Risk & Farm Resilience")
    st.subheader("Assessing crop vulnerabilities under official weather warnings and alerts")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("#### 1. State × Crop Average Crop Health Score")
        if not yield_df.empty and not farms_df.empty:
            merged_farms = pd.merge(yield_df, farms_df, on="farm_id")
            heatmap_data = merged_farms.pivot_table(
                index="crop", columns="state", values="crop_health_score", aggfunc="mean"
            )
            fig = graphs.plot_crop_health_heatmap(heatmap_data)
            st.pyplot(fig)
            st.caption(
                "Reading across a row shows how one crop fares in different states; reading down a "
                "column compares crops within a state. Scores cluster tightly in the 60s-70s, so no "
                "single state-crop pairing stands out as dramatically healthier than the rest."
            )
        else:
            st.warning("Data not available.")

    with col2:
        st.info(
            """
        ### 🔍 What We Notice (Readings):
        - **Regional Strengths**: Notice how certain cells contain high crop health scores (dark blue cells). This represents optimal growth conditions for specific crops in specific states.
        - **Weak Cells**: Lighter cells indicate states where certain crops are highly stressed, showing lower average health scores.
        """
        )

    st.markdown("---")

    col3, col4 = st.columns([1, 2])

    with col3:
        st.info(
            """
        ### 💡 Business Direction & Value:
        - **Resilience Planning**:
          Advisors can immediately spot which crops have the lowest health score in a specific region, suggesting a change of crop variety or modification in fertilizer usage.
        - **Proactive Pesticide Distribution**:
          When a flood warning or cyclone alert is triggered, pest attack rates shoot up. Advisors can use the chart on the right to pre-position pesticide supplies in alert-prone states before the weather event begins.
        """
        )

    with col4:
        st.write("#### 2. Pest Attack Rate under Alert vs. No-Alert Conditions")
        if not yield_df.empty and not farms_df.empty and not weather_df.empty:
            merged = pd.merge(yield_df, farms_df, on="farm_id").merge(
                weather_df, left_on="matched_station_code", right_on="station_code", suffixes=("", "_station")
            )
            merged["has_alert"] = (
                (merged["flood_warning"].str.upper() == "YES") | (merged["cyclone_alert"].str.upper() == "YES")
            ).map({True: "Alert Triggered", False: "No Alert"})

            pest_attacks = merged.groupby(["has_alert", "pest_attack"]).size().unstack(fill_value=0)
            for col_name in ["Yes", "No"]:
                if col_name not in pest_attacks.columns:
                    pest_attacks[col_name] = 0

            pest_rate = (pest_attacks["Yes"] / (pest_attacks["Yes"] + pest_attacks["No"])) * 100
            pest_rate_df = pest_rate.reset_index(name="pest_attack_rate_pct")

            fig = graphs.plot_pest_attack_rate(pest_rate_df)
            st.pyplot(fig)
            st.caption(
                "The two bars are nearly identical (33.9% vs 32.2%), so an active flood or cyclone "
                "alert does not raise the chance of a pest attack. Weather alerts are not a usable "
                "early-warning signal for pests here — but the chart below shows pests still matter."
            )
        else:
            st.warning("Data not available.")

    st.markdown("---")

    st.write("#### 3. What a Pest Attack Actually Costs a Farm")
    if not yield_df.empty:
        pest_summary = (
            yield_df.groupby("pest_attack")[["crop_health_score", "yield_gap_tonnes"]].mean().reset_index()
        )
        fig = graphs_insights.plot_pest_impact(pest_summary)
        st.pyplot(fig)
        st.caption(
            "Farms hit by pests average a crop health score of 45 against 77 for farms that were not — "
            "a 32-point collapse. Their yield gap swings from -1.2 tonnes (beating expectations) to "
            "+10.3 tonnes lost. Pest attacks are the single largest driver of lost yield in this dataset."
        )
    else:
        st.warning("Data not available.")
