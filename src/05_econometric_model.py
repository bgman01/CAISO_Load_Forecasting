from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

from sklearn.metrics import mean_absolute_error, mean_squared_error
#use cleaned load data
cleaned_file = Path(r"C:\Users\Brian\Documents\Coding\CAISO_load_forecasting\data\caiso_loads\cleaned\historical_data\caiso_load_2022_2024_clean.csv")
historical_load = pd.read_csv(cleaned_file)

historical_load["date"] = pd.to_datetime(historical_load["date"])
historical_load["timestamp"] = pd.to_datetime(historical_load["timestamp"])  #ensure datetime is preserved 
historical_load["day_of_week"] = historical_load["date"].dt.day_name()
historical_load["month"] = historical_load["date"].dt.month
historical_load["lag_24"] = historical_load["caiso"].shift(24)
historical_load["lag_168"] = historical_load["caiso"].shift(168)

#split 2024 out of training data (use 2024 as test year on model build from 2021-2023)
train = historical_load[historical_load["date"].dt.year <= 2023].copy()
test_2024 = historical_load[historical_load["date"].dt.year == 2024].copy()

train = train.dropna(subset=["lag_24", "lag_168"])
test_2024 = test_2024.dropna(subset=["lag_24", "lag_168"])

#no interaction term model
model = smf.ols("caiso ~ C(hr) + C(day_of_week) + C(month) + lag_24 + lag_168", data=train).fit() #caiso as response, C(hr) + C(day) + C(month) as categorical
test_2024["forecast_regression"] = model.predict(test_2024)

mae_regression = mean_absolute_error(test_2024["caiso"], test_2024["forecast_regression"])
rmse_regression = np.sqrt(mean_squared_error(test_2024["caiso"],test_2024["forecast_regression"]))

print("Regression Model")
print("MAE:", mae_regression)
print("RMSE:", rmse_regression)

#interaction term on hr*month included since we know load shape changes with season
model_interaction = smf.ols("caiso ~ C(hr) * C(month) + C(day_of_week) + lag_24 + lag_168", data=train).fit()
test_2024["forecast_interaction"] = model_interaction.predict(test_2024)

mae_interaction = mean_absolute_error(test_2024["caiso"], test_2024["forecast_interaction"])
rmse_interaction = np.sqrt(mean_squared_error(test_2024["caiso"],test_2024["forecast_interaction"]))

print("Interaction Model")
print("MAE:", mae_interaction)
print("RMSE:", rmse_interaction)