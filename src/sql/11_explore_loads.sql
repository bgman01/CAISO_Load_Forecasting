--1. Confirm row counts, date ranges, and # of DST dates
SELECT
    source_stage,
    COUNT_BIG(*) AS hourly_rows,
    MIN(load_date) AS first_load_date,
    MAX(load_date) AS last_load_date,
    SUM(CASE WHEN hours_in_load_date <> 24 THEN 1 ELSE 0 END) AS rows_on_DST_transition_dates
FROM gold.caiso_hourly_load_features
GROUP BY source_stage;

--2. What is the average daily load shape?
SELECT
    hour_ending,
    AVG(caiso_mw) AS average_caiso_load_mw,
    MIN(caiso_mw) AS minimum_caiso_load_mw,
    MAX(caiso_mw) AS maximum_caiso_load_mw
FROM gold.caiso_hourly_load_features
WHERE source_stage = 'historical'
GROUP BY hour_ending
ORDER BY hour_ending;

-- 3. How does load differ between weekdays and weekends at each hour?
SELECT
    hour_ending,
    is_weekend,
    AVG(caiso_mw) AS average_caiso_load_mw
FROM gold.caiso_hourly_load_features
WHERE source_stage = 'historical'
GROUP BY hour_ending, is_weekend
ORDER BY hour_ending, is_weekend;

-- 4. Find monthly peak hours
WITH ranked_monthly_peaks AS (
    SELECT
        load_year,
        load_month,
        load_date,
        hour_ending,
        caiso_mw,
        caiso_minus_regional_mw,
        ROW_NUMBER() OVER (
            PARTITION BY load_year, load_month
            ORDER BY caiso_mw DESC
        ) AS peak_rank
    FROM gold.caiso_hourly_load_features
    WHERE source_stage = 'historical'
)
SELECT
    load_year,
    load_month,
    load_date,
    hour_ending,
    caiso_mw AS monthly_peak_load_mw,
    caiso_minus_regional_mw
FROM ranked_monthly_peaks
WHERE peak_rank = 1
ORDER BY load_year, load_month;

-- 5. Show 30 day load trend
SELECT
    load_date,
    average_load_mw,
    rolling_30_day_average_load_mw
FROM gold.caiso_daily_summary
WHERE source_stage = 'historical'
ORDER BY load_date;

-- 6. categorical weather and load view 
SELECT
    CASE
        WHEN temp_sacramento_f < 55 THEN 'Below 55 F'
        WHEN temp_sacramento_f < 70 THEN '55 to under 70 F'
        WHEN temp_sacramento_f < 85 THEN '70 to under 85 F'
        ELSE '85 F and above'
    END AS sacramento_temperature_band,
    COUNT_BIG(*) AS hourly_rows,
    AVG(caiso_mw) AS average_caiso_load_mw
FROM gold.caiso_hourly_load_weather
WHERE source_stage = 'historical'
  AND weather_match_status = 'matched'
GROUP BY
    CASE
        WHEN temp_sacramento_f < 55 THEN 'Below 55 F'
        WHEN temp_sacramento_f < 70 THEN '55 to under 70 F'
        WHEN temp_sacramento_f < 85 THEN '70 to under 85 F'
        ELSE '85 F and above'
    END
ORDER BY sacramento_temperature_band;
