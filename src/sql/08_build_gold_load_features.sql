--build hourly load features (no weather included)

DROP TABLE IF EXISTS gold.caiso_hourly_features;
DROP TABLE IF EXISTS gold.caiso_hourly_load_features;
GO

CREATE TABLE gold.caiso_hourly_load_features
AS
WITH load_features AS (
    SELECT
        l.*,
        COUNT(*) OVER (PARTITION BY l.load_date) AS hours_in_load_date,
        LAG(l.caiso_mw, 24) OVER (
            ORDER BY l.load_date, l.hour_ending, l.hour_instance
        ) AS caiso_lag_24_mw,
        LAG(l.caiso_mw, 168) OVER (
            ORDER BY l.load_date, l.hour_ending, l.hour_instance
        ) AS caiso_lag_168_mw
    FROM silver.caiso_load_hourly AS l
)
SELECT
    l.source_stage,
    l.load_date,
    l.hour_ending,
    l.hour_instance,
    l.local_timestamp_label,
    YEAR(l.load_date) AS load_year,
    MONTH(l.load_date) AS load_month,
    -- e.g 1900-01-01 is Monday. Sets 1 = Monday and 7 = Sunday
    (DATEDIFF(day, CONVERT(date, '19000101', 112), l.load_date) % 7) + 1 AS weekday_number,
    CASE
        WHEN (DATEDIFF(day, CONVERT(date, '19000101', 112), l.load_date) % 7) + 1 IN (6, 7)
            THEN 1
        ELSE 0
    END AS is_weekend,
    l.pge_mw,
    l.sce_mw,
    l.sdge_mw,
    l.vea_mw,
    l.caiso_mw,
    l.regional_total_mw,
    l.caiso_minus_regional_mw,
    l.caiso_lag_24_mw,
    l.caiso_lag_168_mw,
    l.hours_in_load_date
FROM load_features AS l;
GO
