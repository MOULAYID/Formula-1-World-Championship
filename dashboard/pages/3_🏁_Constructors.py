"""Page 3: Constructors (Team Dominance & Era Analytics)."""

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
from dashboard.components.charts import build_era_win_share_chart
from dashboard.components.kpi_card import render_insight_box
from dashboard.components.styles import inject_f1_custom_css
from src.utils.helpers import apply_f1_plotly_theme, F1_COLORS

inject_f1_custom_css()

master_df, _, constructor_stats, _, _ = load_cached_data()

st.title("🏁 Constructor Analytics & Era Dominance")
st.markdown("Examining team efficiency, era market share, and mechanical reliability over 7 decades.")

# Era Win Share Chart
st.subheader("📊 Dominant Eras: Constructor Race Wins Share")
fig_era = build_era_win_share_chart(master_df)
st.plotly_chart(fig_era, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top Constructors by Race Wins")
    top_teams = constructor_stats.head(10)
    fig_wins = px.bar(
        top_teams,
        x="wins",
        y="constructor_name",
        orientation="h",
        color="wins",
        color_continuous_scale="Reds",
        labels={"wins": "Total Wins", "constructor_name": "Team"},
    )
    fig_wins.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(apply_f1_plotly_theme(fig_wins, "All-Time Constructor Wins"), use_container_width=True)

with col2:
    st.subheader("⚙️ Mechanical Reliability Score (%)")
    fig_rel = px.scatter(
        constructor_stats[constructor_stats["race_starts"] >= 30],
        x="points_per_start",
        y="reliability_score",
        size="wins",
        hover_name="constructor_name",
        color="reliability_score",
        color_continuous_scale="Teal",
        labels={"points_per_start": "Points per Race Start", "reliability_score": "Reliability Score (%)"},
    )
    st.plotly_chart(apply_f1_plotly_theme(fig_rel, "Team Points Efficiency vs Reliability"), use_container_width=True)

# Table
st.subheader("📋 Constructor Performance Matrix")
st.dataframe(
    constructor_stats[["constructor_name", "constructor_nationality", "wins", "podiums", "race_starts", "win_rate", "reliability_score"]].head(15).rename(
        columns={
            "constructor_name": "Team",
            "constructor_nationality": "Country",
            "wins": "Total Wins",
            "podiums": "Podiums",
            "race_starts": "Race Starts",
            "win_rate": "Win Rate",
            "reliability_score": "Reliability %",
        }
    ),
    use_container_width=True,
)

render_insight_box(
    "Ferrari, McLaren, Mercedes, Red Bull, Williams, and Lotus account for over 75% of all Grands Prix wins in history. Team dominance is highly era-dependent: Mercedes dominated 2014–2020 (74% win rate), Red Bull dominated 2010–2013 and 2022–2023, while Ferrari dominated the early 2000s.",
    title="CONSTRUCTOR ERA INSIGHT"
)
