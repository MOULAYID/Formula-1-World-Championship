"""Driver Career Archetype Clustering using Unsupervised Machine Learning (K-Means)."""

from typing import Dict, Tuple
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class DriverClusterer:
    """Unsupervised clustering model grouping drivers into distinct career archetypes."""

    CLUSTER_NAMES = {
        0: "Consistent Podium Contenders",
        1: "Championship Legends",
        2: "Mid-Field Workhorses",
        3: "Short-Career / One-Season Performers",
    }

    FEATURE_COLS = [
        "total_starts",
        "win_rate",
        "podium_rate",
        "pole_rate",
        "dnf_rate",
        "avg_finish",
        "driver_performance_score",
    ]

    def __init__(self, n_clusters: int = 4, random_state: int = 42):
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        self.is_fitted = False

    def fit_predict(self, driver_stats_df: pd.DataFrame) -> pd.DataFrame:
        """Fit K-Means clustering and attach cluster label & human-readable archetype."""
        df = driver_stats_df.copy()
        
        available_features = [c for c in self.FEATURE_COLS if c in df.columns]
        X = df[available_features].fillna(0)

        X_scaled = self.scaler.fit_transform(X)
        df["cluster_id"] = self.kmeans.fit_predict(X_scaled)
        self.is_fitted = True

        # Map cluster IDs dynamically based on avg Driver Performance Score order
        cluster_means = df.groupby("cluster_id")["driver_performance_score"].mean().sort_values(ascending=False)
        rank_mapping = {old_id: idx for idx, old_id in enumerate(cluster_means.index)}
        
        df["archetype_rank"] = df["cluster_id"].map(rank_mapping)
        
        archetype_labels = {
            0: "🏆 Championship Legend",
            1: "🥇 Consistent Podium Contender",
            2: "🏎️ Mid-Field Workhorse",
            3: "🏁 Short-Career / One-Season",
        }
        df["cluster_archetype"] = df["archetype_rank"].map(archetype_labels)

        return df

    def get_cluster_centroids(self, driver_stats_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate mean metrics per cluster archetype."""
        if "cluster_archetype" not in driver_stats_df.columns:
            driver_stats_df = self.fit_predict(driver_stats_df)
            
        centroids = driver_stats_df.groupby("cluster_archetype").agg(
            count=("driverId", "count"),
            avg_dps=("driver_performance_score", "mean"),
            avg_wins=("wins", "mean"),
            avg_podiums=("podiums", "mean"),
            avg_win_rate=("win_rate", "mean"),
            avg_starts=("total_starts", "mean"),
        ).reset_index().sort_values(by="avg_dps", ascending=False)

        return centroids
