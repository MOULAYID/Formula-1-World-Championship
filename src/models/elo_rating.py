"""Sequential multi-driver F1 Elo rating system engine."""

import pandas as pd
import numpy as np


class F1EloEngine:
    """Computes sequential Elo ratings for F1 drivers and constructors across 1950 to Present."""

    def __init__(self, master_df: pd.DataFrame, initial_elo: float = 1500.0, k_factor: float = 32.0):
        self.master_df = master_df.copy()
        self.initial_elo = initial_elo
        self.k_factor = k_factor

    def compute_historical_elo(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Compute race-by-race Elo ratings for all drivers and constructors.

        Returns:
            driver_elo_history: Race-by-race Elo history for drivers
            driver_peak_elo: Peak Elo rating leaderboard per driver
            constructor_elo_history: Constructor Elo progression
        """
        # Ensure chronological sorting by year and round
        df = self.master_df.sort_values(["year", "round", "positionOrder"]).copy()

        driver_ratings = {}
        constructor_ratings = {}
        driver_history = []
        constructor_history = []

        # Iterate race by race
        for race_id, race_group in df.groupby("raceId", sort=False):
            year = race_group["year"].iloc[0]
            round_num = race_group["round"].iloc[0]
            race_name = race_group["race_name"].iloc[0]
            race_date = race_group["race_date"].iloc[0]

            drivers_in_race = race_group["driverId"].tolist()
            constructors_in_race = race_group["constructorId"].tolist()

            # Initialize new drivers/constructors
            for d in drivers_in_race:
                if d not in driver_ratings:
                    driver_ratings[d] = self.initial_elo
            for c in constructors_in_race:
                if c not in constructor_ratings:
                    constructor_ratings[c] = self.initial_elo

            # Pairwise Elo updates for drivers based on finish order
            n_entrants = len(race_group)
            if n_entrants < 2:
                continue

            driver_deltas = {d: 0.0 for d in drivers_in_race}
            constructor_deltas = {c: 0.0 for c in constructors_in_race}

            # Compare every pair (i, j) where i finished ahead of j
            race_list = race_group.to_dict("records")
            for i in range(n_entrants):
                for j in range(i + 1, n_entrants):
                    d_a, d_b = race_list[i]["driverId"], race_list[j]["driverId"]
                    r_a, r_b = driver_ratings[d_a], driver_ratings[d_b]

                    # Expected score A vs B
                    e_a = 1.0 / (1.0 + 10.0 ** ((r_b - r_a) / 400.0))
                    e_b = 1.0 - e_a

                    # Actual score: A finished ahead of B (S_A = 1, S_B = 0)
                    scale = self.k_factor / (n_entrants - 1)
                    driver_deltas[d_a] += scale * (1.0 - e_a)
                    driver_deltas[d_b] += scale * (0.0 - e_b)

                    # Constructor Elo update
                    c_a, c_b = race_list[i]["constructorId"], race_list[j]["constructorId"]
                    if c_a != c_b:
                        cr_a, cr_b = constructor_ratings[c_a], constructor_ratings[c_b]
                        ce_a = 1.0 / (1.0 + 10.0 ** ((cr_b - cr_a) / 400.0))
                        ce_b = 1.0 - ce_a
                        constructor_deltas[c_a] += scale * (1.0 - ce_a)
                        constructor_deltas[c_b] += scale * (0.0 - ce_b)

            # Apply deltas & record state
            for row in race_list:
                d = row["driverId"]
                c = row["constructorId"]
                driver_ratings[d] += driver_deltas[d]
                constructor_ratings[c] += constructor_deltas[c]

                driver_history.append({
                    "raceId": race_id,
                    "year": year,
                    "round": round_num,
                    "race_date": race_date,
                    "race_name": race_name,
                    "driverId": d,
                    "driver_name": row["driver_name"],
                    "positionOrder": row["positionOrder"],
                    "driver_elo": driver_ratings[d],
                })

                constructor_history.append({
                    "raceId": race_id,
                    "year": year,
                    "round": round_num,
                    "race_date": race_date,
                    "constructorId": c,
                    "constructor_name": row["constructor_name"],
                    "constructor_elo": constructor_ratings[c],
                })

        df_driver_hist = pd.DataFrame(driver_history)
        df_constructor_hist = pd.DataFrame(constructor_history).drop_duplicates(subset=["raceId", "constructorId"])

        # Compute peak Elo leaderboard
        df_peak = df_driver_hist.groupby(["driverId", "driver_name"]).agg(
            peak_elo=("driver_elo", "max"),
            latest_elo=("driver_elo", "last"),
            starts=("raceId", "count"),
            first_year=("year", "min"),
            last_year=("year", "max")
        ).reset_index().sort_values(by="peak_elo", ascending=False)

        return df_driver_hist, df_peak, df_constructor_hist
