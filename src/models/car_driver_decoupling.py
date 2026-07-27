"""Linear Ridge regression model decoupling driver skill from car dominance."""

import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge


class CarDriverDecoupler:
    """Decomposes race finish position into Driver Skill Index and Car Performance Index."""

    def __init__(self, master_df: pd.DataFrame, alpha: float = 1.0):
        self.master_df = master_df.copy()
        self.alpha = alpha
        self.driver_skill_df = pd.DataFrame()
        self.car_dominance_df = pd.DataFrame()

    def fit(self, min_starts: int = 15) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Fit Ridge linear model to isolate pure Driver Skill from Car Dominance."""
        df = self.master_df[self.master_df["positionOrder"].notnull()].copy()
        
        # Filter drivers with minimum race starts
        driver_counts = df["driverId"].value_counts()
        valid_drivers = driver_counts[driver_counts >= min_starts].index
        df = df[df["driverId"].isin(valid_drivers)].copy()

        # Create car-season composite key (e.g. Mercedes_2020)
        df["car_season"] = df["constructor_name"] + "_" + df["year"].astype(str)

        # Invert position: 1st gets highest score (e.g., 25 - position)
        df["performance_score"] = 25.0 - np.clip(df["positionOrder"], 1, 24)

        # One-hot encode drivers and car-seasons
        driver_dummies = pd.get_dummies(df["driver_name"], prefix="driver", dtype=float)
        car_dummies = pd.get_dummies(df["car_season"], prefix="car", dtype=float)

        X = pd.concat([driver_dummies, car_dummies], axis=1)
        y = df["performance_score"]

        model = Ridge(alpha=self.alpha, fit_intercept=True)
        model.fit(X, y)

        # Extract coefficients
        coefs = pd.Series(model.coef_, index=X.columns)

        driver_coefs = coefs[coefs.index.str.startswith("driver_")].reset_index()
        driver_coefs.columns = ["feature", "pure_driver_skill_index"]
        driver_coefs["driver_name"] = driver_coefs["feature"].str.replace("driver_", "", regex=False)
        driver_coefs = driver_coefs.sort_values("pure_driver_skill_index", ascending=False)

        car_coefs = coefs[coefs.index.str.startswith("car_")].reset_index()
        car_coefs.columns = ["feature", "car_dominance_index"]
        car_coefs["car_season"] = car_coefs["feature"].str.replace("car_", "", regex=False)
        car_coefs["constructor_name"] = car_coefs["car_season"].apply(lambda s: s.rsplit("_", 1)[0])
        car_coefs["year"] = car_coefs["car_season"].apply(lambda s: int(s.rsplit("_", 1)[1]))
        car_coefs = car_coefs.sort_values("car_dominance_index", ascending=False)

        # Normalize driver skill scores to 0-100 scale
        min_s, max_s = driver_coefs["pure_driver_skill_index"].min(), driver_coefs["pure_driver_skill_index"].max()
        if max_s > min_s:
            driver_coefs["driver_skill_normalized"] = ((driver_coefs["pure_driver_skill_index"] - min_s) / (max_s - min_s)) * 100.0
        else:
            driver_coefs["driver_skill_normalized"] = 50.0

        self.driver_skill_df = driver_coefs
        self.car_dominance_df = car_coefs

        return driver_coefs, car_coefs
