"""Lap-by-lap tyre degradation estimator and pit stop strategy (undercut/overcut) analyzer."""

import pandas as pd
import numpy as np


class StrategyAnalytics:
    """Analytical engine for tyre degradation slopes and undercut/overcut strategy evaluation."""

    def __init__(self, lap_times_df: pd.DataFrame, pit_stops_df: pd.DataFrame, master_df: pd.DataFrame):
        self.lap_times = lap_times_df.copy() if lap_times_df is not None else pd.DataFrame()
        self.pit_stops = pit_stops_df.copy() if pit_stops_df is not None else pd.DataFrame()
        self.master_df = master_df.copy()

    def compute_tyre_degradation(self, min_laps_in_stint: int = 5) -> pd.DataFrame:
        """Estimate average tyre degradation rate (seconds lost per lap) per constructor/era.

        Calculates slope of lap time vs stint lap number, filtering out pit in/out laps
        and safety car outliers (>107% of median race lap time).
        """
        if self.lap_times.empty:
            return pd.DataFrame()

        # Convert milliseconds to seconds if present
        laps = self.lap_times.copy()
        if "milliseconds" in laps.columns:
            laps["lap_seconds"] = laps["milliseconds"] / 1000.0
        elif "seconds" in laps.columns:
            laps["lap_seconds"] = laps["seconds"]
        else:
            return pd.DataFrame()

        # Merge with master_df metadata
        meta = self.master_df[["raceId", "driverId", "constructorId", "constructor_name", "era", "year"]].drop_duplicates()
        laps = laps.merge(meta, on=["raceId", "driverId"], how="inner")

        # Filter outlier safety car / slow laps (>107% of race median)
        race_medians = laps.groupby("raceId")["lap_seconds"].transform("median")
        clean_laps = laps[(laps["lap_seconds"] > 40.0) & (laps["lap_seconds"] <= race_medians * 1.07)].copy()

        # Identify pit laps to separate stints if pit_stops available
        if not self.pit_stops.empty:
            pit_laps = set(zip(self.pit_stops["raceId"], self.pit_stops["driverId"], self.pit_stops["lap"]))
            clean_laps["is_pit_lap"] = clean_laps.apply(lambda r: (r["raceId"], r["driverId"], r["lap"]) in pit_laps, axis=1)
            clean_laps = clean_laps[~clean_laps["is_pit_lap"]]

        # Calculate stint lap number
        clean_laps["stint_id"] = (clean_laps["lap"] - clean_laps.groupby(["raceId", "driverId"])["lap"].cumcount()).astype(str)
        clean_laps["stint_lap_num"] = clean_laps.groupby(["raceId", "driverId", "stint_id"]).cumcount() + 1

        # Compute degradation slope per stint using numpy polyfit
        results = []
        for (race_id, driver_id, stint_id), group in clean_laps.groupby(["raceId", "driverId", "stint_id"]):
            if len(group) >= min_laps_in_stint:
                slope, _ = np.polyfit(group["stint_lap_num"], group["lap_seconds"], 1)
                # Keep realistic degradation slopes between 0.001s/lap and 0.5s/lap
                if 0.001 <= slope <= 0.5:
                    results.append({
                        "raceId": race_id,
                        "driverId": driver_id,
                        "constructorId": group["constructorId"].iloc[0],
                        "constructor_name": group["constructor_name"].iloc[0],
                        "era": group["era"].iloc[0],
                        "year": group["year"].iloc[0],
                        "stint_length": len(group),
                        "degradation_sec_per_lap": slope,
                    })

        df_deg = pd.DataFrame(results)
        return df_deg

    def compute_undercut_overcut_success(self) -> pd.DataFrame:
        """Calculate success rate of undercut vs overcut pit stop strategies."""
        if self.pit_stops.empty:
            return pd.DataFrame()

        pits = self.pit_stops.sort_values(["raceId", "stop"])
        meta = self.master_df[["raceId", "driverId", "driver_name", "positionOrder"]].drop_duplicates()
        pits = pits.merge(meta, on=["raceId", "driverId"], how="inner")

        # Compare consecutive pit stops in same race window
        events = []
        for race_id, group in pits.groupby("raceId"):
            group = group.sort_values("lap")
            for i in range(len(group) - 1):
                stop_a = group.iloc[i]
                stop_b = group.iloc[i + 1]
                lap_diff = stop_b["lap"] - stop_a["lap"]
                # Evaluate undercut window (1 to 3 laps delta between rivals)
                if 1 <= lap_diff <= 3 and stop_a["driverId"] != stop_b["driverId"]:
                    undercutter_won = stop_a["positionOrder"] < stop_b["positionOrder"]
                    events.append({
                        "raceId": race_id,
                        "pitted_first_driver": stop_a["driver_name"],
                        "pitted_second_driver": stop_b["driver_name"],
                        "lap_delta": lap_diff,
                        "strategy_type": "Undercut" if lap_diff >= 1 else "Overcut",
                        "is_undercut_successful": undercutter_won,
                    })

        df_strategy = pd.DataFrame(events)
        return df_strategy
