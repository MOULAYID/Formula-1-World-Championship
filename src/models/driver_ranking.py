"""Driver Ranking Model predicting Driver Performance Score using machine learning."""

from typing import Dict, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


class DriverRankingModel:
    """Supervised regression model predicting Driver Performance Score."""

    FEATURE_COLS = [
        "win_rate",
        "podium_rate",
        "pole_rate",
        "dnf_rate",
        "avg_finish",
        "avg_grid",
        "teammate_h2h_win_rate",
        "points_per_start",
        "championships",
    ]

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
        self.is_fitted = False
        self.feature_importances_: pd.DataFrame = pd.DataFrame()

    def fit(self, driver_stats_df: pd.DataFrame) -> Dict[str, float]:
        """Fit the model on driver career stats DataFrame."""
        df = driver_stats_df.copy()
        
        # Verify required columns exist
        available_features = [c for c in self.FEATURE_COLS if c in df.columns]
        if not available_features:
            raise ValueError("No matching feature columns found in DataFrame.")

        X = df[available_features].fillna(0)
        y = df["driver_performance_score"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model.fit(X_train, y_train)
        self.is_fitted = True

        y_pred = self.model.predict(X_test)
        
        # Feature importances
        importances = pd.DataFrame({
            "feature": available_features,
            "importance": self.model.feature_importances_
        }).sort_values(by="importance", ascending=False)
        self.feature_importances_ = importances

        metrics = {
            "r2_score": r2_score(y_test, y_pred),
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
        }
        return metrics

    def predict(self, X_input: pd.DataFrame) -> np.ndarray:
        """Predict Driver Performance Score for new input samples."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before predicting.")
        available_features = [c for c in self.FEATURE_COLS if c in X_input.columns]
        X = X_input[available_features].fillna(0)
        return self.model.predict(X)
