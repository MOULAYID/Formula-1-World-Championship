"""Page 2: Drivers (Driver Performance & GOAT Radar Comparison)."""

import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dashboard.data_loader import load_cached_data
from dashboard.components.charts import build_driver_radar_chart, build_goat_scatter_matrix
from dashboard.components.kpi_card import render_insight_box
from dashboard.components.styles import inject_f1_custom_css
from src.utils.helpers import apply_f1_plotly_theme, F1_COLORS, get_driver_flag_url

inject_f1_custom_css()

master_df, driver_stats, _, _, _ = load_cached_data()

st.title("🏎️ Driver Performance & GOAT Analysis")
st.markdown("Statistically evaluating driver greatness, career consistency, and teammate head-to-head records.")

# Filters
col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    default_legends = ["Lewis Hamilton", "Michael Schumacher", "Ayrton Senna", "Max Verstappen", "Fernando Alonso"]
    all_drivers = sorted(driver_stats["driver_name"].tolist())
    selected_drivers = st.multiselect(
        "Select Drivers to Compare (Radar & Trajectory):",
        options=all_drivers,
        default=default_legends[:4],
    )
with col_f2:
    min_starts_filter = st.slider("Minimum Career Starts Threshold:", min_value=10, max_value=100, value=20, step=10)

filtered_stats = driver_stats[driver_stats["total_starts"] >= min_starts_filter].copy()

# Scatter Matrix
st.subheader("📊 The GOAT Matrix: Driver Performance Score (DPS) vs Win Rate")
fig_goat = build_goat_scatter_matrix(filtered_stats)
st.plotly_chart(fig_goat, use_container_width=True)

# Radar Chart
if selected_drivers:
    st.subheader("🎯 Driver Radar Profile Comparison")
    fig_radar = build_driver_radar_chart(driver_stats, selected_drivers)
    st.plotly_chart(fig_radar, use_container_width=True)

# Career Cumulative Wins Trajectory
st.subheader("📈 Cumulative Race Wins Trajectory by Race Starts")
if selected_drivers:
    sel_ids = driver_stats[driver_stats["driver_name"].isin(selected_drivers)]["driverId"].tolist()
    traj_df = master_df[master_df["driverId"].isin(sel_ids)].sort_values(["driverId", "race_date"])
    traj_df["career_race_num"] = traj_df.groupby("driverId").cumcount() + 1
    traj_df["cumulative_wins"] = traj_df.groupby("driverId")["is_win"].cumsum()

    fig_traj = px.line(
        traj_df,
        x="career_race_num",
        y="cumulative_wins",
        color="driver_name",
        labels={"career_race_num": "Career Race Start #", "cumulative_wins": "Cumulative Wins", "driver_name": "Driver"},
        color_discrete_sequence=px.colors.qualitative.Set1,
    )
    st.plotly_chart(apply_f1_plotly_theme(fig_traj, "Race Wins Accumulation Pace", height=450), use_container_width=True)

# Leaderboard Table
st.subheader("🏆 Driver Performance Score (DPS) Leaderboard")
display_cols = [
    "driver_name", "driver_nationality", "championships", "wins", "podiums", "poles",
    "total_starts", "win_rate", "podium_rate", "teammate_h2h_win_rate", "driver_performance_score"
]
table_df = filtered_stats[display_cols].head(25).copy()
table_df["win_rate"] = (table_df["win_rate"] * 100).map("{:.1f}%".format)
table_df["podium_rate"] = (table_df["podium_rate"] * 100).map("{:.1f}%".format)
table_df["teammate_h2h_win_rate"] = (table_df["teammate_h2h_win_rate"] * 100).map("{:.1f}%".format)
table_df["flag"] = table_df["driver_nationality"].apply(get_driver_flag_url)
table_df["driver"] = table_df["flag"] + " " + table_df["driver_name"]

st.dataframe(
    table_df[["driver", "championships", "wins", "podiums", "poles", "total_starts", "win_rate", "podium_rate", "teammate_h2h_win_rate", "driver_performance_score"]].rename(
        columns={
            "driver": "Driver",
            "championships": "Titles",
            "wins": "Wins",
            "podiums": "Podiums",
            "poles": "Poles",
            "total_starts": "Starts",
            "win_rate": "Win %",
            "podium_rate": "Podium %",
            "teammate_h2h_win_rate": "Teammate H2H %",
            "driver_performance_score": "DPS Rating",
        }
    ),
    use_container_width=True,
    height=400,
)

render_insight_box(
    "The Driver Performance Score (DPS) normalizes career wins, podiums, championships, and teammate head-to-head battles to isolate driver talent across 70+ years of changing calendar lengths and points scoring rules.",
    title="GOAT MODEL METHODOLOGY"
)
