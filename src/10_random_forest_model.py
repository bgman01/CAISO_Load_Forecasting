from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

project_dir = Path(__file__).resolve().parents[1]
cleaned_file = project_dir / "data" / "caiso_loads" / "cleaned" / "historical_data" / "caiso_load_2021_2024_clean.csv"
weather_file = project_dir / "data" / "weather" / "regional_weather_2021_2024.csv"

historical_load = pd.read_csv(cleaned_file)
weather = pd.read_csv(weather_file)

historical_load["date"] = pd.to_datetime(historical_load["date"])
historical_load["timestamp"] = pd.to_datetime(historical_load["timestamp"])
weather["timestamp"] = pd.to_datetime(weather["timestamp"])

historical_load = historical_load.merge(weather,on="timestamp",how="left")
historical_load = historical_load.sort_values("timestamp", kind="stable").reset_index(drop=True) #sort by timestamp to ensure proper merge with weather data

historical_load["day_of_week"] = historical_load["date"].dt.dayofweek
historical_load["month"] = historical_load["date"].dt.month

historical_load["lag_24"] = historical_load["caiso"].shift(24)
historical_load["lag_168"] = historical_load["caiso"].shift(168)


features = ["hr","day_of_week","month","lag_24","lag_168","temp_sacramento","temp_san_jose","temp_fresno",
    "temp_los_angeles","temp_riverside","temp_san_diego","temp_poway"]


train = historical_load[historical_load["date"].dt.year <= 2023].copy()
test_2024 = historical_load[historical_load["date"].dt.year == 2024].copy()


X_train = train[features]
y_train = train["caiso"]

X_test = test_2024[features]
y_test = test_2024["caiso"]

#random forest model
model_rf = RandomForestRegressor(n_estimators=500,max_depth=15,min_samples_leaf=2,n_jobs=-1,random_state=23)
model_rf.fit(X_train, y_train)

#2024 forecast
test_2024["forecast_rf"] = model_rf.predict(X_test)


#random forest metrics
mae_rf = mean_absolute_error(y_test,test_2024["forecast_rf"])
rmse_rf = np.sqrt(mean_squared_error(y_test,test_2024["forecast_rf"]))

mape_rf = np.mean(np.abs((y_test - test_2024["forecast_rf"])/y_test))*100

print("Random Forest CAISO Model")
print("MAE:", mae_rf)
print("RMSE:", rmse_rf)
print("MAPE:", mape_rf)

feature_importance = pd.Series(model_rf.feature_importances_,index=features).sort_values(ascending=False)
print(feature_importance)