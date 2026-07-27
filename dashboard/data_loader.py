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
from src.features.strategy_analytics import StrategyAnalytics
from src.features.weather_analytics import WeatherAnalytics
from src.models.elo_rating import F1EloEngine
from src.models.car_driver_decoupling import CarDriverDecoupler


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


@st.cache_data
def load_advanced_analytics(master_df, data_dict):
    """Compute and cache advanced analytics (Strategy, Weather/Rain, Elo, Car-Driver Decoupling)."""
    # 1. Strategy Analytics
    strat_engine = StrategyAnalytics(data_dict.get("lap_times"), data_dict.get("pit_stops"), master_df)
    deg_df = strat_engine.compute_tyre_degradation()
    undercut_df = strat_engine.compute_undercut_overcut_success()

    # 2. Weather & Rain Master
    weather_engine = WeatherAnalytics(master_df)
    rain_master_df = weather_engine.compute_rain_master_ratings()

    # 3. Elo Engine
    elo_engine = F1EloEngine(master_df)
    driver_elo_hist, driver_peak_elo, constructor_elo_hist = elo_engine.compute_historical_elo()

    # 4. Car vs Driver Decoupler
    decoupler = CarDriverDecoupler(master_df)
    pure_skill_df, car_dominance_df = decoupler.fit()

    return {
        "deg_df": deg_df,
        "undercut_df": undercut_df,
        "rain_master_df": rain_master_df,
        "driver_elo_hist": driver_elo_hist,
        "driver_peak_elo": driver_peak_elo,
        "constructor_elo_hist": constructor_elo_hist,
        "pure_skill_df": pure_skill_df,
        "car_dominance_df": car_dominance_df,
    }
