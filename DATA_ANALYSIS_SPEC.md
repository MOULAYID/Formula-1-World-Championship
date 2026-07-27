# DATA ANALYSIS SPECIFICATION: Formula 1 Performance Intelligence Platform

## 1. Data Schema & Relational Structure
The F1 dataset consists of 14 relational tables linked by key identifiers:

```
races (raceId) ──┬── results (resultId, raceId, driverId, constructorId, statusId)
                 ├── qualifying (qualifyId, raceId, driverId, constructorId)
                 ├── pit_stops (raceId, driverId, stop)
                 ├── lap_times (raceId, driverId, lap)
                 └── driver_standings / constructor_standings
drivers (driverId)
constructors (constructorId)
circuits (circuitId)
status (statusId)
```

### Key Field Transformations
- **Time String Parsing**: Convert `time` and `duration` (e.g. `"1:27.452"` or `"23.426"`) to floating-point `milliseconds`.
- **Null Value Standardization**: Convert missing indicators (`\N`) to standard `NaN` / `None`.
- **Status Classification**: Categorize `statusId` into:
  - `Finished`: Completed race (`statusId == 1` or positionText is numeric).
  - `Mechanical DNF`: Engine, gearbox, hydraulics, electrical, turbo failure.
  - `Accident / Collision DNF`: Crash, collision, spin, off track.
  - `Other`: Disqualified, lap down, did not qualify.

---

## 2. Analytical Formulations & Metrics Design

### 2.1 Driver Performance Score (DPS)
To evaluate career greatness across eras without bias from modern long calendars or point system inflation:

$$DPS = w_1 \cdot \text{WinRate} + w_2 \cdot \text{PodiumRate} + w_3 \cdot \text{NormalizedTitleCount} + w_4 \cdot \text{TeammateH2HWinRate} + w_5 \cdot (1 - \text{AvgNormFinish})$$

Where:
- $\text{WinRate} = \frac{\text{Total Wins}}{\text{Total Race Starts}}$
- $\text{PodiumRate} = \frac{\text{Total Podiums}}{\text{Total Race Starts}}$
- $\text{TeammateH2HWinRate} = \frac{\text{Races Finished Ahead of Teammate}}{\text{Races Both Teammate & Driver Finished}}$
- Weights: $w_1 = 0.30$, $w_2 = 0.20$, $w_3 = 0.20$, $w_4 = 0.15$, $w_5 = 0.15$. Scaled to $[0, 100]$.

### 2.2 Driver vs. Car Variance Decomposition
To separate driver skill from car performance:
- **Two-Way Fixed Effects Model**:
  $$Y_{i,j,t} = \mu + \alpha_i (\text{Driver}_i) + \beta_j (\text{Constructor}_j) + \gamma_t (\text{Era}_t) + \varepsilon_{i,j,t}$$
  Where $Y_{i,j,t}$ is the normalized finishing position or points percentage of Driver $i$ in Constructor $j$'s car during Era $t$.
- **Driver Impact Score (DIS)**: Estimated fixed effect $\hat{\alpha}_i$.
- **Constructor Dominance Score (CDS)**: Estimated fixed effect $\hat{\beta}_j$.
- **Teammate Delta Analysis**: Compare intra-team qualifying and race pace differences between paired teammates.

### 2.3 Era Definitions
- **1950–1970**: Early Pioneers & Front-Engine Era
- **1970–1990**: Ground Effect, Turbo Era & Classic Rivalries
- **1990–2005**: High-Tech V10 Era & Schumacher Dominance
- **2005–2014**: V8 Engine Era & Red Bull/Ferrari Battles
- **2014–Present**: Turbo-Hybrid Era & Mercedes/Red Bull Dominance

### 2.4 Circuit Difficulty Score (CDS)
$$CDS = 0.40 \cdot \text{DNF\_Rate} + 0.35 \cdot (1 - \text{Corr}(\text{Grid}, \text{Finish})) + 0.25 \cdot \text{Position\_Variance}$$
- High CDS indicates technical, unforgiving circuits where driver mistake risks are high and grid advantage is less guaranteed.

### 2.5 Championship Competitiveness Index (CCI)
$$CCI = \frac{\text{Unique Race Winners in Season}}{\text{Total Races in Season}} \times \left(1 - \frac{\text{P1 Points} - \text{P2 Points}}{\text{P1 Points}}\right)$$

---

## 3. Statistical Testing Methodology
1. **ANOVA (Analysis of Variance)**: Test whether mean finishing positions differ significantly across driver eras and constructors.
2. **Correlation Analysis**: Spearman rank correlation between qualifying grid position and final race finish across different track types.
3. **Regression Analysis**: Ordinary Least Squares (OLS) regression predicting points per race based on grid start, constructor standing rank, and circuit characteristics.

---

## 4. Machine Learning Specifications

### 4.1 Driver Performance Ranking Model (Supervised Regression)
- **Target**: Driver Performance Score ($DPS$).
- **Features**: Qualifying average rank, overtake ratio, win rate, podium conversion, DNF rate, teammate win percentage, car dominance tier.
- **Algorithms**: Random Forest Regressor, XGBoost Regressor.
- **Evaluation Metrics**: $R^2$, MAE, RMSE, SHAP feature importance analysis.

### 4.2 Race Outcome Prediction (Supervised Classification)
- **Target**: `is_podium` (1 if position $\le 3$, else 0).
- **Features**: Starting grid position, constructor season win rate, driver career podium rate, circuit historical finish, qualifying time gap to pole, recent 5-race form.
- **Algorithms**: Logistic Regression, Random Forest Classifier, XGBoost Classifier.
- **Evaluation Metrics**: ROC-AUC, Precision, Recall, F1-Score, Confusion Matrix.

### 4.3 Driver Clustering (Unsupervised Machine Learning)
- **Target**: Discover natural groupings of driver career archetypes.
- **Features**: Career starts, win percentage, podium percentage, points per start, DNF percentage, qualifying average position.
- **Algorithms**: K-Means Clustering (Elbow & Silhouette optimization), Agglomerative Hierarchical Clustering.
- **Clusters**:
  1. *Championship Legends*
  2. *Consistent Podium Contenders*
  3. *Mid-Field Workhorses*
  4. *Short-Career / One-Season Performers*
