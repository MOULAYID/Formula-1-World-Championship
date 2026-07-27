"""Page 5: Race Analytics (Qualifying vs Race Performance)."""

import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dashboard.data_loader import load_cached_data
from dashboard.components.charts import build_grid_vs_finish_scatter
from dashboard.components.kpi_card import render_insight_box
from dashboard.components.styles import inject_f1_custom_css
from src.utils.helpers import apply_f1_plotly_theme, F1_COLORS

inject_f1_custom_css()

master_df, driver_stats, _, _, _ = load_cached_data()

st.title("📊 Race Analytics: Qualifying vs. Race Performance")
st.markdown("Analyzing qualifying correlation to victory, grid position changes, and overtake recoveries.")

# Scatter Plot
st.subheader("🎯 Grid Position vs. Final Race Position Scatter")
fig_scatter = build_grid_vs_finish_scatter(master_df)
st.plotly_chart(fig_scatter, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Highest Average Positions Gained per Race")
    top_gained = master_df.groupby(["driverId", "driver_name"]).agg(
        starts=("resultId", "count"),
        avg_gained=("positions_gained", "mean"),
        total_gained=("positions_gained", "sum")
    ).reset_index()
    top_gained = top_gained[top_gained["starts"] >= 30].sort_values(by="avg_gained", ascending=False).head(10)

    fig_gain = px.bar(
        top_gained,
        x="avg_gained",
        y="driver_name",
        orientation="h",
        color="avg_gained",
        color_continuous_scale="Viridis",
        labels={"avg_gained": "Avg Positions Gained / Race", "driver_name": "Driver"},
    )
    fig_gain.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(apply_f1_plotly_theme(fig_gain, "Master Overtakers & Recovery Drivers"), use_container_width=True)

with col2:
    st.subheader("🏁 Race Winners Starting Grid Distribution")
    win_grid = master_df[master_df["is_win"] == 1]["grid"].value_counts().reset_index()
    win_grid.columns = ["grid_start", "win_count"]
    win_grid = win_grid[win_grid["grid_start"] > 0].sort_values(by="grid_start").head(10)

    fig_win_grid = px.bar(
        win_grid,
        x="grid_start",
        y="win_count",
        color="win_count",
        color_continuous_scale="Reds",
        labels={"grid_start": "Grid Position Start", "win_count": "Total Race Wins"},
    )
    st.plotly_chart(apply_f1_plotly_theme(fig_win_grid, "Starting Grid of Race Winners"), use_container_width=True)

render_insight_box(
    "Over 45% of all Formula 1 races in history are won from Pole Position (Grid 1), and over 75% are won from the front row (Grid 1 & 2). Winning from outside the top 10 requires extraordinary race pace, rain conditions, or safety car luck.",
    title="QUALIFYING CONVERSION INSIGHT"
)
