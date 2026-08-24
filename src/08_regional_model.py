from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import requests
from sklearn.metrics import mean_absolute_error, mean_squared_error

project_dir = Path.cwd()
cleaned_file = project_dir / "data" / "caiso_loads" / "cleaned" / "historical_data" / "caiso_load_2021_2024_clean.csv"
weather_file = project_dir / "data" / "weather" / "california_weather_2021_2024.csv"
historical_load = pd.read_csv(cleaned_file)
weather = pd.read_csv(weather_file)

#check that sum of individual areas matches total CAISO load
historical_load["area_sum"] = (historical_load["pge"]+ historical_load["sce"] + historical_load["sdge"]+ historical_load["vea"])
historical_load["area_difference"] = (historical_load["caiso"] - historical_load["area_sum"])
print(historical_load["area_difference"].describe())

cities = {
    "sacramento": (38.58, -121.49),
    "san_jose": (37.33, -121.91),
    "fresno": (36.74, -119.79), #PGE

    "los_angeles": (34.05, -118.24), #SCE
    "riverside": (33.98, -117.38),

    "san_diego": (32.76, -117.17), #SDGE
    "poway": (32.96, -117.04)
}

historical_load = historical_load.sort_values("timestamp", kind="stable").reset_index(drop=True) #sort by timestamp to ensure proper merge with weather data
historical_load["day_of_week"] = historical_load["date"].dt.day_name()
historical_load["month"] = historical_load["date"].dt.month
weather["timestamp"] = pd.to_datetime(weather["timestamp"])

historical_load = historical_load.merge(weather, left_on="timestamp", right_on="timestamp", how="left")

historical_load["pge_lag_24"] = historical_load["pge"].shift(24)
historical_load["pge_lag_168"] = historical_load["pge"].shift(168) #pge lagged loads for regional model

historical_load["temp_sacramento_sq"] = historical_load["temp_sacramento"] ** 2
historical_load["temp_san_jose_sq"] = historical_load["temp_san_jose"] ** 2
historical_load["temp_fresno_sq"] = historical_load["temp_fresno"] ** 2

train = historical_load[historical_load["date"].dt.year <= 2023].copy()
test_2024 = historical_load[historical_load["date"].dt.year == 2024].copy()

model_pge = smf.ols(
    """pge ~ C(hr) * C(month)
    + C(day_of_week)
    + pge_lag_24
    + pge_lag_168
    + temp_sacramento
    + temp_sacramento_sq
    + temp_san_jose
    + temp_san_jose_sq
    + temp_fresno
    + temp_fresno_sq""",
    data=train
).fit()

test_2024["forecast_pge"] = model_pge.predict(test_2024)

mae_pge = mean_absolute_error(
    test_2024["pge"],
    test_2024["forecast_pge"]
)

rmse_pge = np.sqrt(
    mean_squared_error(
        test_2024["pge"],
        test_2024["forecast_pge"]
    )
)

print("PG&E Weather Model")
print("MAE:", mae_pge)
print("RMSE:", rmse_pge)