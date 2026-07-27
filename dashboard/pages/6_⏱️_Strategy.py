"""Page 6: Strategy (Pit Stop Pace & Reliability Analysis)."""

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
from dashboard.components.kpi_card import render_insight_box
from dashboard.components.styles import inject_f1_custom_css
from src.utils.helpers import apply_f1_plotly_theme, F1_COLORS

inject_f1_custom_css()

master_df, _, constructor_stats, _, data_dict = load_cached_data()
pit_stops_df = data_dict.get("pit_stops")

st.title("⏱️ Strategy & Reliability Analytics")
st.markdown("Pit stop execution speed, strategy windows, and mechanical DNF reliability trends.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🍩 Overall Race Result Status Breakdown")
    dnf_counts = master_df["dnf_category"].value_counts().reset_index()
    dnf_counts.columns = ["category", "count"]

    fig_pie = px.pie(
        dnf_counts,
        names="category",
        values="count",
        hole=0.45,
        color="category",
        color_discrete_map={
            "Finished": "#00D2BE",
            "Mechanical DNF": "#E10600",
            "Accident / Collision DNF": "#FF8700",
            "Other Retirement": "#94A3B8",
            "Disqualified": "#FFD700"
        }
    )
    st.plotly_chart(apply_f1_plotly_theme(fig_pie, "F1 Race Status Breakdown (70+ Years)"), use_container_width=True)

with col2:
    st.subheader("⚙️ DNF Causes Rate Across F1 Eras")
    era_dnf = master_df.groupby("era").agg(
        mechanical_dnf_rate=("is_mechanical_dnf", "mean"),
        accident_dnf_rate=("is_accident_dnf", "mean"),
    ).reset_index()
    era_dnf["mechanical_dnf_rate"] *= 100.0
    era_dnf["accident_dnf_rate"] *= 100.0

    fig_era_dnf = px.bar(
        era_dnf,
        x="era",
        y=["mechanical_dnf_rate", "accident_dnf_rate"],
        barmode="group",
        labels={"value": "DNF Rate (%)", "variable": "Cause", "era": "Era"},
        color_discrete_map={
            "mechanical_dnf_rate": F1_COLORS["red"],
            "accident_dnf_rate": F1_COLORS["orange"],
        }
    )
    st.plotly_chart(apply_f1_plotly_theme(fig_era_dnf, "Mechanical vs Accident DNF Rate by Era"), use_container_width=True)

# Pit stop duration analysis if available
if pit_stops_df is not None and not pit_stops_df.empty:
    st.subheader("⏱️ Pit Stop Duration Evolution (2011–Present)")
    pits_clean = pit_stops_df.copy()
    pits_clean["seconds"] = pd.to_numeric(pits_clean["duration"], errors="coerce")
    pits_clean = pits_clean[(pits_clean["seconds"] > 1.5) & (pits_clean["seconds"] < 45.0)]
    
    # Merge with race year
    races_min = master_df[["raceId", "year", "constructor_name"]].drop_duplicates()
    pits_merged = pits_clean.merge(races_min, on="raceId", how="left")

    fig_pits = px.box(
        pits_merged,
        x="year",
        y="seconds",
        color_discrete_sequence=[F1_COLORS["cyan"]],
        labels={"year": "Season Year", "seconds": "Pit Stop Duration (s)"},
    )
    st.plotly_chart(apply_f1_plotly_theme(fig_pits, "Pit Stop Stationary Duration Distribution"), use_container_width=True)

render_insight_box(
    "In the 1950s–1970s, over 40% of grid starters suffered mechanical failures due to engine reliability limits. In modern hybrid F1 (2014–present), mechanical DNF rates fell below 6%, making pit stop strategy and tyre preservation key differentiators.",
    title="RELIABILITY EVOLUTION INSIGHT"
)
