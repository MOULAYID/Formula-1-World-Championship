# DASHBOARD SPECIFICATION: Formula 1 Performance Intelligence Platform

## 1. Design System & Visual Identity

### 1.1 Aesthetic Theme: Formula 1 Racing Aesthetics
- **Color Palette**:
  - Primary Brand Red: `#E10600` (Official F1 Red)
  - Dark Background: `#0B0E14` (Deep Night Carbon)
  - Card / Container Background: `#151922` (Sleek Dark Slate)
  - Border Color: `#232A36`
  - Text Primary: `#FFFFFF`
  - Text Secondary: `#94A3B8` (Muted Slate)
  - Accent Gold (Championships): `#FFD700`
  - Accent Cyan / Blue (Telemetry): `#00D2BE` (Mercedes Petrol Green/Cyan)
  - Accent Orange (McLaren/Speed): `#FF8700`
- **Typography**: Clean modern sans-serif (`Inter`, `Titillium Web`, system sans-serif).
- **Styling Elements**: Glassmorphism cards, glowing metric badges, subtle red accent top-borders.

---

## 2. Multi-Page Structure & Layout Wireframes

```
+-----------------------------------------------------------------------+
|  🏎️ FORMULA 1 PERFORMANCE INTELLIGENCE PLATFORM           [Dark Mode] |
+-----------------------------------------------------------------------+
| SIDEBAR NAV    | MAIN DASHBOARD CONTENT AREA                          |
| -------------- | ---------------------------------------------------  |
| 🏠 Home        | [ Executive KPI Row ]                                |
| 🏎️ Drivers     | [ KPI 1 | KPI 2 | KPI 3 | KPI 4 | KPI 5 | KPI 6 ]    |
| 🏁 Constructors| ---------------------------------------------------  |
| 🗺️ Circuits    | [ Main Chart / Interactive Filters ]                 |
| 📊 Race Analytics| [ Secondary Insights & Tables ]                    |
| ⏱️ Strategy    |                                                      |
| 🔮 Predictions |                                                      |
+-----------------------------------------------------------------------+
```

---

## 3. Page Specifications

### Page 1: 🏠 Home (Executive Overview)
- **KPI Bar**: Total Championships, Total Races, Total Drivers, Total Constructors, Total Circuits, Total Countries, Total Race Wins, Avg Grid Improvement, Avg Finish.
- **Visualizations**:
  - *F1 70-Year Evolution Line Chart*: Race count and unique winners by season.
  - *Dominant Eras Timeline*: Bar chart of constructor wins grouped by historical era.
  - *Executive Summary Insights Card*: Strategic narrative highlighting F1 development key points.

### Page 2: 🏎️ Drivers (Driver Performance & GOAT Analysis)
- **Interactive Controls**: Multi-driver search dropdown, Era filter, Start threshold slider (min 20 starts).
- **Visualizations**:
  - *The GOAT Debate Matrix*: Scatter plot comparing Driver Performance Score vs. Career Win Percentage.
  - *Legend Radar Chart*: 5-axis radar chart comparing selected drivers (Win %, Podium %, Pole %, Teammate H2H %, DPS).
  - *Career Trajectory Line*: Cumulative wins and points trajectory by career start index.
  - *Driver Ranking Leaderboard*: Ranked table with Driver Performance Score and career stats.

### Page 3: 🏁 Constructors (Team Dominance & Era Analytics)
- **Visualizations**:
  - *Constructor Championship Leaderboard*: Total titles and wins for Ferrari, Mercedes, Red Bull, McLaren, Williams, Lotus.
  - *Era Dominance Breakdown*: Stacked area chart showing market share of wins per era.
  - *Constructor Efficiency Matrix*: Points per race vs. DNF reliability rate scatter plot.

### Page 4: 🗺️ Circuits (Track Difficulty & Characteristics Map)
- **Visualizations**:
  - *Global Circuit Map*: Interactive Plotly scatter_mapbox showing circuit locations, country, lat/long, and total races hosted.
  - *Circuit Difficulty Score Leaderboard*: Ranked bar chart of tracks by Circuit Difficulty Score.
  - *Qualifying Position Impact*: Bar chart of win percentage from Pole Position per circuit.

### Page 5: 📊 Race Analytics (Qualifying vs. Race Performance)
- **Visualizations**:
  - *Grid Position vs. Race Finish Scatter*: Correlation plot with linear trendlines.
  - *Positions Gained Heatmap*: Grid start position vs. average positions gained/lost.
  - *Overcoming Bad Qualifying*: Drivers with highest average position gains on race day.

### Page 6: ⏱️ Strategy (Pit Stop Pace & Reliability Analysis)
- **Visualizations**:
  - *Pit Stop Duration Evolution*: Box plots of pit stop durations by season (2011–Present).
  - *Team Pit Stop Benchmark*: Average pit stop time by constructor team.
  - *DNF Breakdown Donut Chart*: Mechanical failures vs. collisions vs. driver errors across eras.

### Page 7: 🔮 Predictions (ML Driver Ranking & Podium Predictor)
- **Interactive Features**:
  - *Live Podium Predictor Form*: Select Starting Grid Position, Constructor Team, Driver, Circuit, and Recent Form to output Top-3 Podium Probability %.
  - *Driver Performance Score Predictor*: Input driver career statistics to estimate predicted Driver Performance Score.
  - *SHAP / Feature Importance Plot*: Visual breakdown of factors influencing the machine learning predictions.
  - *Driver Clustering Profiles*: Visual 2D PCA/TSNE plot of driver career clusters (*Legends*, *Consistent*, *Workhorses*, *One-Season Performers*).
