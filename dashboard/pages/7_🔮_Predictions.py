"""Page 7: Predictions (ML Driver Ranking & Podium Predictor)."""

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
from src.models.driver_ranking import DriverRankingModel
from src.models.race_prediction import RaceOutcomePredictor
from src.models.driver_clustering import DriverClusterer
from src.utils.helpers import apply_f1_plotly_theme, F1_COLORS

inject_f1_custom_css()

master_df, driver_stats, constructor_stats, circuit_stats, _ = load_cached_data()

st.title("🔮 Machine Learning Predictions & Clustering")
st.markdown("Predict podium probabilities, analyze feature importance, and explore driver career archetypes.")

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

tab1, tab2, tab3 = st.tabs(["🏁 Interactive Podium Predictor", "📊 Feature Importance & DPS", "🧩 Driver Archetype Clustering"])

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
    st.subheader("📊 Driver Performance Score - Model Feature Importance")
    fi_df = r_model.feature_importances_
    fig_fi = px.bar(
        fi_df,
        x="importance",
        y="feature",
        orientation="h",
        color="importance",
        color_continuous_scale="Reds",
        labels={"importance": "Relative Feature Importance", "feature": "Stat Metric"},
    )
    fig_fi.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(apply_f1_plotly_theme(fig_fi, "Key Factors Driving Driver Performance Score"), use_container_width=True)

with tab3:
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

    st.markdown("### 📋 Cluster Archetype Profiles")
    centroids = c_model.get_cluster_centroids(clustered_df)
    centroids["avg_win_rate"] = (centroids["avg_win_rate"] * 100).map("{:.1f}%".format)
    centroids["avg_dps"] = centroids["avg_dps"].map("{:.1f}".format)
    centroids["avg_wins"] = centroids["avg_wins"].map("{:.1f}".format)
    centroids["avg_podiums"] = centroids["avg_podiums"].map("{:.1f}".format)
    
    st.dataframe(
        centroids.rename(columns={
            "cluster_archetype": "Archetype",
            "count": "Driver Count",
            "avg_dps": "Avg DPS Rating",
            "avg_wins": "Avg Wins",
            "avg_podiums": "Avg Podiums",
            "avg_win_rate": "Avg Win %",
            "avg_starts": "Avg Starts",
        }),
        use_container_width=True,
    )
