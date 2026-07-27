"""Page 6: Strategy (Pit Stop Pace, Tyre Degradation & Undercut Analysis)."""

import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dashboard.data_loader import load_cached_data, load_advanced_analytics
from dashboard.components.kpi_card import render_insight_box
from dashboard.components.styles import inject_f1_custom_css, render_f1_sidebar
from src.utils.helpers import apply_f1_plotly_theme, F1_COLORS

st.set_page_config(page_title="Strategy Analytics - F1 Platform", page_icon="⏱️", layout="wide", initial_sidebar_state="expanded")
inject_f1_custom_css()
render_f1_sidebar()

master_df, _, constructor_stats, _, data_dict = load_cached_data()
adv_data = load_advanced_analytics(master_df, data_dict)
deg_df = adv_data["deg_df"]
undercut_df = adv_data["undercut_df"]
pit_stops_df = data_dict.get("pit_stops")

st.title("⏱️ Strategy, Tyre Degradation & Undercut Analytics")
st.markdown("Pit stop execution speed, stint tyre degradation slopes, and undercut vs overcut strategy success rates.")

tab1, tab2, tab3 = st.tabs(["🍩 DNF & Reliability Breakdown", "🏎️ Tyre Degradation Slopes", "⏱️ Undercut vs Overcut Strategy"])

with tab1:
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

with tab2:
    st.subheader("📊 Average Tyre Degradation Slopes by Constructor")
    st.markdown("Quantifying average lap time loss per lap ($\text{sec/lap}$) due to tyre degradation.")

    if not deg_df.empty:
        avg_deg = deg_df.groupby("constructor_name").agg(
            avg_degradation_sec_per_lap=("degradation_sec_per_lap", "mean"),
            stints_analyzed=("stint_length", "count")
        ).reset_index()
        avg_deg = avg_deg[avg_deg["stints_analyzed"] >= 5].sort_values("avg_degradation_sec_per_lap")

        fig_deg = px.bar(
            avg_deg.head(12),
            x="avg_degradation_sec_per_lap",
            y="constructor_name",
            orientation="h",
            color="avg_degradation_sec_per_lap",
            color_continuous_scale="Reds",
            labels={"avg_degradation_sec_per_lap": "Tyre Degradation Slope (s/lap)", "constructor_name": "Constructor"},
        )
        fig_deg.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(apply_f1_plotly_theme(fig_deg, "Tyre Degradation Slope (Lower is Better)"), use_container_width=True)
    else:
        st.info("Lap time degradation analysis loading...")

with tab3:
    st.subheader("⏱️ Undercut vs. Overcut Strategy Win Rates")
    st.markdown("Evaluating whether pitting 1–3 laps before a direct competitor (Undercut) yields track position gain.")

    if not undercut_df.empty:
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            success_rate = undercut_df["is_undercut_successful"].mean() * 100.0
            st.metric("Overall Undercut Success Rate", f"{success_rate:.1f}%")
            
            fig_undercut = px.pie(
                undercut_df,
                names="is_undercut_successful",
                title="Undercut Strategy Outcome",
                color_discrete_sequence=["#00D2BE", "#E10600"]
            )
            st.plotly_chart(apply_f1_plotly_theme(fig_undercut, "Undercut Success Share"), use_container_width=True)

        with col_u2:
            lap_delta_df = undercut_df.groupby("lap_delta")["is_undercut_successful"].mean().reset_index()
            lap_delta_df["is_undercut_successful"] *= 100.0
            fig_delta = px.bar(
                lap_delta_df,
                x="lap_delta",
                y="is_undercut_successful",
                labels={"lap_delta": "Lap Delta Between Pit Stops", "is_undercut_successful": "Success Rate (%)"},
                color="is_undercut_successful",
                color_continuous_scale="Teal"
            )
            st.plotly_chart(apply_f1_plotly_theme(fig_delta, "Undercut Success by Lap Gap"), use_container_width=True)
