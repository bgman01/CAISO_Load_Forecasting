# CAISO Load Forecasting

## Project Overview

Electricity grids must continuously balance customer demand with available generation and grid resources. The California Independent System Operator (CAISO) coordinates this balance across most of California’s electricity system. 

Demand can change substantially by hour, season, weather conditions, and day of week, making interpretable and accurate forecasts of system load a challenging endeavor. Accurate hourly load forecasts help system operators and energy providers anticipate periods of high demand, schedule generation and market resources, maintain adequate reserves, and plan for variable output from renewables. Forecasting is especially important during heat waves and evening hours, when system demand can be high while solar generation declines.

This project develops and evaluates hourly electricity load forecasting models for the entire CAISO system. Using historical CAISO load (MW), calendar effects, and hourly weather observations from selected California cities, I compared seasonal-naive benchmarks, regression approaches, a regional-level model, and a Random Forest model.

The original forecasting analysis is implemented in Python. I later added a Microsoft Fabric component to work with the same data in OneLake and Warehouse SQL. That work takes the original Excel exports through bronze, silver, and gold tables, then uses SQL for basic data checks and exploration. The forecasting models themselves are still built and evaluated in Python. Weather features were built into the models by pulling data from an open source weather API. Finally, I created Power BI visualizations to explore total and monthly system loads by Time-of-Use Period (TOU), filter by year, month, historical/validation data (source stage), and TOU period. These visuals help inform how variation in hourly patterns can be used to inform a TOU rate design. 

For the initial forecasting model development in Python, 2021–2023 CAISO data was used for training and 2024 was used as a chronological development year for comparing models. After selecting the strongest approaches, the models were retrained using data through 2024 and evaluated against a separate 2025 validation year.

The Random Forest was the best performing model and was evaluated using Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Mean Absolute Percentage Error (MAPE):

- **MAE:** 717 MW
- **RMSE:** 1,012 MW
- **MAPE:** 2.77%

Forecast errors were also analyzed by month, hour, and peak-demand periods to identify where the model succeeds and fails at a more granular level than the aggregate evaluation metrics.

## Data

Hourly CAISO load data from the [CAISO Historical EMS Hourly Load library](https://www.caiso.com/library/historical-ems-hourly-load/) cover 2021–2025 and include total system load plus load for major CAISO service territories:

- Pacific Gas & Electric (PG&E)
- Southern California Edison (SCE)
- San Diego Gas & Electric (SDG&E)
- Valley Electric Association (VEA)

Historical weather data were retrieved from the [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) for several California locations:

- Sacramento
- San Jose
- Fresno
- Los Angeles
- Riverside
- San Diego
- Poway

Hourly temperature observations were merged with CAISO load data by timestamp for the Python modeling analysis.

The data periods have distinct roles throughout the project:

- **Historical period:** 2021–2024. Used for exploratory analysis, model development, and the 2024 comparison year.
- **Validation period:** 2025. Held out from model selection and used for the final evaluation.

## Fabric, SQL, Power BI

I used Fabric to keep the original CAISO Excel files as raw OneLake files, do the basic transformations in SQL, and explore the resulting tables. Finally, I created some Power BI visualizations of various breakdowns of load with different TOU structures.

```text
CAISO Excel exports
    -> OneLake bronze files (unchanged .xlsx files)
    -> Fabric notebook staging CSVs
    -> Warehouse bronze tables
    -> Warehouse silver tables
    -> Warehouse gold feature and summary tables
    -> SQL data-quality checks and exploration
```

## Fabric workflow

1. Original CAISO `.xlsx` exports are placed in separate OneLake folders for historical and validation data:

   ```text
   Files/bronze/loads/historical/
   Files/bronze/loads/validation/
   ```

2. [`01_stage_caiso_load_data_raw.py`](src/notebooks/01_stage_caiso_load_data_raw.py) is run as a Fabric notebook. It reads the Excel exports, adds the originating `source_file`, and writes raw CSV staging copies. It deliberately does not clean or filter the source rows.

3. The two regional-weather CSVs are placed in the corresponding OneLake bronze folders:

   ```text
   Files/bronze/weather/historical/regional_weather_2021_2024.csv
   Files/bronze/weather/validation/regional_weather_2025.csv
   ```

4. The SQL scripts in [`src/sql`](src/sql) are run in this order:

   ```text
   `03_create_schemas.sql` -> Creates the `bronze`, `silver`, and `gold` schemas. 
   `04_load_bronze_caiso_loads.sql` -> Uses `OPENROWSET(BULK...)` to read staging CSVs into raw load tables. 
   `05_load_bronze_weather.sql` -> Uses `OPENROWSET(BULK...)` to read the regional-weather CSVs into raw weather tables. 
   `06_transform_silver_loads.sql` -> Combines historical and validation load rows, removes export footer rows, and applies data types. 
   `07_transform_silver_weather.sql` -> Combines and types the weather data. 
   `08_build_gold_load_features.sql` -> Creates hourly load, calendar, and lag features. 
   `09_build_gold_load_weather.sql` -> Adds weather features where the hourly timestamps are reliable matches. 
   `10_build_gold_daily_summary.sql` -> Creates daily average, minimum, maximum, peak, and rolling average summaries. 
   `11_explore_loads.sql` -> Contains SQL exploration queries. 
   ```

## Power BI Report
The Time-of-Use (TOU) periods in this project were defined as an experimental analytical framework for examining when CAISO system load occurs. They were not derived from a cost-of-service study, real tariffs, or a customer bill analysis.

The structure designates late afternoon and evening hours as 'On-Peak' because system demand is known to be elevated during those periods, particularly when solar generation declines. Overnight and selected midday hours are classified as 'Super Off-Peak' to represent periods that may offer greater opportunity for flexible electricity use when solar generation is high. Remaining hours are classified as 'Off-Peak'.

### TOU periods:
- **On-Peak:** 4-9pm every day (HR ending 17-21)
- **Off-Peak:** weekdays 6am-10am, 2-4pm, 9pm-12am; weekends 2-4pm, 9pm-12am
- **Super Off-Peak:** weekdays 12-6am, 10am-2pm; weekends 12am-2pm

The Power BI report evaluates the resulting load allocation by period, month, and year. This helps assess whether the defined periods capture meaningful differences in observed load patterns.

A production TOU rate design study would require much more additional information, including hourly energy and capacity costs, procurement costs, usage by customer class, revenue requirements, customer bill impacts, affordability considerations, and analysis of customer behavioral responses to rate changes.

[View Power BI report](PowerBI/PowerBI_System-Load-and-TOU.pdf)

### Fabric tables

- **Bronze:** raw files and raw-text Warehouse tables. The original CAISO Excel files stay unchanged in OneLake.
- **Silver:** historical and validation load rows are combined but keep a `source_stage` label. Blank rows and `CAISO Public` footers are removed, and the fields are converted to usable SQL types.
- **Gold:** load features, load-and-weather features, and daily summaries used for analysis.

The first exploration query confirmed the expected complete periods in Fabric:

| Source stage | Hourly rows | Date range |
|---|---:|---|
| Historical | 35,064 | 2021-01-01 to 2024-12-31 |
| Validation | 8,760 | 2025-01-01 to 2025-12-31 |

### Daylight saving time

CAISO has 23 observations on spring daylight-saving days and 25 on fall days, while the weather CSVs have 24 timestamp labels every day. I handled that mismatch as follows:

- `hour_instance` preserves both valid repeated DST transition load observations (days where clocks 'fall back')
- `source_stage` keeps the historical and final validation periods identifiable after they are combined in silver.
- The gold table leaves weather blank on transition dates instead of forcing a questionable match.
- The 24 & 168 he observation lags are previous observations around DST, not necessarily the same clock hour.

This keeps the special dates visible instead of pretending every day has the same number of hours. 

## Exploratory Analysis

As expected, CAISO load displays strong daily and seasonal structure.

![CAISO hourly load](output/Figure_1_load_series.png)

System demand follows a highly repetitive intraday pattern. Average load increases during the morning, exhibits substantial seasonal variation during daytime hours, and rises again toward the evening.

![Average CAISO load by hour](output/Figure_2_average_hourly_load.png)

The shape of the daily load curve also varies significantly by season. Summer months exhibit much stronger afternoon demand, while several winter and spring months show a more pronounced midday decline.

![Average hourly load by month](output/Figure_6_hourly_load_monthly.png)

Monthly peak demand shows substantial yearly variability, including the extreme event on September 6, 2022, when total system load peaked above 51,000 MW.

![Monthly peak CAISO load](output/Figure_7_monthly_peaks.png)

These patterns motivated the use of calendar effects, seasonal interactions, lagged load, and regional weather predictors. I also recreated several of these exploration questions in `11_explore_loads.sql`.

## Time Series Diagnostics

CAISO load exhibits strong temporal dependence.

| Lag | Correlation |
|---:|---:|
| 1 hour | 0.974 |
| 24 hours | 0.929 |
| 48 hours | 0.847 |
| 168 hours | 0.839 |

The particularly strong 24-hour correlation indicates that load from the same hour on the previous day provides substantial information for short-term forecasting. Weekly load also remains highly correlated.

ADF and KPSS stationarity tests produced different conclusions. The ADF test strongly rejected a unit root, while the KPSS test rejected level stationarity. Combined with the ACF and exploratory plots, these results are consistent with a series containing strong deterministic daily, weekly, and seasonal structure.

Daily and weekly lag variables were therefore incorporated directly into the forecasting models.

---

## Forecasting Approach

Model development followed a chronological evaluation design:

**2021–2023 training data → 2024 model comparison → retrain through 2024 → 2025 final validation**

### Seasonal-Naive Benchmarks

Two simple benchmarks were first evaluated:

$$
\hat{L}_t^{(24)} = L_{t-24}
$$

and

$$
\hat{L}_t^{(168)} = L_{t-168}
$$

The 24-hour seasonal-naive forecast substantially outperformed the weekly benchmark and provided the main baseline for evaluating more sophisticated models.

### Regression Models

The first regression models incorporated:

- hour of day
- day of week
- month
- 24-hour lagged load
- 168-hour lagged load

An hour-by-month interaction was then introduced because exploratory analysis showed that the intraday load profile changes substantially across seasons.

Hourly temperature observations were subsequently added to capture weather-related load variation.

### Regional-Level Model

Because California weather and electricity demand vary geographically, separate regression models were developed for the major CAISO service territories.

Regional forecasts used service-territory-specific lagged loads and weather observations from representative cities. The individual regional forecasts were then summed to produce a total CAISO system forecast.

### Random Forest

A Random Forest was used as a nonlinear forecasting model with the following predictors:

- hour
- day of week
- month
- 24-hour load lag
- 168-hour load lag
- hourly temperatures across seven California locations

Unlike the regression models, the Random Forest can capture nonlinear relationships and interactions without explicitly specifying their functional form.

The 24-hour lag was by far the model's most important predictor, consistent with the strong daily autocorrelation observed during the time-series analysis.

## 2024 Model Development Results

Models were compared on 2024 after training on 2021–2023 data.

| Model | MAE (MW) | RMSE (MW) |
|---|---:|---:|
| 168-hour seasonal naive | 1,859 | 2,826 |
| 24-hour seasonal naive | 1,288 | 1,847 |
| Basic OLS | 995 | 1,382 |
| OLS + Hour × Month | 988 | 1,373 |
| OLS + Weather | 954 | 1,302 |
| Regional-Level OLS | 849 | 1,132 |
| Random Forest | 773 | 1,104 |

The Random Forest produced the lowest MAE and RMSE among all models tested. Its MAE was approximately 40% lower than the 24-hour seasonal-naive benchmark.

The regional-level model also performed substantially better than the aggregate weather regression, suggesting that explicitly modeling geographic differences in load and weather provided useful predictive information.

## Final 2025 Validation

After model development, the regional OLS and Random Forest approaches were retrained using data through 2024 and evaluated on the separate 2025 validation year.

| Model | MAE (MW) | RMSE (MW) | MAPE |
|---|---:|---:|---:|
| Regional-Level OLS | 815 | 1,098 | 3.20% |
| Random Forest | 717 | 1,012 | 2.77% |

The Random Forest remained the strongest model on the 2025 validation data, reducing MAE by approximately 12% relative to the regional OLS model.
The model's 2025 performance was also similar to and slightly better than its 2024 comparison year performance, providing evidence that the model generalized well to the following year.

## Forecast Error Analysis

Average forecast accuracy varied considerably by season and hour.

### Error by Month

![Random Forest MAPE by month](output/Figure_14_rf_error_monthly.png)

Monthly MAPE ranged from approximately 2.36% to 3.80%.

- Lowest MAPE: October — 2.36%
- Highest MAPE: March — 3.80%

March and May produced larger errors than most summer and winter months. A possible explanation is that load and weather variability are greater during seasonal transition months and were not fully captured by the model.

### Error by Hour

![Random Forest MAPE by hour](output/Figure_15_rf_mape_hourly.png)

Forecast accuracy was highest overnight and early in the morning. MAPE increased substantially during daytime and afternoon hours.

- Lowest hourly MAPE: 06:00 — **1.60%**
- Highest hourly MAPE: 15:00 — **4.71%**

The model therefore performs substantially better during relatively stable overnight periods than during the more variable daytime load cycle.

### Performance During High-Demand Periods

Across the top 5% of 2025 load hours:

| Metric | Result |
|---|---:|
| Load threshold | 33,963 MW |
| MAE | 1,135 MW |
| RMSE | 1,431 MW |
| MAPE | 3.12% |

Errors increased during high demand periods relative to overall 2025 performance, indicating that extreme load conditions remain more difficult to predict.

The annual system peak occurred on August 21, 2025 at 19:00:

- Actual load: **43,923 MW**
- Random Forest forecast: **40,884 MW**
- Underforecast: **3,039 MW**
- Percentage error: **6.92%**

![Actual vs. Random Forest forecast during 2025 peak week](output/Figure_16_peak_week_forecast.png)

Although the model tracks the overall load pattern during the peak week, the annual maximum illustrates the increased difficulty of accurately forecasting extreme demand.

## Key Findings

1. Recent load is the strongest predictor of short-term CAISO demand. Load at the same hour one day earlier had a correlation of 0.93 with current load and dominated Random Forest feature importance.
2. Adding calendar, seasonal, and weather features improved forecast accuracy by more than 20% compared with a baseline that used the previous day’s same-hour load as the forecast.
3. Weather improves forecast accuracy. Adding hourly temperature observations further reduced both MAE and RMSE.
4. Regional modeling adds predictive value. Modeling major service territories separately produced substantially lower forecast error than a single aggregate weather regression.
5. The Random Forest produced the strongest overall performance. It achieved a 2025 validation MAPE of **2.77%**.
6. Forecast performance deteriorates during the most operationally important periods. Errors were larger during high-demand hours, including a 6.92% underforecast at the 2025 annual system peak.
7. The Fabric work adds a SQL version of the data preparation and exploration steps, using bronze, silver, and gold Warehouse tables.

## Limitations

Models using weather features in this project use realized hourly weather observations rather than weather forecasts available at the time of prediction. The reported results should therefore be interpreted as weather-conditioned forecast performance rather than a complete reconstruction of CAISO's historical day-ahead forecasting methodology.

An operational forecasting system would replace observed future temperatures with weather forecasts available at the time each load forecast is produced and would use more weather stations than the seven representative locations used here.


## Tools

### Forecasting and analysis

- Python
- pandas
- NumPy
- statsmodels
- scikit-learn
- matplotlib
- Open-Meteo API

### MS Fabric, SQL, Power BI extension

- Microsoft Fabric Lakehouse + Warehouse
- SQL 
- Power BI

## Repository Structure

```text
CAISO_load_forecasting/
│
├── data/
│   ├── caiso_loads/
│   │   ├── raw/
│   │   │   ├── historical_data/        #Source CAISO data (2021-2024)
│   │   │   └── validation_data/        #Source CAISO data (2025)
│   │   ├── raw_csv/
│   │   │   ├── historical_data/        #Raw CSV staging files for MS Fabric (2021-2024)
│   │   │   └── validation_data/        #Raw CSV staging files for MS Fabric (2025)
│   │   └── cleaned/
│   │       ├── historical_data/        #Cleaned CAISO data (2021-2024)
│   │       └── validation_data/        #Cleaned CAISO data (2025)
│   └── weather/
│       ├── historical/                 #Weather data (2021-2024)
│       └── validation/                 #Weather data (2025)  
│
├── output/                             #Python exploratory and forecast figures
│  
|
|── PowerBI/ 
|     └── PowerBI_System-Load-and-TOU.pdf       #Power BI visualization PDF output
|
├── src/
│   ├── modeling/                        #Original Python data cleaning, modeling, and evaluation scripts
│   │   ├── 01_clean_raw_loads.py
│   │   ├── 02_EDA.py
│   │   ├── 03_time_series_diagnostics.py
│   │   ├── 04_base_forecasts.py
│   │   ├── 05_econometric_model.py
│   │   ├── 06_weather_input.py
│   │   ├── 07_weather_model.py
│   │   ├── 08_regional_weather_input.py
│   │   ├── 09_regional_model.py
│   │   ├── 10_random_forest_model.py
│   │   ├── 11_validation_cleaning.py
│   │   ├── 12_regional_2025_weather_input.py
│   │   ├── 13_final_validation.py
│   │   └── 14_forecast_error_analysis.py
│   │
│   ├── notebooks/
│   │   └── 01_stage_caiso_load_data_raw.py
│   │
│   └── sql/
│       ├── 01_create_schemas.sql
│       ├── 02_load_bronze_caiso_loads.sql
│       ├── 03_load_bronze_weather.sql
│       ├── 04_transform_silver_loads.sql
│       ├── 05_transform_silver_weather.sql
│       ├── 06_build_gold_load_features.sql
│       ├── 07_build_gold_load_weather.sql
│       ├── 08_build_gold_daily_summary.sql
│       ├── 09_explore_loads.sql
│       └── 10_build_system_tou_summary.sql
│
├── time_series_paper/    #personal academic time series paper covering mathematical foundations of time series as applied to forecasting
│ 
│
└── README.md
```