from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parents[2]
historical_dir = project_dir / "data" / "caiso_loads" / "raw" / "historical_data"
cleaned_dir = project_dir / "data" / "caiso_loads" / "cleaned" / "historical_data"

files = sorted(historical_dir.glob("*.xlsx"))

dataframes = [] 
for file in files:
    df = pd.read_excel(file) #read current excel file
    df["source_file"] = file.name
    dataframes.append(df) #df with all excels

historical_load = pd.concat(
    dataframes, #concatenate all files into one historical_load dataframe
    ignore_index=True
)

#initial inspection
print(historical_load.shape)
print(historical_load.columns)
print(historical_load.head())
print(historical_load.tail())
historical_load.info()
print(historical_load.isna().sum())

#CHECK DATES -> normalize column names and check date data type
historical_load.columns = historical_load.columns.str.strip().str.lower()
print(historical_load["date"].dtype)
print(historical_load["date"].head(20))

invalid_dates = historical_load[historical_load["date"].isna()]
print(invalid_dates) #looks like dates are entirely empty rows, can safely remove them
historical_load = historical_load.dropna(subset=["date"])
print(historical_load.isna().sum()) #still missing values for other columns

missing_rows = historical_load[historical_load[["hr", "pge", "sce", "sdge", "vea", "caiso"]].isna().any(axis=1)]
print(missing_rows) #looks like a stray 'CAISO Public' footer is at the bottom of these 2024 datasets, can confidently remove
historical_load = historical_load[historical_load["date"] != "CAISO Public"]
print(historical_load.isna().sum())

historical_load["date"] = pd.to_datetime(historical_load["date"]) #standardize date
print(historical_load["date"].min())
print(historical_load["date"].max()) #date ranges are good, all of 2021 to 2024

#CHECK TIME (HR) COLUMNS
print(sorted(historical_load["hr"].unique()))
print(historical_load["hr"].value_counts().sort_index()) #hrs 1 has 1465 unique values, hrs 2 has 1457 corresponding with DST jumps across 4 years

#CHECK IOU + CAISO columns + descriptive stats
iou_columns = ["pge", "sce", "sdge", "vea", "caiso"]
print(historical_load[iou_columns].describe()) #as expected, loads dominated by PG&E and SCE, with SDG&E being about 9% of loads and VEA (Valley Electric Association) <1% 
print((historical_load[iou_columns] <= 0).sum())

#create single timestamp column combining date + time e.g. '2024-05-13 13:00'
historical_load["timestamp"] = historical_load["date"] + pd.to_timedelta(historical_load["hr"] - 1, unit="h")
historical_load = historical_load.sort_values("timestamp")
print(historical_load[["date", "hr", "timestamp"]].head(30))

#convert historical_load to clean csv and export
historical_load.to_csv(cleaned_dir / "caiso_load_2021_2024_clean.csv", index=False)