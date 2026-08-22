from pathlib import Path
import pandas as pd
import requests

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
        "end_date": "2025-12-31",
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

weather_file = Path(r"C:\Users\Brian\Documents\Coding\CAISO_load_forecasting\data\weather\california_weather_2021_2025.csv")
weather.to_csv(weather_file, index=False)

weather = pd.read_csv(weather_file)
weather["timestamp"] = pd.to_datetime(weather["timestamp"])
historical_load = historical_load.merge(
    weather,
    on="timestamp",
    how="left"
)