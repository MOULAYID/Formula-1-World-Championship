"""Page 2: Drivers (Driver Performance, GOAT Radar & Rain Master Analysis)."""

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

from dashboard.data_loader import load_cached_data, load_advanced_analytics
from dashboard.components.charts import build_driver_radar_chart, build_goat_scatter_matrix
from dashboard.components.kpi_card import render_insight_box
from dashboard.components.styles import inject_f1_custom_css, render_f1_sidebar
from src.utils.helpers import apply_f1_plotly_theme, F1_COLORS, get_driver_flag_url

st.set_page_config(page_title="Driver Performance - F1 Platform", page_icon="🏎️", layout="wide", initial_sidebar_state="expanded")
inject_f1_custom_css()
render_f1_sidebar()

master_df, driver_stats, _, _, data_dict = load_cached_data()
adv_data = load_advanced_analytics(master_df, data_dict)
rain_master_df = adv_data["rain_master_df"]

st.title("🏎️ Driver Performance & Rain Master Analysis")
st.markdown("Statistically evaluating driver greatness, career consistency, rain performance, and teammate head-to-head records.")

tab_goat, tab_rain = st.tabs(["🏆 GOAT Matrix & Leaderboards", "🌧️ Rain Master & Wet Weather Performance"])

with tab_goat:
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
        height=380,
    )

with tab_rain:
    st.subheader("🌧️ All-Time Rain Master Rating (Wet Weather Specialists)")
    st.markdown("Evaluating driver win rates, podiums, and position gains in wet/rain-affected Grands Prix.")

    if not rain_master_df.empty:
        col_r1, col_r2 = st.columns([3, 2])
        with col_r1:
            fig_rain = px.bar(
                rain_master_df.head(15),
                x="rain_master_score",
                y="driver_name",
                orientation="h",
                color="rain_master_score",
                color_continuous_scale="Blues",
                labels={"rain_master_score": "Rain Master Index (0-100)", "driver_name": "Driver"},
            )
            fig_rain.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(apply_f1_plotly_theme(fig_rain, "Rain Master Leaderboard"), use_container_width=True)

        with col_r2:
            st.subheader("📊 Wet vs. Dry Win Rate Delta")
            fig_delta = px.scatter(
                rain_master_df.head(20),
                x="dry_win_rate",
                y="wet_win_rate",
                size="wet_wins",
                color="rain_master_score",
                hover_name="driver_name",
                labels={"dry_win_rate": "Dry Race Win Rate", "wet_win_rate": "Wet Race Win Rate"},
                color_continuous_scale="Viridis",
            )
            st.plotly_chart(apply_f1_plotly_theme(fig_delta, "Wet vs Dry Win Rate Scatter"), use_container_width=True)

        render_insight_box(
            "Drivers like Ayrton Senna, Michael Schumacher, Lewis Hamilton, and Max Verstappen exhibit higher win rates in rain than in dry conditions, demonstrating superior car control when mechanical car dominance is neutralized.",
            title="RAIN MASTER INSIGHT"
        )
