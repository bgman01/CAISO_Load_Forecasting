--preview the historical weather file
SELECT TOP 10 *
FROM OPENROWSET(
    BULK 'https://onelake.dfs.fabric.microsoft.com/1514dadc-9182-486a-a8f8-fb2bf6665fea/fb6f8ecc-6d7d-4a98-b8fd-0f82f2cf6ff4/Files/bronze/weather/historical/regional_weather_2021_2024.csv',
    FORMAT = 'CSV',
    HEADER_ROW = TRUE
) 
WITH (
    [timestamp] VARCHAR(50),
    temp_sacramento VARCHAR(20),
    temp_san_jose VARCHAR(20),
    temp_fresno VARCHAR(20),
    temp_los_angeles VARCHAR(20),
    temp_riverside VARCHAR(20),
    temp_san_diego VARCHAR(20),
    temp_poway VARCHAR(20)
) AS source;
GO

CREATE TABLE bronze.regional_weather_historical_raw
AS
SELECT *
FROM OPENROWSET(
    BULK 'https://onelake.dfs.fabric.microsoft.com/1514dadc-9182-486a-a8f8-fb2bf6665fea/fb6f8ecc-6d7d-4a98-b8fd-0f82f2cf6ff4/Files/bronze/weather/historical/regional_weather_2021_2024.csv',
    FORMAT = 'CSV',
    HEADER_ROW = TRUE
) 
WITH (
    [timestamp] VARCHAR(50),
    temp_sacramento VARCHAR(20),
    temp_san_jose VARCHAR(20),
    temp_fresno VARCHAR(20),
    temp_los_angeles VARCHAR(20),
    temp_riverside VARCHAR(20),
    temp_san_diego VARCHAR(20),
    temp_poway VARCHAR(20)
) AS source;
GO

CREATE TABLE bronze.regional_weather_validation_raw
AS
SELECT *
FROM OPENROWSET(
    BULK 'https://onelake.dfs.fabric.microsoft.com/1514dadc-9182-486a-a8f8-fb2bf6665fea/fb6f8ecc-6d7d-4a98-b8fd-0f82f2cf6ff4/Files/bronze/weather/validation/regional_weather_2025.csv',
    FORMAT = 'CSV',
    HEADER_ROW = TRUE
) 
WITH (
    [timestamp] VARCHAR(50),
    temp_sacramento VARCHAR(20),
    temp_san_jose VARCHAR(20),
    temp_fresno VARCHAR(20),
    temp_los_angeles VARCHAR(20),
    temp_riverside VARCHAR(20),
    temp_san_diego VARCHAR(20),
    temp_poway VARCHAR(20)
) AS source;
GO

SELECT COUNT(*) AS historical_weather_rows
FROM bronze.regional_weather_historical_raw;

SELECT COUNT(*) AS validation_weather_rows
FROM bronze.regional_weather_validation_raw;