"""F1 Data Loader module for ingestion and clean parsing of CSV datasets."""

import os
from pathlib import Path
from typing import Dict, Optional, Union
import numpy as np
import pandas as pd


def parse_time_to_ms(time_str: Union[str, float, int]) -> Optional[float]:
    """Convert time strings (e.g. '1:27.452' or '23.426') to milliseconds float."""
    if pd.isna(time_str) or time_str == r"\N" or not time_str:
        return np.nan
    
    if isinstance(time_str, (int, float)):
        return float(time_str)
    
    try:
        s_str = str(time_str).strip()
        if ":" in s_str:
            parts = s_str.split(":")
            if len(parts) == 2:
                minutes = float(parts[0])
                seconds = float(parts[1])
                return (minutes * 60 + seconds) * 1000.0
            elif len(parts) == 3:
                hours = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])
                return (hours * 3600 + minutes * 60 + seconds) * 1000.0
        else:
            return float(s_str) * 1000.0
    except Exception:
        return np.nan


class F1DataLoader:
    """Class responsible for loading raw F1 CSV files from data directory."""

    CSV_FILES = [
        "races.csv",
        "results.csv",
        "drivers.csv",
        "constructors.csv",
        "circuits.csv",
        "status.csv",
        "qualifying.csv",
        "pit_stops.csv",
        "lap_times.csv",
        "driver_standings.csv",
        "constructor_standings.csv",
        "seasons.csv",
        "sprint_results.csv",
    ]

    def __init__(self, data_dir: Union[str, Path] = "data"):
        self.data_dir = Path(data_dir)

    def load_csv(self, filename: str) -> pd.DataFrame:
        """Load a single CSV file, handling missing values '\\N'."""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found at: {filepath}")

        df = pd.read_csv(filepath, na_values=[r"\N", "\\N", "N/A", "nan", ""])
        
        # Clean string columns with whitespace
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"nan": np.nan, r"\N": np.nan, "None": np.nan})

        return df

    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all 14 core F1 CSV files into a dictionary of DataFrames."""
        data_dict = {}
        for fname in self.CSV_FILES:
            key = fname.replace(".csv", "")
            try:
                data_dict[key] = self.load_csv(fname)
            except FileNotFoundError:
                print(f"Warning: {fname} not found in {self.data_dir}")
        return data_dict

    def clean_results(self, df_results: pd.DataFrame) -> pd.DataFrame:
        """Clean numerical and time fields in results DataFrame."""
        df = df_results.copy()
        
        numeric_cols = ["grid", "positionOrder", "points", "laps", "milliseconds", "statusId"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                
        if "position" in df.columns:
            df["position_numeric"] = pd.to_numeric(df["position"], errors="coerce")
            
        if "fastestLapTime" in df.columns:
            df["fastest_lap_ms"] = df["fastestLapTime"].apply(parse_time_to_ms)
            
        return df

    def clean_drivers(self, df_drivers: pd.DataFrame) -> pd.DataFrame:
        """Clean drivers DataFrame and construct full driver name."""
        df = df_drivers.copy()
        df["driver_name"] = df["forename"].fillna("") + " " + df["surname"].fillna("")
        df["driver_name"] = df["driver_name"].str.strip()
        if "dob" in df.columns:
            df["dob"] = pd.to_datetime(df["dob"], errors="coerce")
        return df

    def clean_pit_stops(self, df_pits: pd.DataFrame) -> pd.DataFrame:
        """Clean pit stops duration and milliseconds."""
        df = df_pits.copy()
        if "milliseconds" in df.columns:
            df["milliseconds"] = pd.to_numeric(df["milliseconds"], errors="coerce")
        if "duration" in df.columns:
            df["duration_ms"] = df["duration"].apply(parse_time_to_ms)
        return df
