from pathlib import Path
import pandas as pd
import requests

project_dir = Path(__file__).resolve().parents[2]
cleaned_file = project_dir / "data" / "caiso_loads" / "cleaned" / "historical_data" / "caiso_load_2021_2024_clean.csv"
historical_load = pd.read_csv(cleaned_file)
historical_load["date"] = pd.to_datetime(historical_load["date"])
historical_load["timestamp"] = pd.to_datetime(historical_load["timestamp"])

#use open-meteo data (free access weather API)
cities = {
    "sacramento": (38.58, -121.49),
    "san_jose": (37.33, -121.91),
    "los_angeles": (34.05, -118.24),
    "san_diego": (32.76, -117.17)
}

weather_data = []

for city, coordinates in cities.items():
    latitude = coordinates[0]
    longitude = coordinates[1]
    url = "https://archive-api.open-meteo.com/v1/archive"

    #collect weather data based on lat long within date range for every hour, temp 2m above surface
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": "2021-01-01",
        "end_date": "2024-12-31",
        "hourly": "temperature_2m",
        "temperature_unit": "fahrenheit",
        "timezone": "America/Los_Angeles"
    }

    response = requests.get(url, params=params)
    data = response.json()

    #create city level weather df
    city_weather = pd.DataFrame({
        "timestamp": data["hourly"]["time"],
        f"temp_{city}": data["hourly"]["temperature_2m"]
    })

    #add timestamp to city df
    city_weather["timestamp"] = pd.to_datetime(city_weather["timestamp"])
    weather_data.append(city_weather)

   
weather = weather_data[0]

#combine cities into master weather df
for city_weather in weather_data[1:]:
    weather = weather.merge(city_weather, on="timestamp", how="outer")

print(weather.head())
print(weather.shape)
print(weather.isna().sum())


weather_file = project_dir / "data" / "weather" / "historical" / "california_weather_2021_2024.csv"
weather.to_csv(weather_file, index=False)

print(f"Saved weather data to: {weather_file}")

print("Duplicate timestamps:", historical_load["timestamp"].duplicated().sum())
duplicates = historical_load[historical_load["timestamp"].duplicated(keep=False)].sort_values("timestamp")
print(duplicates[["timestamp", "date", "hr", "caiso"]])

weather_duplicates = weather[weather["timestamp"].duplicated(keep=False)].sort_values("timestamp")
print(weather_duplicates)
