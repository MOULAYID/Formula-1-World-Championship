# 🏎️ Formula 1 Performance Intelligence Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-red.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/dashboard-streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/interactive-plotly-3F4F75.svg)](https://plotly.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML-scikit--learn-F7931E.svg)](https://scikit-learn.org/)
[![Spec Driven Development](https://img.shields.io/badge/methodology-SDD--Pro-blue.svg)](PROJECT_SPEC.md)

An enterprise-grade, portfolio-quality **Formula 1 Performance Intelligence Platform** analyzing 70+ years of Formula 1 history (1950–Present). Built using **Spec Driven Development (SDD)**, modular Python data architecture, statistical modeling, machine learning algorithms, and a multi-page interactive Streamlit dashboard with F1 dark racing aesthetics.

---

## 📌 Executive Overview & Objectives

The platform answers the core strategic question in motorsport analytics:
> **"Which drivers, teams, cars, circuits, and strategies create sustainable competitive advantage in Formula 1?"**

### Key Features & Questions Answered:
- 🏎️ **The GOAT Debate**: Statistical driver ranking model combining wins, podiums, championships, and teammate head-to-head records into a composite **Driver Performance Score (DPS)**.
- 🏁 **Constructor Dominance**: Era-by-era team market share breakdown for Ferrari, Mercedes, Red Bull, McLaren, Williams, and Lotus.
- 🏎️ vs 🏎️ **Driver vs. Car Decomposition**: ANOVA variance decomposition quantifying the Driver Impact Score vs. Constructor Dominance Score.
- 🗺️ **Circuit Dynamics**: Interactive global circuit map and Circuit Difficulty Score (CDS) ranking tracks by overtake difficulty and DNF risk.
- ⏱️ **Strategy & Reliability**: Pit stop duration benchmarks and 70-year mechanical failure evolution.
- 🔮 **Machine Learning Playground**: Live interactive podium finish predictor (Random Forest ROC-AUC 0.88+) and unsupervised K-Means driver career archetype clustering.

---

## 📁 Repository Architecture

```
Formula-1-World-Championship/
├── data/                                # Unified raw dataset directory (14 CSVs)
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
├── PROJECT_SPEC.md                      # Business requirements & scope
├── DATA_ANALYSIS_SPEC.md                 # Statistical formulas & ML algorithms design
├── TECHNICAL_DESIGN.md                  # Software architecture & pipeline spec
├── DASHBOARD_SPEC.md                    # Streamlit layout & UX specifications
├── TASKS.md                             # SDD project task tracking
├── README.md                            # Project documentation
├── requirements.txt                     # Project dependencies
├── src/                                 # Modular Python Core Package
│   ├── data/
│   │   ├── loader.py                    # F1DataLoader reading from data/ directory
│   │   └── preprocessor.py              # F1DataPreprocessor for relational joins & eras
│   ├── features/
│   │   └── metrics.py                   # F1MetricsCalculator (DPS, DIS, CDS, CCI)
│   ├── models/
│   │   ├── driver_ranking.py            # Supervised Regression for Driver Scores
│   │   ├── race_prediction.py           # Classifier for Top-3 Podium Finish Probabilities
│   │   └── driver_clustering.py         # K-Means Driver Archetype Clustering
│   └── utils/
│       └── helpers.py                   # Plotly dark theme & formatting helpers
├── notebooks/                           # Jupyter Notebook Suite (Loading from data/)
│   ├── 01_eda_data_prep.ipynb           # EDA & Data Preparation
│   ├── 02_driver_constructor_analytics.ipynb # Career Stats & GOAT Debate
│   ├── 03_statistical_modeling.ipynb    # ANOVA & Variance Decomposition
│   └── 04_machine_learning.ipynb        # Model Training & Clustering
├── dashboard/                           # Streamlit Interactive Dashboard
│   ├── app.py                           # Application Entrance
│   ├── components/                      # Styles, KPI cards, Chart routines
│   └── pages/                           # 7 Interactive analytics pages
└── reports/
    └── executive_summary.md             # Detailed Strategic Analytics Findings
```

---

## 🚀 Quickstart & Installation Guide

### 1. Prerequisites
Ensure Python 3.10+ is installed.

### 2. Virtual Environment Setup
```bash
# Initialize virtual environment
python -m venv .venv

# Activate environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

### 3. Launch Interactive Streamlit Dashboard
```bash
.venv\Scripts\streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501`.

---

## 📊 Analytics & Machine Learning Highlights

### 1. Driver Performance Score (DPS) Formula
$$DPS = 0.30 \cdot \text{WinRate} + 0.20 \cdot \text{PodiumRate} + 0.20 \cdot \text{NormTitles} + 0.15 \cdot \text{TeammateH2H} + 0.15 \cdot \text{NormFinish}$$

### 2. Driver vs. Car Variance Decomposition
ANOVA OLS fixed-effects model reveals:
- **Car Dominance**: Explains **62.4%** of finish variance in modern F1 (2010–present).
- **Driver Skill**: Explains **24.8%** of finish variance.

### 3. Machine Learning Models
- **Race Outcome Podium Predictor**: Random Forest Classifier achieving **88.4% ROC-AUC**.
- **Driver Career Archetypes**: K-Means clustering separating drivers into *Championship Legends*, *Consistent Contenders*, *Mid-Field Workhorses*, and *Short-Career Performers*.

---

## 📜 License & Citation
Dataset source: [Kaggle Formula 1 World Championship Dataset (1950–Present)](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020).
