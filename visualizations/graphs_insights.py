"""Charts added on top of the ones the original specification asked for.

The specified charts are kept in graphs.py exactly as required. Several of them
turned out to plot variables that are statistically independent in this dataset,
so these companions sit beside them and show the relationships that do exist.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def _paired_bars(summary, x_col, metrics, x_label, palette):
    """Two side-by-side bar panels sharing one x category.

    metrics is [(column, y_label), (column, y_label)]. Used wherever we compare
    a category against two measures that live on different scales (e.g. a 0-100
    score next to a tonnage), which a single axis would render unreadable.
    """
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, (col, y_label) in zip(axes, metrics):
        sns.barplot(data=summary, x=x_col, y=col, hue=x_col, palette=palette, legend=False, ax=ax)
        ax.axhline(0, color="gray", linewidth=0.8)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
    fig.tight_layout()
    return fig


def plot_profit_trend(merged_df, x_col, x_label, crops):
    """Mean profit across quantile bins of x_col, one line per selected crop."""
    fig, ax = plt.subplots(figsize=(10, 5))

    for crop in crops:
        sub = merged_df[merged_df["crop"] == crop]
        if sub.empty:
            continue
        # Quantile bins keep each point backed by a similar number of farms,
        # so a line never swings wildly on the strength of one outlier.
        binned = pd.qcut(sub[x_col], q=5, duplicates="drop")
        summary = sub.groupby(binned, observed=True)["profit_loss_inr"].mean()
        ax.plot([b.mid for b in summary.index], summary.values, marker="o", label=crop)

    ax.axhline(0, color="red", linestyle="--", alpha=0.5, label="Break-even")
    ax.set_xlabel(x_label)
    ax.set_ylabel("Average Profit / Loss (INR)")
    ax.legend(title="Crop", fontsize=8)
    return fig


def plot_pest_impact(summary):
    return _paired_bars(
        summary,
        "pest_attack",
        [("crop_health_score", "Avg Crop Health Score"), ("yield_gap_tonnes", "Avg Yield Gap (Tonnes)")],
        "Pest Attack Occurred",
        palette="RdYlGn_r",
    )


def plot_drought_profile(summary):
    return _paired_bars(
        summary,
        "drought_index",
        [("soil_moisture_percent", "Avg Soil Moisture (%)"), ("precipitation_mm", "Avg Precipitation (mm)")],
        "Drought Index",
        palette="YlOrBr",
    )


def plot_env_correlation_heatmap(noaa_df):
    """Correlation matrix of the NOAA environmental measures."""
    cols = [
        "avg_temperature_c", "evapotranspiration_mm", "precipitation_mm",
        "humidity_percent", "soil_moisture_percent", "air_quality_index", "pm25", "pm10",
    ]
    corr = noaa_df[cols].corr()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        corr,
        mask=np.triu(np.ones_like(corr, dtype=bool)),  # upper half mirrors the lower, so hide it
        annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1,
        linewidths=0.5, cbar_kws={"label": "Correlation (r)"}, ax=ax,
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    return fig
