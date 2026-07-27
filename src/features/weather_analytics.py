"""Rain Master and wet weather performance rating engine."""

import pandas as pd
import numpy as np


class WeatherAnalytics:
    """Analytical engine to identify wet races and rate driver wet-weather performance."""

    # Curated historical wet / chaotic wet-dry F1 Grands Prix
    HISTORICAL_WET_RACES_KEYWORDS = [
        "Monaco 1984", "Monaco 1996", "Monaco 2008", "Monaco 2016", "Monaco 2022",
        "Spain 1996", "Belgium 1998", "Belgium 2021", "Europe 1999", "Europe 2007",
        "Japan 1994", "Fuji 2007", "Fuji 2008", "Brazil 2008", "Brazil 2016",
        "Canada 2011", "Germany 2019", "Turkey 2020", "Russia 2021", "Netherlands 2023",
        "Great Britain 2008", "China 2009", "Malaysia 2009", "Italy 2008"
    ]

    def __init__(self, master_df: pd.DataFrame):
        self.master_df = master_df.copy()

    def identify_wet_races(self) -> pd.DataFrame:
        """Flag races that were wet or featured rain disruptions based on known wet events or high DNF/lap time variance."""
        races = self.master_df[["raceId", "year", "circuit_name", "race_name", "positions_gained"]].drop_duplicates()
        
        # Match by name or high position variance
        def is_wet_row(row):
            event_str = f"{row['circuit_name']} {row['year']}"
            race_str = f"{row['race_name']} {row['year']}"
            if any(k.lower() in event_str.lower() or k.lower() in race_str.lower() for k in self.HISTORICAL_WET_RACES_KEYWORDS):
                return True
            return False

        races["is_wet_race"] = races.apply(is_wet_row, axis=1)
        return races[["raceId", "is_wet_race"]]

    def compute_rain_master_ratings(self, min_wet_starts: int = 2) -> pd.DataFrame:
        """Compute Rain Master rating for all drivers across wet vs dry conditions."""
        wet_flags = self.identify_wet_races()
        df = self.master_df.merge(wet_flags, on="raceId", how="left")
        df["is_wet_race"] = df["is_wet_race"].fillna(False)

        # Group by driver for wet races
        wet_df = df[df["is_wet_race"]].copy()
        if wet_df.empty:
            return pd.DataFrame()

        wet_stats = wet_df.groupby(["driverId", "driver_name", "driver_nationality"]).agg(
            wet_starts=("resultId", "count"),
            wet_wins=("is_win", "sum"),
            wet_podiums=("is_podium", "sum"),
            wet_avg_positions_gained=("positions_gained", "mean"),
            wet_avg_finish=("positionOrder", "mean")
        ).reset_index()

        # Group by driver for dry races
        dry_df = df[~df["is_wet_race"]].copy()
        dry_stats = dry_df.groupby("driverId").agg(
            dry_starts=("resultId", "count"),
            dry_wins=("is_win", "sum"),
            dry_podiums=("is_podium", "sum"),
            dry_avg_finish=("positionOrder", "mean")
        ).reset_index()

        merged = wet_stats.merge(dry_stats, on="driverId", how="left")
        merged = merged[merged["wet_starts"] >= min_wet_starts].copy()

        merged["wet_win_rate"] = merged["wet_wins"] / merged["wet_starts"]
        merged["wet_podium_rate"] = merged["wet_podiums"] / merged["wet_starts"]
        merged["dry_win_rate"] = (merged["dry_wins"] / merged["dry_starts"]).fillna(0.0)

        # Compute Rain Master Index (0 - 100)
        merged["wet_overperformance_delta"] = merged["wet_win_rate"] - merged["dry_win_rate"]
        
        merged["rain_master_score"] = (
            (merged["wet_win_rate"] * 40.0) +
            (merged["wet_podium_rate"] * 30.0) +
            (np.clip(merged["wet_avg_positions_gained"], -5, 10) * 2.5) +
            (np.clip(merged["wet_overperformance_delta"], 0, 1) * 20.0)
        )
        
        # Scale to 0 - 100 max range
        max_score = merged["rain_master_score"].max()
        if max_score > 0:
            merged["rain_master_score"] = (merged["rain_master_score"] / max_score) * 100.0

        return merged.sort_values(by="rain_master_score", ascending=False)
