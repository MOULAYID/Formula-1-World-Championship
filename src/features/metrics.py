"""F1 Metrics Calculator implementing Driver Performance Score, Dominance, Circuit Difficulty, and Track Characteristics."""

from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd


# Circuit Type Taxonomy
STREET_CIRCUITS = ["Monaco", "Marina Bay", "Baku", "Albert Park", "Jeddah", "Las Vegas", "Miami", "Valencia", "Sochi"]
POWER_CIRCUITS = ["Monza", "Spa-Francorchamps", "Silverstone", "Red Bull Ring", "Hockenheimring", "Indianapolis", "Circuit of the Americas"]
TECHNICAL_CIRCUITS = ["Hungaroring", "Circuit de Barcelona-Catalunya", "Suzuka", "Zandvoort", "Magny-Cours", "Sepang", "Interlagos"]


class F1MetricsCalculator:
    """Calculates custom analytical metrics for drivers, constructors, circuits, and seasons."""

    def __init__(self, master_df: pd.DataFrame, driver_standings_df: Optional[pd.DataFrame] = None):
        self.df = master_df.copy()
        self.driver_standings = driver_standings_df.copy() if driver_standings_df is not None else pd.DataFrame()

    def compute_driver_career_stats(self, min_starts: int = 10) -> pd.DataFrame:
        """Compute career aggregation metrics for drivers including fastest laps."""
        # Calculate fastest lap indicator if rank == 1 or fastestLap == '1'
        if "rank" in self.df.columns:
            self.df["is_fastest_lap"] = (pd.to_numeric(self.df["rank"], errors="coerce") == 1).astype(int)
        else:
            self.df["is_fastest_lap"] = 0

        grouped = self.df.groupby(["driverId", "driver_name", "driver_nationality"])
        
        stats = grouped.agg(
            total_starts=("resultId", "count"),
            wins=("is_win", "sum"),
            podiums=("is_podium", "sum"),
            poles=("is_pole", "sum"),
            fastest_laps=("is_fastest_lap", "sum"),
            total_points=("points", "sum"),
            avg_grid=("grid", "mean"),
            avg_finish=("positionOrder", "mean"),
            total_dnfs=("is_dnf", "sum"),
            mechanical_dnfs=("is_mechanical_dnf", "sum"),
            accident_dnfs=("is_accident_dnf", "sum"),
            first_year=("year", "min"),
            last_year=("year", "max"),
        ).reset_index()

        stats = stats[stats["total_starts"] >= min_starts].copy()

        # Rates
        stats["win_rate"] = stats["wins"] / stats["total_starts"]
        stats["podium_rate"] = stats["podiums"] / stats["total_starts"]
        stats["pole_rate"] = stats["poles"] / stats["total_starts"]
        stats["fastest_lap_rate"] = stats["fastest_laps"] / stats["total_starts"]
        stats["dnf_rate"] = stats["total_dnfs"] / stats["total_starts"]
        stats["points_per_start"] = stats["total_points"] / stats["total_starts"]
        stats["career_span_years"] = stats["last_year"] - stats["first_year"] + 1

        # Calculate World Championships
        championships = self._calculate_world_championships()
        stats = stats.merge(championships, on="driverId", how="left")
        stats["championships"] = stats["championships"].fillna(0).astype(int)

        # Calculate Teammate Head-to-Head Win Rate
        h2h_rates = self._calculate_teammate_h2h()
        stats = stats.merge(h2h_rates, on="driverId", how="left")
        stats["teammate_h2h_win_rate"] = stats["teammate_h2h_win_rate"].fillna(0.50)

        # Composite Driver Performance Score (DPS)
        stats["driver_performance_score"] = self._compute_dps(stats)

        return stats.sort_values(by="driver_performance_score", ascending=False)

    def _calculate_world_championships(self) -> pd.DataFrame:
        """Count World Drivers' Championships (P1 at end of season)."""
        if self.driver_standings.empty or "position" not in self.driver_standings.columns:
            final_races = self.df.groupby("year")["round"].max().reset_index()
            year_points = self.df.groupby(["year", "driverId"])["points"].sum().reset_index()
            year_winners = year_points.sort_values(["year", "points"], ascending=[True, False]).groupby("year").first().reset_index()
            champs = year_winners.groupby("driverId")["year"].count().reset_index().rename(columns={"year": "championships"})
            return champs

        races_last = self.df.groupby("year")["round"].max().reset_index()
        last_race_ids = self.df.merge(races_last, on=["year", "round"])["raceId"].unique()
        
        final_standings = self.driver_standings[self.driver_standings["raceId"].isin(last_race_ids)]
        final_champs = final_standings[final_standings["position"] == 1]
        champs = final_champs.groupby("driverId")["raceId"].count().reset_index().rename(columns={"raceId": "championships"})
        return champs

    def _calculate_teammate_h2h(self) -> pd.DataFrame:
        """Calculate percentage of races finished ahead of teammate when both finish."""
        df_fin = self.df[self.df["is_dnf"] == 0][["raceId", "constructorId", "driverId", "positionOrder"]]
        
        merged = df_fin.merge(df_fin, on=["raceId", "constructorId"], suffixes=("_d1", "_d2"))
        paired = merged[merged["driverId_d1"] != merged["driverId_d2"]].copy()
        paired["ahead"] = (paired["positionOrder_d1"] < paired["positionOrder_d2"]).astype(int)
        
        h2h = paired.groupby("driverId_d1").agg(
            total_battles=("ahead", "count"),
            wins_ahead=("ahead", "sum")
        ).reset_index().rename(columns={"driverId_d1": "driverId"})

        h2h["teammate_h2h_win_rate"] = np.where(
            h2h["total_battles"] > 0,
            h2h["wins_ahead"] / h2h["total_battles"],
            0.50
        )
        return h2h[["driverId", "teammate_h2h_win_rate"]]

    def _compute_dps(self, stats: pd.DataFrame) -> pd.Series:
        """Compute Driver Performance Score (0-100 scale)."""
        w_win = 0.30
        w_podium = 0.20
        w_champ = 0.20
        w_h2h = 0.15
        w_finish = 0.15

        norm_win = np.clip(stats["win_rate"] / 0.40, 0, 1)
        norm_podium = np.clip(stats["podium_rate"] / 0.60, 0, 1)
        norm_champ = np.clip(stats["championships"] / 7.0, 0, 1)
        norm_h2h = np.clip(stats["teammate_h2h_win_rate"], 0, 1)
        norm_finish = np.clip((20.0 - stats["avg_finish"]) / 19.0, 0, 1)

        raw_score = (
            w_win * norm_win +
            w_podium * norm_podium +
            w_champ * norm_champ +
            w_h2h * norm_h2h +
            w_finish * norm_finish
        ) * 100.0

        return np.round(raw_score, 2)

    def compute_constructor_stats(self) -> pd.DataFrame:
        """Compute constructor dominance and reliability statistics."""
        grouped = self.df.groupby(["constructorId", "constructor_name", "constructor_nationality"])
        
        c_stats = grouped.agg(
            total_entries=("resultId", "count"),
            race_starts=("raceId", "nunique"),
            wins=("is_win", "sum"),
            podiums=("is_podium", "sum"),
            total_points=("points", "sum"),
            total_dnfs=("is_dnf", "sum"),
            mechanical_dnfs=("is_mechanical_dnf", "sum"),
            first_year=("year", "min"),
            last_year=("year", "max"),
        ).reset_index()

        c_stats["win_rate"] = c_stats["wins"] / np.maximum(c_stats["race_starts"], 1)
        c_stats["podium_rate"] = c_stats["podiums"] / np.maximum(c_stats["total_entries"], 1)
        c_stats["reliability_score"] = (1.0 - (c_stats["mechanical_dnfs"] / np.maximum(c_stats["total_entries"], 1))) * 100.0
        c_stats["points_per_start"] = c_stats["total_points"] / np.maximum(c_stats["race_starts"], 1)

        return c_stats.sort_values(by="wins", ascending=False)

    def compute_circuit_difficulty(self) -> pd.DataFrame:
        """Calculate Circuit Difficulty Score (CDS) and classify track characteristics."""
        grouped = self.df.groupby(["circuitId", "circuit_name", "location", "circuit_country", "lat", "lng"])
        
        c_diff = grouped.agg(
            total_races=("raceId", "nunique"),
            total_starts=("resultId", "count"),
            total_dnfs=("is_dnf", "sum"),
            mechanical_dnfs=("is_mechanical_dnf", "sum"),
            accident_dnfs=("is_accident_dnf", "sum"),
            pole_wins=("is_win", lambda x: (x & (self.df.loc[x.index, "grid"] == 1)).sum()),
            avg_positions_gained=("positions_gained", "mean"),
        ).reset_index()

        c_diff["dnf_rate"] = c_diff["total_dnfs"] / np.maximum(c_diff["total_starts"], 1)
        c_diff["pole_win_rate"] = c_diff["pole_wins"] / np.maximum(c_diff["total_races"], 1)

        # Track Characteristic Classification
        def classify_track(row):
            c_name = row["location"]
            if any(s in c_name for s in STREET_CIRCUITS):
                return "Street Circuit"
            elif any(p in c_name for p in POWER_CIRCUITS):
                return "Power Dependent"
            elif any(t in c_name for t in TECHNICAL_CIRCUITS):
                return "High-Downforce Technical"
            else:
                return "Balanced Hybrid"

        c_diff["track_type"] = c_diff.apply(classify_track, axis=1)

        # Composite Circuit Difficulty Score (0 to 100)
        c_diff["circuit_difficulty_score"] = np.round(
            (0.50 * c_diff["dnf_rate"] + 0.30 * (1.0 - c_diff["pole_win_rate"]) + 0.20 * np.clip(np.abs(c_diff["avg_positions_gained"]) / 10.0, 0, 1)) * 100.0,
            2
        )

        return c_diff.sort_values(by="circuit_difficulty_score", ascending=False)
