import streamlit as st
import graphs


def render(dfs):
    yield_df = dfs["fact_crop_yield"]
    noaa_df = dfs["fact_global_climate_environment"]

    st.title("💡 Hidden Insights in the Data")
    st.write(
        "Sometimes the most obvious charts don't tell the whole story, because averages "
        "can look very similar. Here are some hidden, strong mathematical relationships "
        "we found in the data, explained simply!"
    )

    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("#### 1. Evapotranspiration vs. Temperature (NOAA Data)")
        if not noaa_df.empty:
            fig = graphs.plot_evapotranspiration_trend(noaa_df)
            st.pyplot(fig)
            st.caption(
                "Average evaporation climbs at every step of the temperature scale, from 0.8mm below "
                "0C to 6.0mm above 30C — a roughly sevenfold increase. Temperature and water loss move "
                "almost perfectly together (r = +0.95)."
            )
        else:
            st.warning("Data not available.")

    with col2:
        st.info(
            """
        ### 🔍 The Pattern
        There is a **94% correlation** between temperature and evapotranspiration (how fast water evaporates from the soil and plants). Instead of a complex density map, we've grouped temperatures into simple buckets to show how the average evaporation skyrockets as it gets hotter.

        ### 🧠 The Logic
        As it gets hotter, water turns into vapor much faster. This means on hot days, the soil dries out incredibly quickly.

        ### 🎯 The Outcome
        This chart is a perfect visual for **Water Stress**. It proves to stakeholders that rising temperatures don't just mean a hotter day—they mean a much higher risk of drought for farmers.
        """
        )

    st.markdown("---")

    col3, col4 = st.columns([2, 1])
    with col3:
        st.write("#### 2. Actual Yield vs. Expected Yield (Crop Data)")
        if not yield_df.empty:
            fig = graphs.plot_yield_gap_scatter(yield_df)
            st.pyplot(fig)
            st.caption(
                "Points hug the red perfect-match line closely (r = +0.97), so farms forecast their "
                "harvest well. The points sitting below the line are the shortfalls, averaging about "
                "5% of expected yield."
            )
        else:
            st.warning("Data not available.")

    with col4:
        st.info(
            """
        ### 🔍 The Pattern
        There is a **97% correlation** between what farmers expect to harvest and what they actually harvest. We took a random sample of farms so the chart is clean and easy to read. You can clearly see expectations and reality are tightly bound, but with notable drops below the red perfect match line.

        ### 🧠 The Logic
        The red line shows where expectations perfectly match reality. Dots falling far below the line represent a "Yield Gap"—a significant loss.

        ### 🎯 The Outcome
        By plotting this, agricultural advisors can quickly spot which seasons (like Monsoon) have the most unpredictable harvests, and step in to help farmers estimate better.
        """
        )

    st.markdown("---")

    col5, col6 = st.columns([2, 1])
    with col5:
        st.write("#### 3. Air Quality (AQI) vs. Precipitation (NOAA Data)")
        if not noaa_df.empty:
            fig = graphs.plot_aqi_by_precipitation(noaa_df)
            st.pyplot(fig)
            st.caption(
                "Average AQI falls steadily from the dry bucket through to heavy rain, confirming rain "
                "clears particulates from the air (r = -0.74). This is the effect the flat AQI-by-country "
                "chart in Use Case 3 was missing."
            )
        else:
            st.warning("Data not available.")

    with col6:
        st.info(
            """
        ### 🔍 The Pattern
        Instead of a chaotic map of dots, we grouped the rainfall amounts into buckets (Dry, Light, Moderate, Heavy). We clearly see that as precipitation rises, the average AQI falls (improving air quality).

        ### 🧠 The Logic
        Certain extreme weather events (like heavy precipitation) act as natural air scrubbers, washing particulate matter out of the atmosphere.

        ### 🎯 The Outcome
        This helps global insurers understand *what* physical events drive poor environmental quality, allowing them to price environmental risk policies based on weather triggers rather than just location.
        """
        )
