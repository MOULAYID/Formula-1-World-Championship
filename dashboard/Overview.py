"""Formula 1 Performance Intelligence Platform - Main Streamlit Entrypoint (Overview)."""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

# Setup Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dashboard.data_loader import load_cached_data
from dashboard.components.styles import inject_f1_custom_css
from dashboard.components.kpi_card import render_kpi_card, render_insight_box

# Configure Page - Overview Title
st.set_page_config(
    page_title="Overview - F1 Performance Intelligence Platform",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Custom CSS
inject_f1_custom_css()

# Load Data
try:
    master_df, driver_stats, constructor_stats, circuit_stats, data_dict = load_cached_data()
except Exception as e:
    st.error(f"Error loading datasets from data/ directory: {e}")
    st.stop()

# Header Banner - Overview Title
st.markdown(
    """
    <div class="f1-header-title">
        🏎️ FORMULA 1 <span class="f1-header-accent">INTELLIGENCE OVERVIEW</span>
    </div>
    <div class="f1-subtitle">
        Enterprise Performance Analytics, Statistical Modeling & Machine Learning (1950–Present)
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar Navigation Info
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/3/33/F1.svg", width=120)
    st.markdown("### 🏎️ **F1 Intelligence Nav**")
    st.markdown("Select a page above to explore performance analytics.")
    st.divider()
    st.caption("Data Source: Kaggle F1 World Championship Dataset (1950–Present)")
    st.caption("Built with Python, Scikit-Learn, Plotly & Streamlit")

# Overview KPIs
col1, col2, col3 = st.columns(3)
with col1:
    render_kpi_card("Total Grands Prix", f"{master_df['raceId'].nunique():,}", "Races across 70+ years", "#E10600")
with col2:
    render_kpi_card("Total Drivers", f"{master_df['driverId'].nunique():,}", "Unique driver starts", "#00D2BE")
with col3:
    render_kpi_card("Total Constructors", f"{master_df['constructorId'].nunique():,}", "Chassis / Engine Teams", "#FFD700")

st.divider()

# DATASET STATISTICS & OVERVIEW SECTION
st.subheader("📊 Dataset Statistics & Relational Architecture")
st.markdown("Detailed breakdown of the 14 relational dataset tables gathered in `data/` from the Kaggle F1 World Championship Dataset:")

# Compute stats for each table
table_info = []
for name, df in data_dict.items():
    table_info.append({
        "Table Name": f"{name}.csv",
        "Row Count": f"{len(df):,}",
        "Column Count": len(df.columns),
        "Memory Size": f"{df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB",
        "Primary Keys / Identifiers": ", ".join([c for c in df.columns if "Id" in c or c in ["year", "lap", "stop"]][:3]),
    })

df_table_stats = pd.DataFrame(table_info)

col_d1, col_d2 = st.columns([3, 2])
with col_d1:
    st.dataframe(df_table_stats, use_container_width=True, height=360)

with col_d2:
    st.markdown("#### 🎯 Dataset Coverage Statistics:")
    st.write(f"- **Historical Span**: `1950` to `Present` (74 Seasons)")
    st.write(f"- **Master Data Entries**: `{len(master_df):,}` race result starts")
    st.write(f"- **Total Recorded Laps**: `{len(data_dict.get('lap_times', [])):,}` individual lap records")
    st.write(f"- **Total Pit Stops Recorded**: `{len(data_dict.get('pit_stops', [])):,}` pit stop events")
    st.write(f"- **Qualifying Sessions**: `{len(data_dict.get('qualifying', [])):,}` qualifying results")
    st.write(f"- **Overall DNF Rate**: `{master_df['is_dnf'].mean()*100:.1f}%` of race starts ended in retirement")
    st.write(f"- **Mechanical Failure Rate**: `{master_df['is_mechanical_dnf'].mean()*100:.1f}%` of starts")

render_insight_box(
    "This platform applies sports data science to decouple driver skill from car dominance, predict podium probabilities, cluster driver career archetypes, and analyze pit-stop strategies across 70+ years of F1 dataset history.",
    title="PLATFORM & DATASET OVERVIEW"
)
