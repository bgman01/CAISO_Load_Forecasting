from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

project_dir = Path(__file__).resolve().parents[1]
results_file = (project_dir  / "data" / "caiso_loads" / "cleaned" / "validation_data" / "caiso_forecasts_2025.csv")
results = pd.read_csv(results_file)

results["date"] = pd.to_datetime(results["date"])
results["timestamp"] = pd.to_datetime(results["timestamp"])

results["error_rf"] = (results["caiso"] - results["forecast_rf"]) #positive error = underforecast, negative error = overforecast
results["abs_error_rf"] = (results["error_rf"].abs())
results["ape_rf"] = (results["abs_error_rf"]/results["caiso"])*100 

#look at errors by month
results["month"] = results["date"].dt.month
monthly_error = (results.groupby("month").agg(mae=("abs_error_rf", "mean"), mape=("ape_rf", "mean"), rmse=("error_rf", lambda x: np.sqrt(np.mean(x**2)))))
print(monthly_error)

#FIGURE 14: RF ERRORS (MAPE) MONTHLY
monthly_error["mape"].plot(kind="bar")
plt.ylabel("MAPE (%)")
plt.xlabel("Month")
plt.title("Random Forest Forecast Error by Month - 2025")
plt.tight_layout()
plt.show()

#look at errors by hour
hourly_error = (results.groupby("hr").agg(mae=("abs_error_rf", "mean"),mape=("ape_rf", "mean")))
print(hourly_error)

hourly_error["mape"].plot()
#FIGURE 15: RF ERRORS (MAPE) HOURLY
plt.ylabel("MAPE (%)")
plt.xlabel("Hour")
plt.title("Random Forest MAPE by Hour - 2025")
plt.xticks(range(1, 25))
plt.tight_layout()
plt.show()

#look at errors for highest load periods (within top 5%)
peak_threshold = results["caiso"].quantile(0.95)
peak_hours = results[results["caiso"] >= peak_threshold].copy()
peak_mae = peak_hours["abs_error_rf"].mean()
peak_rmse = np.sqrt(np.mean(peak_hours["error_rf"]**2))
peak_mape = peak_hours["ape_rf"].mean()

print("Top 5% Load Hours")
print("Load threshold:", peak_threshold)
print("MAE:", peak_mae)
print("RMSE:", peak_rmse)
print("MAPE:", peak_mape)



#FIGURE 16: ACTUAL VS RF FORECASTS FOR 2025 PEAK WEEK
peak_index = results["caiso"].idxmax()
peak_date = results.loc[peak_index, "date"]
peak_load = results.loc[peak_index, "caiso"]
peak_hour = results.loc[peak_index, "hr"]

print("2025 Peak Date:", peak_date)
print("2025 Peak Hour:", peak_hour)
print("2025 Peak Load:", peak_load)
plot_start = peak_date - pd.Timedelta(days=3)
plot_end = peak_date + pd.Timedelta(days=3)

peak_week = results[(results["date"] >= plot_start) & (results["date"] <= plot_end)].copy()
plt.figure(figsize=(12, 5))

plt.plot(peak_week["timestamp"],peak_week["caiso"],label="Actual")
plt.plot(peak_week["timestamp"],peak_week["forecast_rf"],label="Random Forest Forecast")
plt.xlabel("Date")
plt.ylabel("CAISO Load (MW)")
plt.title("Actual vs. Random Forest Forecast at 2025 Peak Week")
plt.legend()
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

peak_forecast = results.loc[peak_index, "forecast_rf"]
peak_error = peak_load-peak_forecast
peak_error_pct = abs(peak_error)/peak_load * 100

print("Forecast at Peak:", peak_forecast)
print("Peak Error (MW):", peak_error)
print("Peak Error (%):", peak_error_pct)