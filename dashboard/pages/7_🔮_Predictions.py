"""Page 7: Predictions (ML Podium Predictor, Elo Rating & Car vs Driver Skill Decoupling)."""

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
from dashboard.components.kpi_card import render_kpi_card, render_insight_box
from dashboard.components.styles import inject_f1_custom_css, render_f1_sidebar
from src.models.driver_ranking import DriverRankingModel
from src.models.race_prediction import RaceOutcomePredictor
from src.models.driver_clustering import DriverClusterer
from src.utils.helpers import apply_f1_plotly_theme, F1_COLORS

st.set_page_config(page_title="Predictions & Elo - F1 Platform", page_icon="🔮", layout="wide", initial_sidebar_state="expanded")
inject_f1_custom_css()
render_f1_sidebar()

master_df, driver_stats, constructor_stats, circuit_stats, data_dict = load_cached_data()
adv_data = load_advanced_analytics(master_df, data_dict)

driver_elo_hist = adv_data["driver_elo_hist"]
driver_peak_elo = adv_data["driver_peak_elo"]
pure_skill_df = adv_data["pure_skill_df"]
car_dominance_df = adv_data["car_dominance_df"]

st.title("🔮 Machine Learning, Elo Ratings & Car-Driver Decoupling")
st.markdown("Predict podium probabilities, track historical Elo ratings, and decouple pure driver skill from car performance.")

# Train Models with Cache
@st.cache_resource
def train_models():
    r_model = DriverRankingModel()
    r_metrics = r_model.fit(driver_stats)
    
    p_model = RaceOutcomePredictor()
    p_metrics = p_model.fit(master_df)
    
    c_model = DriverClusterer(n_clusters=4)
    clustered_df = c_model.fit_predict(driver_stats)
    
    return r_model, r_metrics, p_model, p_metrics, c_model, clustered_df

r_model, r_metrics, p_model, p_metrics, c_model, clustered_df = train_models()

tab1, tab2, tab3, tab4 = st.tabs([
    "🏁 Live Podium Predictor",
    "♟️ All-Time Elo Ratings",
    "⚖️ Skill vs. Car Decoupling",
    "🧩 Driver Archetype Clustering"
])

with tab1:
    st.subheader("🎯 Live Race Outcome / Podium Predictor")
    st.markdown("Input race parameters to estimate the probability of a **Top-3 Podium Finish**.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        grid_pos = st.number_input("Starting Grid Position:", min_value=1, max_value=24, value=1)
        recent_form = st.slider("Recent 3-Race Average Finish:", min_value=1.0, max_value=20.0, value=2.5, step=0.5)
    with col2:
        selected_team = st.selectbox("Constructor Team:", sorted(master_df["constructor_name"].dropna().unique()))
        c_id = master_df[master_df["constructor_name"] == selected_team]["constructorId"].iloc[0]
    with col3:
        selected_circuit = st.selectbox("Grand Prix Circuit:", sorted(master_df["circuit_name"].dropna().unique()))
        track_id = master_df[master_df["circuit_name"] == selected_circuit]["circuitId"].iloc[0]

    sample_input = {
        "grid": grid_pos,
        "year": 2024,
        "round": 10,
        "recent_avg_finish": recent_form,
        "circuitId": track_id,
        "constructorId": c_id,
    }

    podium_prob = p_model.predict_podium_proba(sample_input)

    st.markdown("---")
    res_col1, res_col2 = st.columns([1, 2])
    with res_col1:
        render_kpi_card("Predicted Podium Probability", f"{podium_prob*100.0:.1f}%", f"Grid {grid_pos} at {selected_circuit}", "#00D2BE" if podium_prob > 0.5 else "#E10600")
    with res_col2:
        st.markdown(f"**Model Performance Metrics (Random Forest Classifier)**:")
        st.write(f"- **ROC-AUC Score**: `{p_metrics['roc_auc']:.3f}`")
        st.write(f"- **Accuracy**: `{p_metrics['accuracy']*100:.1f}%`")
        st.write(f"- **Precision**: `{p_metrics['precision']*100:.1f}%` | **Recall**: `{p_metrics['recall']*100:.1f}%`")

with tab2:
    st.subheader("♟️ All-Time Peak F1 Elo Rating Leaderboard")
    st.markdown("Sequential pairwise Elo updates across all 1,100+ Grands Prix from 1950 to present.")

    if not driver_peak_elo.empty:
        col_e1, col_e2 = st.columns([3, 2])
        with col_e1:
            fig_elo = px.bar(
                driver_peak_elo.head(15),
                x="peak_elo",
                y="driver_name",
                orientation="h",
                color="peak_elo",
                color_continuous_scale="Reds",
                labels={"peak_elo": "All-Time Peak Elo Rating", "driver_name": "Driver"},
            )
            fig_elo.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(apply_f1_plotly_theme(fig_elo, "Peak Elo Leaderboard"), use_container_width=True)

        with col_e2:
            st.subheader("📈 Career Elo Trajectory Comparison")
            legend_drivers = ["Lewis Hamilton", "Michael Schumacher", "Ayrton Senna", "Max Verstappen"]
            sel_elo = driver_elo_hist[driver_elo_hist["driver_name"].isin(legend_drivers)]
            fig_traj = px.line(
                sel_elo,
                x="year",
                y="driver_elo",
                color="driver_name",
                labels={"year": "Season Year", "driver_elo": "Elo Rating", "driver_name": "Driver"}
            )
            st.plotly_chart(apply_f1_plotly_theme(fig_traj, "Elo Rating Trajectory Over Time"), use_container_width=True)

with tab3:
    st.subheader("⚖️ Pure Driver Skill vs Car Dominance Decoupling")
    st.markdown("Using Ridge linear regression with teammate crossover constraints to separate car performance from driver talent.")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.subheader("🏎️ Top 15 Pure Driver Skill Index (Car-Independent)")
        if not pure_skill_df.empty:
            fig_skill = px.bar(
                pure_skill_df.head(15),
                x="driver_skill_normalized",
                y="driver_name",
                orientation="h",
                color="driver_skill_normalized",
                color_continuous_scale="Teal",
                labels={"driver_skill_normalized": "Pure Skill Index (0-100)", "driver_name": "Driver"}
            )
            fig_skill.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(apply_f1_plotly_theme(fig_skill, "Car-Independent Skill Index"), use_container_width=True)

    with col_d2:
        st.subheader("🏎️ Top Dominant Car Seasons")
        if not car_dominance_df.empty:
            fig_car = px.bar(
                car_dominance_df.head(15),
                x="car_dominance_index",
                y="car_season",
                orientation="h",
                color="car_dominance_index",
                color_continuous_scale="Reds",
                labels={"car_dominance_index": "Car Dominance Score", "car_season": "Team Season"}
            )
            fig_car.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(apply_f1_plotly_theme(fig_car, "Most Dominant Car Seasons"), use_container_width=True)

with tab4:
    st.subheader("🧩 Driver Career Archetype Clustering (K-Means)")
    
    fig_cluster = px.scatter(
        clustered_df,
        x="win_rate",
        y="driver_performance_score",
        color="cluster_archetype",
        size="wins",
        hover_name="driver_name",
        hover_data=["championships", "podiums", "total_starts"],
        color_discrete_map={
            "🏆 Championship Legend": F1_COLORS["gold"],
            "🥇 Consistent Podium Contender": F1_COLORS["cyan"],
            "🏎️ Mid-Field Workhorse": F1_COLORS["orange"],
            "🏁 Short-Career / One-Season": F1_COLORS["text_secondary"],
        },
        labels={"win_rate": "Career Win Rate", "driver_performance_score": "Driver Performance Score"},
    )
    st.plotly_chart(apply_f1_plotly_theme(fig_cluster, "K-Means 4-Archetype Driver Clusters"), use_container_width=True)
