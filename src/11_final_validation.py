from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
validation_dir = project_dir / "data" / "caiso_loads" / "raw" / "validation_data"
cleaned_validation = project_dir / "data" / "caiso_loads" / "cleaned" / "validation_data"

files = sorted(validation_dir.glob("*.xlsx"))

dataframes = [] 
for file in files:
    df = pd.read_excel(file) #read current excel file
    df["source_file"] = file.name
    dataframes.append(df) #df with all excels

validation_load = pd.concat(
    dataframes, 
    ignore_index=True
)

validation_load.columns = validation_load.columns.str.strip().str.lower()
invalid_dates = validation_load[validation_load["date"].isna()]
validation_load = validation_load[validation_load["date"] != "CAISO Public"]
validation_load = validation_load.dropna(subset=["date"])

validation_load["date"] = pd.to_datetime(validation_load["date"])

validation_load["timestamp"] = validation_load["date"] + pd.to_timedelta(validation_load["hr"] - 1, unit="h")
validation_load = validation_load.sort_values("timestamp")

validation_load.to_csv(cleaned_validation / "caiso_load_2025_clean.csv", index=False)

validation_load = pd.read_csv(cleaned_file)
weather = pd.read_csv(weather_file)







validation_load["date"] = pd.to_datetime(validation_load["date"])
validation_load["timestamp"] = pd.to_datetime(validation_load["timestamp"])
weather["timestamp"] = pd.to_datetime(weather["timestamp"])

validation_load = validation_load.merge(weather,on="timestamp",how="left")
validation_load = validation_load.sort_values("timestamp", kind="stable").reset_index(drop=True) #sort by timestamp to ensure proper merge with weather data

validation_load["day_of_week"] = validation_load["date"].dt.dayofweek
validation_load["month"] = validation_load["date"].dt.month