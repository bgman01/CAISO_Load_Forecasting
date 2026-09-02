from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

project_dir = Path(__file__).resolve().parents[2]
cleaned_file = project_dir / "data" / "caiso_loads" / "cleaned" / "historical_data" / "caiso_load_2021_2024_clean.csv"
cleaned_validation = project_dir / "data" / "caiso_loads" / "cleaned" / "validation_data" / "caiso_load_2025_clean.csv"
weather_file = project_dir / "data" / "weather" / "historical" / "regional_weather_2021_2024.csv"
validation_weather_file = project_dir / "data" / "weather" / "validation" / "regional_weather_2025.csv"

#load all data
historical_load = pd.read_csv(cleaned_file)
validation_load = pd.read_csv(cleaned_validation)
historical_weather = pd.read_csv(weather_file)
validation_weather = pd.read_csv(validation_weather_file)

#combine load and weather data (first fix datetime mismatch happening between 2021-2024 and 2025 data)
historical_load["date"] = pd.to_datetime(historical_load["date"],format="mixed")
validation_load["date"] = pd.to_datetime(validation_load["date"],format="mixed")
historical_load["timestamp"] = pd.to_datetime(historical_load["timestamp"],format="mixed")
validation_load["timestamp"] = pd.to_datetime(validation_load["timestamp"],format="mixed")
historical_weather["timestamp"] = pd.to_datetime(historical_weather["timestamp"],format="mixed")
validation_weather["timestamp"] = pd.to_datetime(validation_weather["timestamp"],format="mixed")

all_load = pd.concat([historical_load, validation_load],ignore_index=True)
all_weather = pd.concat([historical_weather, validation_weather],ignore_index=True)


#merge load and weather
all_load = all_load.merge(all_weather,on="timestamp",how="left")
all_load = all_load.sort_values("timestamp",kind="stable").reset_index(drop=True)

#define variables
all_load["day_of_week"] = all_load["date"].dt.dayofweek
all_load["month"] = all_load["date"].dt.month

all_load["lag_24"] = all_load["caiso"].shift(24)
all_load["lag_168"] = all_load["caiso"].shift(168)

all_load["pge_lag_24"] = all_load["pge"].shift(24)
all_load["pge_lag_168"] = all_load["pge"].shift(168)

all_load["sce_lag_24"] = all_load["sce"].shift(24)
all_load["sce_lag_168"] = all_load["sce"].shift(168)

all_load["sdge_lag_24"] = all_load["sdge"].shift(24)
all_load["sdge_lag_168"] = all_load["sdge"].shift(168)

all_load["vea_lag_24"] = all_load["vea"].shift(24)
all_load["vea_lag_168"] = all_load["vea"].shift(168)


#define quadratic temp terms
all_load["temp_sacramento_sq"] = all_load["temp_sacramento"]**2
all_load["temp_san_jose_sq"] = all_load["temp_san_jose"]**2
all_load["temp_fresno_sq"] = all_load["temp_fresno"]**2

all_load["temp_los_angeles_sq"] = all_load["temp_los_angeles"]**2
all_load["temp_riverside_sq"] = all_load["temp_riverside"]**2

all_load["temp_san_diego_sq"] = all_load["temp_san_diego"]**2
all_load["temp_poway_sq"] = all_load["temp_poway"]**2


#train and test splits
train = all_load[all_load["date"].dt.year <= 2024].copy()
test_2025 = all_load[all_load["date"].dt.year == 2025].copy()

#specify same regional ols models from before
model_pge = smf.ols("""pge ~ C(hr) * C(month) + C(day_of_week) + pge_lag_24 + pge_lag_168 + temp_sacramento
    + temp_sacramento_sq + temp_san_jose + temp_san_jose_sq + temp_fresno + temp_fresno_sq""", data=train).fit()
model_sce = smf.ols("""sce ~ C(hr) * C(month) + C(day_of_week) + sce_lag_24 + sce_lag_168 + temp_los_angeles
    + temp_los_angeles_sq + temp_riverside + temp_riverside_sq""", data=train).fit()
model_sdge = smf.ols("""sdge ~ C(hr) * C(month) + C(day_of_week) + sdge_lag_24 + sdge_lag_168 + temp_san_diego
    + temp_san_diego_sq + temp_poway + temp_poway_sq""", data=train).fit()
model_vea = smf.ols("""vea ~ C(hr) * C(month) + C(day_of_week) + vea_lag_24 + vea_lag_168""", data=train).fit()


#2025 forecasts
test_2025["forecast_pge"] = model_pge.predict(test_2025)
test_2025["forecast_sce"] = model_sce.predict(test_2025)
test_2025["forecast_sdge"] = model_sdge.predict(test_2025)
test_2025["forecast_vea"] = model_vea.predict(test_2025)
test_2025["forecast_regional"] = (test_2025["forecast_pge"] + test_2025["forecast_sce"] + test_2025["forecast_sdge"] + test_2025["forecast_vea"])

#regional model evaluation metrics
mae_regional = mean_absolute_error(test_2025["caiso"], test_2025["forecast_regional"])
rmse_regional = np.sqrt(mean_squared_error( test_2025["caiso"], test_2025["forecast_regional"]))
mape_regional = np.mean(np.abs((test_2025["caiso"]-test_2025["forecast_regional"])/test_2025["caiso"]))*100

#random forest model
features = ["hr","day_of_week","month","lag_24","lag_168","temp_sacramento","temp_san_jose","temp_fresno",
    "temp_los_angeles","temp_riverside","temp_san_diego","temp_poway"]

rf_train = train.dropna(subset=features).copy()
rf_test = test_2025.dropna(subset=features).copy()

X_train = rf_train[features]
y_train = rf_train["caiso"]

X_test = rf_test[features]
y_test = rf_test["caiso"]

model_rf = RandomForestRegressor(n_estimators=500,max_depth=15,min_samples_leaf=2,n_jobs=-1,random_state=23)

model_rf.fit(X_train, y_train)
rf_test["forecast_rf"] = model_rf.predict(X_test)

#random forest evaluation metrics
mae_rf = mean_absolute_error(y_test, rf_test["forecast_rf"])
rmse_rf = np.sqrt(mean_squared_error(y_test,rf_test["forecast_rf"]))
mape_rf = np.mean(np.abs((y_test-rf_test["forecast_rf"])/y_test))*100

print("2025 FINAL VALIDATION")

print("Regional OLS")
print("MAE:", mae_regional)
print("RMSE:", rmse_regional)
print("MAPE:", mape_regional)

print("Random Forest")
print("MAE:", mae_rf)
print("RMSE:", rmse_rf)
print("MAPE:", mape_rf)

#add RF forecast to 2025 load dataframe
test_2025.loc[rf_test.index, "forecast_rf"] = rf_test["forecast_rf"]
results_file = (project_dir  / "data" / "caiso_loads" / "cleaned" / "validation_data" / "caiso_forecasts_2025.csv")
test_2025.to_csv(results_file, index=False)
