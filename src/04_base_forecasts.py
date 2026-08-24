from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#use cleaned load data
project_dir = Path.cwd()
cleaned_file = project_dir / "data" / "caiso_loads" / "cleaned" / "historical_data" / "caiso_load_2021_2024_clean.csv"

historical_load = pd.read_csv(cleaned_file)
historical_load["timestamp"] = pd.to_datetime(historical_load["timestamp"])  #ensure datetime is preserved 
historical_load["date"] = pd.to_datetime(historical_load["date"])

#create 24 and 168 hour lagged loads (seasonal naive forecasts)
historical_load["forecast_24"] = historical_load["caiso"].shift(24)
historical_load["forecast_168"] = historical_load["caiso"].shift(168)

test_2024 = historical_load[historical_load["date"].dt.year == 2024].copy()

mae_24 = mean_absolute_error(test_2024["caiso"], test_2024["forecast_24"])
rmse_24 = np.sqrt(mean_squared_error(test_2024["caiso"], test_2024["forecast_24"]))

mae_168 = mean_absolute_error(test_2024["caiso"], test_2024["forecast_168"])
rmse_168 = np.sqrt(mean_squared_error(test_2024["caiso"],test_2024["forecast_168"]))

print("24-hour baseline")
print("MAE:", mae_24)
print("RMSE:", rmse_24)

print("\n168-hour baseline")
print("MAE:", mae_168)
print("RMSE:", rmse_168)

plot_data = test_2024[
    (test_2024["date"] >= "2024-07-01") &
    (test_2024["date"] <= "2024-07-14")
]

plt.figure(figsize=(12, 5))

plt.plot(
    plot_data["timestamp"],
    plot_data["caiso"],
    label="Actual"
)

plt.plot(
    plot_data["timestamp"],
    plot_data["forecast_24"],
    label="24-hour forecast"
)

plt.plot(
    plot_data["timestamp"],
    plot_data["forecast_168"],
    label="168-hour forecast"
)

plt.title("CAISO Baseline Forecasts — July 2024")
plt.xlabel("Date")
plt.ylabel("Load (MW)")
plt.legend()

plt.tight_layout()
plt.show()