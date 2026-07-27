import streamlit as st
from data_loader import render_data_source_sidebar
from views import overview, usecase1_yield_weather, usecase2_climate_risk, usecase3_noaa_environment, hidden_insights

st.set_page_config(
    page_title="Agri-Climate Risk Analytics Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

dfs = render_data_source_sidebar()

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go To Page",
    [
        "Platform Overview",
        "Use Case 1: Yield & Weather",
        "Use Case 2: Climate Risk",
        "Use Case 3: NOAA Environment",
        "Hidden Insights",
    ],
)

PAGES = {
    "Platform Overview": overview,
    "Use Case 1: Yield & Weather": usecase1_yield_weather,
    "Use Case 2: Climate Risk": usecase2_climate_risk,
    "Use Case 3: NOAA Environment": usecase3_noaa_environment,
    "Hidden Insights": hidden_insights,
}

PAGES[page].render(dfs)
