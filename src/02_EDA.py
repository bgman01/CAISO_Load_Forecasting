from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

#use cleaned load data
cleaned_file = Path(r"C:\Users\Brian\Documents\Coding\CAISO_load_forecasting\data\caiso_loads\cleaned\historical_data\caiso_load_2021_2024_clean.csv")

historical_load = pd.read_csv(cleaned_file)
historical_load["timestamp"] = pd.to_datetime(historical_load["timestamp"])  #ensure datetime is preserved 
historical_load["date"] = pd.to_datetime(historical_load["date"])
print(historical_load.head())
print(historical_load.info())

####  FIGURE 1 
#PLOT FULL HOURLY LOAD SERIES 
plt.figure(figsize=(12,5))
plt.plot(historical_load["timestamp"], historical_load["caiso"])
plt.title("CAISO Hourly Load (2021–2024)")
plt.xlabel("Date")
plt.ylabel("Load (MW)")
plt.tight_layout()
plt.show()

#average hourly load
hourly_average = historical_load.groupby("hr")["caiso"].mean()
print(hourly_average)


###FIGURE 2
#PLOT AVERAGE  LOAD by hour - average load shape across all days at given hour

plt.figure(figsize=(12, 5))
plt.plot(hourly_average.index, hourly_average.values)
plt.title("Average CAISO Load by Hour")
plt.xlabel("Hour")
plt.ylabel("Average Load (MW)")
plt.xticks(range(1, 25))
plt.tight_layout()
plt.show()


###FIGURE 3
#PLOT LOAD BY DAY OF WEEK (compare weekday vs weekend)
historical_load["day_of_week"] = historical_load["date"].dt.day_name() #create day of week column
daily_average = historical_load.groupby("day_of_week")["caiso"].mean()
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday", "Sunday"]
daily_average = daily_average.reindex(day_order)
daily_average["Sunday"]
plt.figure(figsize=(12, 5))
plt.bar(daily_average.index, daily_average.values)
plt.title("Average CAISO Load by Day of Week")
plt.xlabel("Day of Week")
plt.ylabel("Average Load (MW)")
plt.ylim(0,27000)
plt.tight_layout()
plt.show()

##FIGURE 4
#INTERACTION OF DAY AND HOUR 
hour_day_average = historical_load.groupby(["day_of_week","hr"])["caiso"].mean().reset_index()
plt.figure(figsize=(12, 6))

for day in day_order:
    day_data = hour_day_average[hour_day_average["day_of_week"] == day]
    plt.plot(day_data["hr"], day_data["caiso"], label=day)

plt.title("Average CAISO Load by Hour and Day of Week")
plt.xlabel("Hour")
plt.ylabel("Average Load (MW)")
plt.xticks(range(1, 25))
plt.legend()

plt.tight_layout()
plt.show()

###FIGURE 5
#SEASSONALITY (ACROSS MONTHS) - average load for each month
historical_load["month"] = historical_load["date"].dt.month
monthly_average = historical_load.groupby("month")["caiso"].mean()
plt.figure(figsize=(12, 5))
plt.bar(monthly_average.index, monthly_average.values)
plt.title("Average CAISO Load by Month")
plt.xlabel("Month")
plt.ylabel("Average Load (MW)")
plt.xticks(range(1, 13))
plt.tight_layout()
plt.show()


###FIGURE 6
#hourly load averages on monthly basis 
monthly_hour_average = historical_load.groupby(["month","hr"])["caiso"].mean().reset_index()
plt.figure(figsize=(12, 6))

for month in range(1, 13):
    month_data = monthly_hour_average[monthly_hour_average["month"] == month]
    plt.plot(month_data["hr"], month_data["caiso"], label=month)

plt.title("Average CAISO Hourly Load by Month")
plt.xlabel("Hour")
plt.ylabel("Average Load (MW)")
plt.xticks(range(1, 25))
plt.legend(title="Month")
plt.tight_layout()
plt.show()

#FIGURE 7
#monthly peak load
historical_load["year"] = historical_load["date"].dt.year #create year column
monthly_peak = historical_load.groupby(["year","month"])["caiso"].max().reset_index()

plt.figure(figsize=(12, 5))
for year in [2021, 2022, 2023, 2024]:
    year_data = monthly_peak[monthly_peak["year"] == year]
    plt.plot(year_data["month"], year_data["caiso"], label=year)

plt.title("Monthly Peak CAISO Load")
plt.xlabel("Month")
plt.ylabel("Peak Load (MW)")
plt.xticks(range(1, 13))
plt.legend(title="Year")
plt.tight_layout()
plt.show()


#FIGURE 8
#daily average load with 30 day rolling average
daily_load = historical_load.groupby("date")["caiso"].mean().reset_index()
daily_load["rolling_30"] = daily_load["caiso"].rolling(30).mean()
plt.figure(figsize=(12, 5))
plt.plot(daily_load["date"], daily_load["caiso"])
plt.plot(daily_load["date"], daily_load["rolling_30"])

plt.title("Average Daily CAISO Load: 2021–2024")
plt.xlabel("Date")
plt.ylabel("Average Load (MW)")
plt.tight_layout()
plt.show()


#investigate the individual hours where peak load occurred each month
peak_indices = historical_load.groupby(["year", "month"])["caiso"].idxmax()
monthly_peak_hours = historical_load.loc[peak_indices, ["year", "month", "date", "hr", "caiso"]]
print(monthly_peak_hours.sort_values("hr"))