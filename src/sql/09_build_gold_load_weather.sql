--add weather to hourly load features

DROP TABLE IF EXISTS gold.caiso_hourly_load_weather;
GO

CREATE TABLE gold.caiso_hourly_load_weather
AS
SELECT
    l.*,
    w.temp_sacramento_f,
    w.temp_san_jose_f,
    w.temp_fresno_f,
    w.temp_los_angeles_f,
    w.temp_riverside_f,
    w.temp_san_diego_f,
    w.temp_poway_f,
    CASE
        --weather contains 24 timestamp labels every day. CAISO has 23 or 25 records on DST transition dates, so those rows are not
        --joined rather than risking a wrong hourly temperature match.
        WHEN l.hours_in_load_date <> 24 THEN 'not joined: DST transition'
        WHEN w.weather_timestamp_label IS NULL THEN 'missing weather'
        ELSE 'matched'
    END AS weather_match_status
FROM gold.caiso_hourly_load_features AS l
LEFT JOIN silver.regional_weather_hourly AS w
    ON l.source_stage = w.source_stage
   AND l.local_timestamp_label = w.weather_timestamp_label
   AND l.hours_in_load_date = 24;
GO

--verify rows
SELECT weather_match_status, COUNT(*) AS row_count
FROM gold.caiso_hourly_load_weather
GROUP BY weather_match_status;
