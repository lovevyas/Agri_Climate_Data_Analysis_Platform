import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 10})

def plot_yield_vs_rainfall(merged_yield_weather):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        data=merged_yield_weather, 
        x="rainfall_mm", 
        y="profit_loss_inr", 
        hue="crop", 
        alpha=0.7,
        ax=ax
    )
    ax.axhline(0, color='red', linestyle='--', alpha=0.5, label="Profitability Threshold")
    ax.set_xlabel("Official Station Rainfall (mm)")
    ax.set_ylabel("Profit / Loss (INR)")
    ax.legend(title="Crop")
    return fig

def plot_rainfall_gap(gap_summary):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=gap_summary,
        x="state",
        y="rainfall_gap_mm",
        palette="coolwarm",
        ax=ax
    )
    ax.axhline(0, color='gray', linestyle='-')
    ax.set_xlabel("State")
    ax.set_ylabel("Average Rainfall Gap (Farm - Station) in mm")
    plt.setp(ax.get_xticklabels(), rotation=45)
    return fig

def plot_crop_health_heatmap(heatmap_data):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(
        heatmap_data,
        annot=True,
        cmap="YlGnBu",
        fmt=".1f",
        cbar_kws={'label': 'Avg Health Score'},
        ax=ax
    )
    ax.set_xlabel("State")
    ax.set_ylabel("Crop")
    return fig

def plot_pest_attack_rate(pest_rate_df):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=pest_rate_df,
        x="has_alert",
        y="pest_attack_rate_pct",
        palette="OrRd",
        ax=ax
    )
    ax.set_ylabel("Pest Attack Rate (%)")
    ax.set_xlabel("Weather Observation Alert Status")
    return fig

def plot_aqi_by_country(aqi_summary):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=aqi_summary,
        x="country",
        y="air_quality_index",
        palette="viridis",
        ax=ax
    )
    ax.set_ylabel("Average Air Quality Index (AQI)")
    ax.set_xlabel("Country")
    return fig

def plot_disaster_risk_heatmap(pivot_risk_pct):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(
        pivot_risk_pct,
        annot=True,
        cmap="Reds",
        fmt=".1f",
        cbar_kws={'label': 'Percentage of Observations (%)'},
        ax=ax
    )
    ax.set_xlabel("Disaster Risk Level")
    ax.set_ylabel("Climate Zone")
    return fig

def plot_evapotranspiration_trend(noaa_df):
    bins = [-20, 0, 10, 20, 30, 50]
    labels = ['Below 0°C', '0-10°C', '10-20°C', '20-30°C', 'Above 30°C']
    noaa_df['temp_range'] = pd.cut(noaa_df['avg_temperature_c'], bins=bins, labels=labels)

    summary = noaa_df.groupby('temp_range', observed=False)['evapotranspiration_mm'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=summary, x='temp_range', y='evapotranspiration_mm', palette='coolwarm', ax=ax)
    ax.set_xlabel("Temperature Range")
    ax.set_ylabel("Average Evaporation Rate (mm)")
    return fig

def plot_yield_gap_scatter(yield_df):
    sample_df = yield_df.sample(n=min(200, len(yield_df)), random_state=42)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        data=sample_df,
        x="expected_yield_tonnes",
        y="actual_yield_tonnes",
        hue="season",
        s=80,
        alpha=0.8,
        ax=ax
    )
    max_val = max(sample_df["expected_yield_tonnes"].max(), sample_df["actual_yield_tonnes"].max())
    ax.plot([0, max_val], [0, max_val], color='red', linestyle='--', label="Perfect Match Line")
    ax.set_xlabel("Expected Yield (Tonnes)")
    ax.set_ylabel("Actual Yield (Tonnes)")
    ax.legend(title="Season")
    return fig

def plot_aqi_by_precipitation(noaa_df):
    bins = [-1, 10, 30, 50, 100]
    labels = ['Dry (0-10mm)', 'Light Rain (10-30mm)', 'Moderate Rain (30-50mm)', 'Heavy Rain (50mm+)']
    noaa_df['precip_range'] = pd.cut(noaa_df['precipitation_mm'], bins=bins, labels=labels)

    summary = noaa_df.groupby('precip_range', observed=False)['air_quality_index'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=summary, x='precip_range', y='air_quality_index', palette='Blues', ax=ax)
    ax.set_xlabel("Amount of Rainfall")
    ax.set_ylabel("Average Air Quality Index (AQI)")
    return fig
