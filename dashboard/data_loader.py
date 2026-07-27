"""Cached data loading module for Streamlit dashboard."""

import sys
from pathlib import Path
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.data.loader import F1DataLoader
from src.data.preprocessor import F1DataPreprocessor
from src.features.metrics import F1MetricsCalculator


@st.cache_data
def load_cached_data():
    """Load and process F1 dataset from data/ directory with caching."""
    loader = F1DataLoader(data_dir=ROOT_DIR / "data")
    data_dict = loader.load_all_data()
    preprocessor = F1DataPreprocessor(data_dict)
    master_df = preprocessor.build_master_results()
    calculator = F1MetricsCalculator(master_df, data_dict.get("driver_standings"))
    driver_stats = calculator.compute_driver_career_stats(min_starts=10)
    constructor_stats = calculator.compute_constructor_stats()
    circuit_stats = calculator.compute_circuit_difficulty()
    return master_df, driver_stats, constructor_stats, circuit_stats, data_dict
