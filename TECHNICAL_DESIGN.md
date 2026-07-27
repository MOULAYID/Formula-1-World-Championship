# TECHNICAL DESIGN SPECIFICATION: Formula 1 Performance Intelligence Platform

## 1. System Architecture Overview

The system architecture follows a decoupled, modular design consisting of four layers:
1. **Data Ingestion & Gathering Layer (`data/`)**: Centralized storage of all 14 Kaggle Formula 1 CSV files.
2. **Data Access & Processing Layer (`src/data/`)**: Loads CSV dataset files from `data/`, cleans strings/dates/nulls, and constructs unified relational dataframes.
3. **Analytics & Feature Layer (`src/features/`)**: Computes statistical metrics, driver composite scores, constructor dominance indices, and circuit difficulty matrices.
4. **Machine Learning & Modeling Layer (`src/models/`)**: Trains and serves regression, classification, and clustering models using Scikit-Learn and XGBoost.
5. **Presentation & Application Layer (`dashboard/`)**: Streamlit multi-page web application featuring responsive Plotly visualizations and F1 dark racing aesthetics.

---

## 2. Directory & Module Structure

```
Formula-1-World-Championship/
├── data/                                # Unified raw dataset directory
│   ├── circuits.csv
│   ├── constructor_results.csv
│   ├── constructor_standings.csv
│   ├── constructors.csv
│   ├── driver_standings.csv
│   ├── drivers.csv
│   ├── lap_times.csv
│   ├── pit_stops.csv
│   ├── qualifying.csv
│   ├── races.csv
│   ├── results.csv
│   ├── seasons.csv
│   ├── sprint_results.csv
│   └── status.csv
├── PROJECT_SPEC.md
├── DATA_ANALYSIS_SPEC.md
├── TECHNICAL_DESIGN.md
├── DASHBOARD_SPEC.md
├── TASKS.md
├── README.md
├── requirements.txt
├── src/                                 # Modular Python package
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py                    # F1DataLoader (reads from data/ directory)
│   │   └── preprocessor.py              # F1DataPreprocessor for cleaning & merging
│   ├── features/
│   │   ├── __init__.py
│   │   └── metrics.py                   # F1MetricsCalculator for DPS, DIS, CDS
│   ├── models/
│   │   ├── __init__.py
│   │   ├── driver_ranking.py            # DriverRankingModel
│   │   ├── race_prediction.py           # RaceOutcomePredictor
│   │   └── driver_clustering.py         # DriverClusterer
│   └── utils/
│       ├── __init__.py
│       └── helpers.py                   # Plotly dark theme & formatting helpers
├── notebooks/                           # Analytical notebooks
│   ├── 01_eda_data_prep.ipynb
│   ├── 02_driver_constructor_analytics.ipynb
│   ├── 03_statistical_modeling.ipynb
│   └── 04_machine_learning.ipynb
├── dashboard/                           # Streamlit Interactive Web Application
│   ├── app.py                           # Main entrance
│   ├── components/                      # KPI cards, styles, Plotly charts
│   └── pages/                           # 7 Interactive analytics pages
└── reports/
    └── executive_summary.md
```

---

## 3. Data Processing Pipeline & Caching

### 3.1 Class Responsibilities
- `F1DataLoader`:
  - Accepts `data_dir` parameter (defaults to `"data"`).
  - Enforces explicit pandas `dtypes`.
  - Replaces `\N` string entries with `np.nan`.
  - Parses time strings (`"1:27.452"`, `"23.426"`) to numeric milliseconds.
  - Exposes `@st.cache_data` decorated loader methods for fast Streamlit UI interaction.
- `F1DataPreprocessor`:
  - Merges `results`, `races`, `drivers`, `constructors`, `circuits`, `status`, `qualifying`, and `pit_stops`.
  - Calculates DNF categories (Mechanical vs. Accident vs. Finished).
  - Assigns historical F1 Eras based on race year.

---

## 4. Machine Learning Pipeline Architecture

### 4.1 Driver Performance Ranking Model (`src/models/driver_ranking.py`)
- RandomForestRegressor predicting composite Driver Performance Score (DPS).

### 4.2 Race Outcome Predictor (`src/models/race_prediction.py`)
- RandomForestClassifier predicting Top 3 Podium Finish probability.

### 4.3 Driver Clustering Model (`src/models/driver_clustering.py`)
- K-Means driver career archetype clustering.
