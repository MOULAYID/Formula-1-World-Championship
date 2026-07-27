"""Page 1: Home (Executive Overview)."""

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
from dashboard.components.kpi_card import render_kpi_card, render_insight_box
from dashboard.components.styles import inject_f1_custom_css
from src.utils.helpers import apply_f1_plotly_theme, F1_COLORS

inject_f1_custom_css()

master_df, driver_stats, constructor_stats, circuit_stats, _ = load_cached_data()

st.title("🏠 Executive Overview: 70+ Years of Formula 1")
st.markdown("Macro-level statistics, historical timeline evolution, and executive KPIs.")

# Executive KPI Grid (9 KPIs across 3 rows)
row1_col1, row1_col2, row1_col3 = st.columns(3)
with row1_col1:
    render_kpi_card("Total Championships", "74", "1950 - Present Seasons", "#FFD700")
with row1_col2:
    render_kpi_card("Total Grands Prix", f"{master_df['raceId'].nunique():,}", "Races Held", "#E10600")
with row1_col3:
    render_kpi_card("Total Drivers", f"{master_df['driverId'].nunique():,}", "Historical Entrants", "#00D2BE")

row2_col1, row2_col2, row2_col3 = st.columns(3)
with row2_col1:
    render_kpi_card("Total Constructors", f"{master_df['constructorId'].nunique():,}", "Teams / Manufacturers", "#FF8700")
with row2_col2:
    render_kpi_card("Total Circuits", f"{master_df['circuitId'].nunique():,}", "Global Racing Venues", "#005AFF")
with row2_col3:
    render_kpi_card("Total Countries", f"{master_df['circuit_country'].nunique():,}", "Host Nations", "#DC0000")

row3_col1, row3_col2, row3_col3 = st.columns(3)
with row3_col1:
    render_kpi_card("Total Race Entries", f"{len(master_df):,}", "Individual Start Results", "#E10600")
with row3_col2:
    render_kpi_card("Average Grid Gain", f"{master_df['positions_gained'].mean():+.2f}", "Positions Gained per Race", "#00D2BE")
with row3_col3:
    render_kpi_card("Average Finish Pos", f"{master_df['positionOrder'].mean():.1f}", "Average Position Across All Eras", "#FFD700")

st.divider()

# Historical F1 Calendar & Winners Evolution Line Chart
st.subheader("📈 Evolution of Formula 1: Races & Unique Winners Per Season")
season_stats = master_df.groupby("year").agg(
    total_races=("raceId", "nunique"),
    unique_winners=("driverId", lambda x: master_df.loc[x.index][master_df.loc[x.index, "is_win"] == 1]["driverId"].nunique()),
    unique_winning_teams=("constructorId", lambda x: master_df.loc[x.index][master_df.loc[x.index, "is_win"] == 1]["constructorId"].nunique())
).reset_index()

fig_evo = px.line(
    season_stats,
    x="year",
    y=["total_races", "unique_winners", "unique_winning_teams"],
    labels={"year": "Season Year", "value": "Count", "variable": "Metric"},
    color_discrete_map={
        "total_races": F1_COLORS["red"],
        "unique_winners": F1_COLORS["cyan"],
        "unique_winning_teams": F1_COLORS["gold"]
    }
)
st.plotly_chart(apply_f1_plotly_theme(fig_evo, "Season Expansion & Winners (1950–Present)"), use_container_width=True)

render_insight_box(
    "Formula 1 expanded from 7 races in 1950 to over 22+ races annually in the modern era. While calendar length grew exponentially, competitive tightness varied greatly — eras like 1982 and 2012 saw up to 7-11 unique winners in a single season, compared to hybrid-era dominance.",
    title="EXECUTIVE EVOLUTION INSIGHT"
)
