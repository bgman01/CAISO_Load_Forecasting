from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from sklearn.metrics import mean_absolute_error, mean_squared_error

project_dir = Path(__file__).resolve().parents[2]
cleaned_file = project_dir / "data" / "caiso_loads" / "cleaned" / "historical_data" / "caiso_load_2021_2024_clean.csv"
weather_file = project_dir / "data" / "weather" / "historical" / "regional_weather_2021_2024.csv"

historical_load = pd.read_csv(cleaned_file)
weather = pd.read_csv(weather_file)

historical_load["date"] = pd.to_datetime(historical_load["date"])
historical_load["timestamp"] = pd.to_datetime(historical_load["timestamp"])
weather["timestamp"] = pd.to_datetime(weather["timestamp"])

historical_load = historical_load.merge(weather,on="timestamp",how="left")
historical_load = historical_load.sort_values("timestamp", kind="stable").reset_index(drop=True) #sort by timestamp to ensure proper merge with weather data
historical_load["day_of_week"] = historical_load["date"].dt.day_name()
historical_load["month"] = historical_load["date"].dt.month

#create regional load 1 day + 1 week lag variables
historical_load["pge_lag_24"] = historical_load["pge"].shift(24)
historical_load["pge_lag_168"] = historical_load["pge"].shift(168) #pge lagged loads for regional model

historical_load["sce_lag_24"] = historical_load["sce"].shift(24)
historical_load["sce_lag_168"] = historical_load["sce"].shift(168) 

historical_load["sdge_lag_24"] = historical_load["sdge"].shift(24)
historical_load["sdge_lag_168"] = historical_load["sdge"].shift(168)

historical_load["vea_lag_24"] = historical_load["vea"].shift(24)
historical_load["vea_lag_168"] = historical_load["vea"].shift(168)


#create city temperature terms
historical_load["temp_sacramento_sq"] = historical_load["temp_sacramento"]**2
historical_load["temp_san_jose_sq"] = historical_load["temp_san_jose"]**2
historical_load["temp_fresno_sq"] = historical_load["temp_fresno"]**2

historical_load["temp_los_angeles_sq"] = historical_load["temp_los_angeles"]**2
historical_load["temp_riverside_sq"] = historical_load["temp_riverside"]**2

historical_load["temp_san_diego_sq"] = historical_load["temp_san_diego"]**2
historical_load["temp_poway_sq"] = historical_load["temp_poway"]**2



#define training and test dfs
train = historical_load[historical_load["date"].dt.year <= 2023].copy()
test_2024 = historical_load[historical_load["date"].dt.year == 2024].copy()

#pge model
model_pge = smf.ols("""pge ~ C(hr) * C(month) + C(day_of_week) + pge_lag_24 + pge_lag_168 + temp_sacramento
    + temp_sacramento_sq + temp_san_jose + temp_san_jose_sq + temp_fresno + temp_fresno_sq""", data=train).fit()
model_sce = smf.ols("""sce ~ C(hr) * C(month) + C(day_of_week) + sce_lag_24 + sce_lag_168 + temp_los_angeles
    + temp_los_angeles_sq + temp_riverside + temp_riverside_sq""", data=train).fit()
model_sdge = smf.ols("""sdge ~ C(hr) * C(month) + C(day_of_week) + sdge_lag_24 + sdge_lag_168 + temp_san_diego
    + temp_san_diego_sq + temp_poway + temp_poway_sq""", data=train).fit()
model_vea = smf.ols("""vea ~ C(hr) * C(month) + C(day_of_week) + vea_lag_24 + vea_lag_168""", data=train).fit()


test_2024["forecast_pge"] = model_pge.predict(test_2024)
test_2024["forecast_sce"] = model_sce.predict(test_2024)
test_2024["forecast_sdge"] = model_sdge.predict(test_2024)
test_2024["forecast_vea"] = model_vea.predict(test_2024)

mae_pge = mean_absolute_error( test_2024["pge"],test_2024["forecast_pge"])
mae_sce = mean_absolute_error( test_2024["sce"],test_2024["forecast_sce"])
mae_sdge = mean_absolute_error( test_2024["sdge"],test_2024["forecast_sdge"])
mae_vea = mean_absolute_error( test_2024["vea"],test_2024["forecast_vea"])

rmse_pge = np.sqrt(mean_squared_error(test_2024["pge"],test_2024["forecast_pge"]))
rmse_sce = np.sqrt(mean_squared_error(test_2024["sce"],test_2024["forecast_sce"]))
rmse_sdge = np.sqrt(mean_squared_error(test_2024["sdge"],test_2024["forecast_sdge"]))
rmse_vea = np.sqrt(mean_squared_error(test_2024["vea"],test_2024["forecast_vea"]))


test_2024["forecast_regional"] = (test_2024["forecast_pge"] + test_2024["forecast_sce"] + test_2024["forecast_sdge"] + test_2024["forecast_vea"])

#final regional model metrics
mae_regional = mean_absolute_error(test_2024["caiso"],test_2024["forecast_regional"])
rmse_regional = np.sqrt(mean_squared_error(test_2024["caiso"], test_2024["forecast_regional"]))

print("Regional CAISO Model")
print("MAE:", mae_regional)
print("RMSE:", rmse_regional)
