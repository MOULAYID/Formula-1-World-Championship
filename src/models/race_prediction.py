"""Race Outcome Classifier predicting Podium (Top 3 Finish) Probability."""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split


class RaceOutcomePredictor:
    """Supervised classification model for predicting Podium Finish (Top 3) probability."""

    FEATURE_COLS = [
        "grid",
        "year",
        "round",
        "constructorId",
        "circuitId",
    ]

    def __init__(self, n_estimators: int = 150, random_state: int = 42):
        self.model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state, class_weight="balanced")
        self.is_fitted = False
        self.feature_cols = self.FEATURE_COLS

    def prepare_features(self, master_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Engineers features for race outcome modeling."""
        df = master_df.copy()
        
        # Grid start position
        df["grid"] = pd.to_numeric(df["grid"], errors="coerce").fillna(20)
        
        # Recent driver form (avg finish in previous 3 races)
        df = df.sort_values(["driverId", "year", "round"])
        df["recent_avg_finish"] = df.groupby("driverId")["positionOrder"].transform(
            lambda x: x.shift(1).rolling(3, min_periods=1).mean()
        ).fillna(10.0)

        # Features array
        cols = ["grid", "year", "round", "recent_avg_finish", "circuitId", "constructorId"]
        X = df[cols].fillna(0)
        y = df["is_podium"].fillna(0).astype(int)
        self.feature_cols = cols

        return X, y

    def fit(self, master_df: pd.DataFrame) -> Dict[str, float]:
        """Train the classifier on historical race data."""
        X, y = self.prepare_features(master_df)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        self.model.fit(X_train, y_train)
        self.is_fitted = True

        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1_score": f1_score(y_test, y_pred, zero_division=0),
            "roc_auc": roc_auc_score(y_test, y_proba),
        }
        return metrics

    def predict_podium_proba(self, sample_dict: Dict[str, Any]) -> float:
        """Predict probability of finishing on the podium for a single race entry."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before predicting.")

        row = pd.DataFrame([sample_dict])
        for col in self.feature_cols:
            if col not in row.columns:
                row[col] = 0

        X_sample = row[self.feature_cols].fillna(0)
        proba = self.model.predict_proba(X_sample)[0, 1]
        return float(proba)
