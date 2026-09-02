--build one row per day for trend and peak demand analysis

DROP TABLE IF EXISTS gold.caiso_daily_summary;
GO

CREATE TABLE gold.caiso_daily_summary
AS
WITH daily_load AS (
    SELECT
        source_stage,
        load_date,
        COUNT(*) AS hours_in_day,
        AVG(caiso_mw) AS average_load_mw,
        MAX(caiso_mw) AS peak_load_mw,
        MIN(caiso_mw) AS minimum_load_mw
    FROM gold.caiso_hourly_load_features
    GROUP BY source_stage, load_date
)
SELECT
    source_stage,
    load_date,
    hours_in_day,
    average_load_mw,
    peak_load_mw,
    minimum_load_mw,
    --current day + prior 29 daily rows = 30 day rolling average
    AVG(average_load_mw) OVER (
        PARTITION BY source_stage
        ORDER BY load_date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_30_day_average_load_mw
FROM daily_load;
GO
