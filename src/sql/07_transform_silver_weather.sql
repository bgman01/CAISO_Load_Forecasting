--create clean weather data from the bronze table

DROP TABLE IF EXISTS silver.regional_weather_hourly;
GO

CREATE TABLE silver.regional_weather_hourly
AS
WITH all_weather_rows AS (
    SELECT
        'historical' AS source_stage,
        [timestamp],
        temp_sacramento, temp_san_jose, temp_fresno,
        temp_los_angeles, temp_riverside, temp_san_diego, temp_poway
    FROM bronze.regional_weather_historical_raw

    UNION ALL

    SELECT
        'validation' AS source_stage,
        [timestamp],
        temp_sacramento, temp_san_jose, temp_fresno,
        temp_los_angeles, temp_riverside, temp_san_diego, temp_poway
    FROM bronze.regional_weather_validation_raw
),
typed_weather_rows AS (
    SELECT
        source_stage,
        -- The weather source is hourly; retain timestamps to the second.
        TRY_CAST([timestamp] AS datetime2(0)) AS weather_timestamp_label,
        TRY_CAST(temp_sacramento AS decimal(5, 1)) AS temp_sacramento_f,
        TRY_CAST(temp_san_jose AS decimal(5, 1)) AS temp_san_jose_f,
        TRY_CAST(temp_fresno AS decimal(5, 1)) AS temp_fresno_f,
        TRY_CAST(temp_los_angeles AS decimal(5, 1)) AS temp_los_angeles_f,
        TRY_CAST(temp_riverside AS decimal(5, 1)) AS temp_riverside_f,
        TRY_CAST(temp_san_diego AS decimal(5, 1)) AS temp_san_diego_f,
        TRY_CAST(temp_poway AS decimal(5, 1)) AS temp_poway_f
    FROM all_weather_rows
)
SELECT
    source_stage,
    weather_timestamp_label,
    CAST(weather_timestamp_label AS date) AS weather_date,
    DATEPART(hour, weather_timestamp_label) + 1 AS hour_ending,
    temp_sacramento_f,
    temp_san_jose_f,
    temp_fresno_f,
    temp_los_angeles_f,
    temp_riverside_f,
    temp_san_diego_f,
    temp_poway_f
FROM typed_weather_rows
WHERE weather_timestamp_label IS NOT NULL
  AND temp_sacramento_f IS NOT NULL
  AND temp_san_jose_f IS NOT NULL
  AND temp_fresno_f IS NOT NULL
  AND temp_los_angeles_f IS NOT NULL
  AND temp_riverside_f IS NOT NULL
  AND temp_san_diego_f IS NOT NULL
  AND temp_poway_f IS NOT NULL;
GO

-- Expected result: 43,824 weather rows with no missing temperature values.
SELECT source_stage, COUNT_BIG(*) AS row_count
FROM silver.regional_weather_hourly
GROUP BY source_stage;
