from pathlib import Path
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller, kpss
import pandas as pd
import matplotlib.pyplot as plt

#use cleaned load data
project_dir = Path(__file__).resolve().parents[1]
cleaned_file = project_dir / "data" / "caiso_loads" / "cleaned" / "historical_data" / "caiso_load_2021_2024_clean.csv"

historical_load = pd.read_csv(cleaned_file)
historical_load["timestamp"] = pd.to_datetime(historical_load["timestamp"])  #ensure datetime is preserved 
historical_load["date"] = pd.to_datetime(historical_load["date"])

#investigate correlations between lags at 1hr, 24 hours, 48 hours, 168 hours (1 week)
print("Lag 1:", historical_load["caiso"].corr(historical_load["caiso"].shift(1)))
print("Lag 24:", historical_load["caiso"].corr(historical_load["caiso"].shift(24)))
print("Lag 48:", historical_load["caiso"].corr(historical_load["caiso"].shift(48)))
print("Lag 168:", historical_load["caiso"].corr(historical_load["caiso"].shift(168)))

#FIGURE 9
#ACF for hourly load lags
plot_acf(historical_load["caiso"],lags=200)

plt.title("ACF of CAISO Hourly Load")
plt.xlabel("Lag (Hours)")
plt.ylabel("Autocorrelation")
plt.tight_layout()
plt.show()


#FIGURE 10
#PACF for hourly load lags
plot_pacf(historical_load["caiso"], lags=60)

plt.title("PACF of CAISO Hourly Load")
plt.xlabel("Lag (Hours)")
plt.ylabel("Partial Autocorrelation")
plt.tight_layout()
plt.show()


#Augmented Dickey Fuller (ADF) test for stationarity - key assumption to using time series models is that the series is stationary 
#we need to guarantee that there is no unit root (i.e stochastic)
#can potentially manipulate the series to achieve stationarity (i.e. differencing)
#ADF hypotheses: H_0: Series is nonstationary (unit root) vs. H_A: Series does not have a unit root
adf_result = adfuller(historical_load["caiso"])

print("ADF Statistic:", adf_result[0])
print("p-value:", adf_result[1])

#Kwiatkowski–Phillips–Schmidt–Shin (KPSS) test for stationarity
#KPSS hypothesis (REVERSE of ADF test): H0: Series is stationary vs H_A: Series has a unit root
kpss_result = kpss(historical_load["caiso"], regression="c", nlags="auto")

print("KPSS Statistic:", kpss_result[0])
print("p-value:", kpss_result[1])

#check differenced load (Load_{t} - Load_{t-24}) 
#differencing can sometimes help give us a stationary series
#FIGURE 11: 24 HOUR DIFFERENCED ACF
historical_load["diff_24"] = historical_load["caiso"].diff(24)
print(historical_load[["date", "hr", "caiso", "diff_24"]].head(30))
plt.figure(figsize=(12, 5))
plot_acf(historical_load["diff_24"].dropna(), lags=200)

plt.title("ACF of 24-Hour Differenced CAISO Load")
plt.xlabel("Lag (Hours)")
plt.ylabel("Autocorrelation")
plt.tight_layout()
plt.show()

#check differenced load (Load_{t} - Load_{t-168}) 
#FIGURE 12: 168 HOUR DIFFERENCED ACF
historical_load["diff_168"] = historical_load["caiso"].diff(168)
plt.figure(figsize=(12, 5))
plot_acf(historical_load["diff_168"].dropna(), lags=200)

plt.title("ACF of 168-Hour Differenced CAISO Load")
plt.xlabel("Lag (Hours)")
plt.ylabel("Autocorrelation")
plt.tight_layout()
plt.show()