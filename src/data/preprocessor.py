"""F1 Data Preprocessor for relational table merging, feature calculation, and era categorization."""

from typing import Dict, Tuple
import numpy as np
import pandas as pd
from .loader import F1DataLoader


def get_f1_era(year: int) -> str:
    """Categorize F1 race year into historical technical eras."""
    if year < 1970:
        return "1950-1969 (Pioneers & Front-Engine)"
    elif year < 1990:
        return "1970-1989 (Ground Effect & Turbo)"
    elif year < 2006:
        return "1990-2005 (V10 Era & Schumacher)"
    elif year < 2014:
        return "2006-2013 (V8 Engine Era & Red Bull)"
    else:
        return "2014-Present (Turbo-Hybrid Era)"


class F1DataPreprocessor:
    """Preprocessor for unifying raw F1 datasets into master analytical DataFrames."""

    def __init__(self, data_dict: Dict[str, pd.DataFrame]):
        self.loader = F1DataLoader()
        self.races = data_dict.get("races", pd.DataFrame())
        self.results = self.loader.clean_results(data_dict.get("results", pd.DataFrame()))
        self.drivers = self.loader.clean_drivers(data_dict.get("drivers", pd.DataFrame()))
        self.constructors = data_dict.get("constructors", pd.DataFrame())
        self.circuits = data_dict.get("circuits", pd.DataFrame())
        self.status = data_dict.get("status", pd.DataFrame())
        self.qualifying = data_dict.get("qualifying", pd.DataFrame())
        self.pit_stops = self.loader.clean_pit_stops(data_dict.get("pit_stops", pd.DataFrame()))

    def classify_status(self, status_str: str) -> str:
        """Classify raw status string into DNF categories."""
        if pd.isna(status_str):
            return "Unknown"
        
        s = str(status_str).lower().strip()
        if s == "finished" or s.startswith("+") or "lap" in s:
            return "Finished"
        elif any(k in s for k in ["accident", "collision", "spin", "off track", "crash"]):
            return "Accident / Collision DNF"
        elif any(k in s for k in [
            "engine", "gearbox", "transmission", "clutch", "hydraulics", "electrical",
            "brakes", "suspension", "overheating", "mechanical", "oil", "water", "turbo",
            "fuel", "wheel", "puncture", "driveshaft", "exhaust", "steering", "battery"
        ]):
            return "Mechanical DNF"
        elif "disqualified" in s:
            return "Disqualified"
        else:
            return "Other Retirement"

    def build_master_results(self) -> pd.DataFrame:
        """Merge results with races, drivers, constructors, circuits, and status."""
        if self.results.empty or self.races.empty:
            raise ValueError("Core datasets (results, races) are empty.")

        # Prepare merge tables
        races_df = self.races[["raceId", "year", "round", "circuitId", "name", "date"]].rename(
            columns={"name": "race_name", "date": "race_date"}
        )
        races_df["era"] = races_df["year"].apply(get_f1_era)

        drivers_df = self.drivers[["driverId", "driverRef", "code", "driver_name", "nationality", "dob"]].rename(
            columns={"nationality": "driver_nationality"}
        )

        constructors_df = self.constructors[["constructorId", "constructorRef", "name", "nationality"]].rename(
            columns={"name": "constructor_name", "nationality": "constructor_nationality"}
        )

        circuits_df = self.circuits[["circuitId", "circuitRef", "name", "location", "country", "lat", "lng", "alt"]].rename(
            columns={"name": "circuit_name", "country": "circuit_country"}
        )

        status_df = self.status[["statusId", "status"]].rename(columns={"status": "status_raw"})

        # Master Merge
        master = self.results.merge(races_df, on="raceId", how="left")
        master = master.merge(drivers_df, on="driverId", how="left")
        master = master.merge(constructors_df, on="constructorId", how="left")
        master = master.merge(circuits_df, on="circuitId", how="left")
        master = master.merge(status_df, on="statusId", how="left")

        # Feature additions
        master["dnf_category"] = master["status_raw"].apply(self.classify_status)
        master["is_win"] = (master["positionOrder"] == 1).astype(int)
        master["is_podium"] = (master["positionOrder"] <= 3).astype(int)
        master["is_top10"] = (master["positionOrder"] <= 10).astype(int)
        master["is_dnf"] = (master["dnf_category"] != "Finished").astype(int)
        master["is_mechanical_dnf"] = (master["dnf_category"] == "Mechanical DNF").astype(int)
        master["is_accident_dnf"] = (master["dnf_category"] == "Accident / Collision DNF").astype(int)
        master["positions_gained"] = master["grid"] - master["positionOrder"]
        
        # Is Pole position
        master["is_pole"] = (master["grid"] == 1).astype(int)

        return master

    def build_qualifying_performance(self) -> pd.DataFrame:
        """Clean and prepare qualifying performance dataset."""
        if self.qualifying.empty:
            return pd.DataFrame()
        
        df_q = self.qualifying.merge(
            self.races[["raceId", "year", "name"]].rename(columns={"name": "race_name"}),
            on="raceId", how="left"
        ).merge(
            self.drivers[["driverId", "driver_name"]], on="driverId", how="left"
        ).merge(
            self.constructors[["constructorId", "name"]].rename(columns={"name": "constructor_name"}),
            on="constructorId", how="left"
        )
        return df_q

    def build_pit_stop_summary(self) -> pd.DataFrame:
        """Merge pit stop details with race, driver, and constructor info."""
        if self.pit_stops.empty:
            return pd.DataFrame()

        pits_merged = self.pit_stops.merge(
            self.races[["raceId", "year", "name"]].rename(columns={"name": "race_name"}),
            on="raceId", how="left"
        ).merge(
            self.drivers[["driverId", "driver_name"]], on="driverId", how="left"
        )

        # Merge constructor from results
        if not self.results.empty:
            results_min = self.results[["raceId", "driverId", "constructorId"]].drop_duplicates()
            pits_merged = pits_merged.merge(results_min, on=["raceId", "driverId"], how="left")
            pits_merged = pits_merged.merge(
                self.constructors[["constructorId", "name"]].rename(columns={"name": "constructor_name"}),
                on="constructorId", how="left"
            )

        return pits_merged
