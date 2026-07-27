"""Page 4: Circuits (Circuit Map & Track Difficulty Analytics)."""

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
from dashboard.components.charts import build_circuits_map
from dashboard.components.kpi_card import render_insight_box
from dashboard.components.styles import inject_f1_custom_css
from src.utils.helpers import apply_f1_plotly_theme, F1_COLORS

inject_f1_custom_css()

_, _, _, circuit_stats, _ = load_cached_data()

st.title("🗺️ Circuit Analytics & Track Characteristics")
st.markdown("Global venue mapping, Circuit Difficulty Score (CDS), and qualifying-to-win conversion rates.")

# Map
st.subheader("🌐 Global F1 Circuits Interactive Map")
fig_map = build_circuits_map(circuit_stats)
st.plotly_chart(fig_map, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏎️ Top 10 Circuits by Difficulty Score (CDS)")
    top_diff = circuit_stats.sort_values(by="circuit_difficulty_score", ascending=False).head(10)
    fig_cds = px.bar(
        top_diff,
        x="circuit_difficulty_score",
        y="circuit_name",
        orientation="h",
        color="circuit_difficulty_score",
        color_continuous_scale="OrRd",
        labels={"circuit_difficulty_score": "Difficulty Score (CDS)", "circuit_name": "Circuit"},
    )
    fig_cds.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(apply_f1_plotly_theme(fig_cds, "Circuit Difficulty Index"), use_container_width=True)

with col2:
    st.subheader("🚩 Pole Position Win Conversion Rate (%)")
    pole_df = circuit_stats[circuit_stats["total_races"] >= 10].sort_values(by="pole_win_rate", ascending=False).head(10)
    fig_pole = px.bar(
        pole_df,
        x="pole_win_rate",
        y="circuit_name",
        orientation="h",
        color="pole_win_rate",
        color_continuous_scale="Greens",
        labels={"pole_win_rate": "Pole Win Rate", "circuit_name": "Circuit"},
    )
    fig_pole.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(apply_f1_plotly_theme(fig_pole, "Tracks Where Pole Predicts Victory"), use_container_width=True)

render_insight_box(
    "Monaco, Singapore, and Hungaroring feature high Pole Win Rates (>55%), where track position is critical due to overtaking difficulty. High-speed power circuits (Monza, Spa-Francorchamps) feature higher position variances and overtake counts.",
    title="CIRCUIT DYNAMICS INSIGHT"
)
