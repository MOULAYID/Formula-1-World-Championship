# PROJECT SPECIFICATION: Formula 1 Performance Intelligence Platform

## 1. Project Overview & Vision
The **Formula 1 Performance Intelligence Platform** is an enterprise-grade sports analytics product designed to analyze over 70 years of Formula 1 history (1950–present). Built to professional motorsport analytical standards, the platform answers the core strategic question:

> **"Which drivers, teams, cars, circuits, and race strategies create sustainable competitive advantage in Formula 1?"**

---

## 2. Target Audience & Personas
- **F1 Team Principal & Race Strategist**: Needs actionable insight into car dominance vs. driver contribution, pit-stop performance windows, and track-specific setup requirements.
- **Sports Data Scientist / Analyst**: Requires rigorous statistical modeling, hypothesis testing, driver ranking models, and predictive ML for race outcomes.
- **Motorsport Media & Executives**: Seeks interactive storytelling, visual GOAT comparisons, era competitiveness analysis, and intuitive executive dashboards.

---

## 3. Scope & Key Business Questions

### 3.1 Driver Performance & Legend Ranking (GOAT Debate)
- Who are the top drivers statistically when controlling for era length, point system changes, and car quality?
- How do legendary drivers (Hamilton, Schumacher, Senna, Verstappen, Fangio, Alonso, Vettel, Prost) compare on win rate, podium consistency, qualifying pace, and teammate head-to-head records?
- What composite metric best captures driver skill independent of machinery?

### 3.2 Constructor Dominance & Era Evolution
- Which constructor teams dominated each distinct era of F1 (1950–1970, 1970–1990, 1990–2005, 2005–2014, 2014–Present)?
- What is the operational efficiency (points scored per race entered, podium conversion rate) of top constructor teams?

### 3.3 Driver Contribution vs. Car Advantage (Decomposition)
- Is F1 success primarily driven by the car or driver talent?
- How can statistical variance decomposition and fixed-effects regression quantify the **Driver Impact Score** versus the **Constructor Dominance Score**?

### 3.4 Circuit Dynamics & Characteristics
- Which circuits favor raw horsepower versus high-downforce technical driver skill?
- What is the DNF rate, overtake difficulty, and qualifying-to-win correlation for every circuit?

### 3.5 Race Strategy & Reliability Analytics
- What pit stop durations give optimal track position advantages?
- How has mechanical reliability evolved across eras and engine suppliers?

### 3.6 Machine Learning & Predictive Modeling
- Can we accurately predict race podium probabilities (Top 3 finish) based on grid position, constructor strength, circuit profile, and recent driver form?
- How can unsupervised machine learning cluster driver career trajectories into distinct performance archetypes?

---

## 4. Key Performance Indicators (KPIs)
- **Executive KPIs**: Total Championships, Total Races, Total Drivers, Total Constructors, Total Circuits, Total Countries, Total Race Wins, Average Grid Improvement, Average Finishing Position.
- **Analytical Metrics**:
  - **Driver Performance Score (DPS)**: Composite index (0–100 scale).
  - **Constructor Dominance Index (CDI)**: Team win share and points efficiency per era.
  - **Circuit Difficulty Score (CDS)**: Composite index based on DNF rate, grid position penalty, and track technicality.
  - **Championship Competitiveness Index (CCI)**: Measure of title race closeness per season.
  - **Reliability Score**: DNF-free rate attributable to mechanical failure.

---

## 5. Deliverables Standard
1. **SDD Specifications**: `PROJECT_SPEC.md`, `DATA_ANALYSIS_SPEC.md`, `TECHNICAL_DESIGN.md`, `DASHBOARD_SPEC.md`, `TASKS.md`.
2. **Unified Data Directory (`data/`)**: All 14 raw F1 CSV files gathered in `data/`.
3. **Python Source Core (`src/`)**: Clean, production-ready modules with type hints, data preprocessing, feature engineering, and ML model wrappers.
4. **Jupyter Notebook Suite (`notebooks/`)**: 4 comprehensive analytical notebooks (EDA, Driver/Constructor Analytics, Statistical Modeling, Machine Learning).
5. **Streamlit Interactive Dashboard (`dashboard/`)**: Responsive, multi-page application with F1 dark racing visual aesthetics.
6. **Executive Summary & Documentation (`reports/` & `README.md`)**: Full strategic insights report and repository overview.
