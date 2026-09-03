-- System load and time-of-use summary. This analysis assigns observed
-- CAISO system load to time-of-use periods; it does not create rates,
-- price multipliers, revenue estimates, or customer bill calculations.
--
-- build table:
--   gold.system_load_monthly_tou_summary

-- Remove the hypothetical rate-scenario table created by the prior version.
DROP TABLE IF EXISTS gold.tou_rate_design_scenario;
GO

-- Classify the existing hourly Gold load data and summarize by month.
--    TOU periods:
--      On-Peak: 4-9pm every day (HR ending 17-21)
--      Off-Peak: weekdays 6am-10am, 2-4pm, 9pm-12am; weekends 2-4pm, 9pm-12am
--      Super Off-Peak: weekdays 12-6am, 10am-2pm; weekends 12am-2pm
DROP TABLE IF EXISTS gold.system_load_monthly_tou_summary;
GO

CREATE TABLE gold.system_load_monthly_tou_summary
AS
WITH classified_load AS (
    SELECT
        source_stage,
        load_date,
        hour_ending,
        caiso_mw,
        CASE
            WHEN hour_ending BETWEEN 17 AND 21 THEN 'On-Peak'

            WHEN is_weekend = 1
                AND hour_ending BETWEEN 1 AND 14
                THEN 'Super Off-Peak'

            WHEN is_weekend = 0
                AND (
                    hour_ending BETWEEN 1 AND 6
                    OR hour_ending BETWEEN 11 AND 14
                 )
                THEN 'Super Off-Peak'

            ELSE 'Off-Peak'
        END AS tou_period
    FROM gold.caiso_hourly_load_features
)
SELECT
    source_stage,
    YEAR(load_date) AS load_year,
    MONTH(load_date) AS load_month,
    tou_period,
    COUNT(*) AS hourly_observations,

    -- One MW observed for one hour is one MWh.
    SUM(CAST(caiso_mw AS decimal(18, 3))) AS system_load_mwh_proxy
FROM classified_load
GROUP BY
    source_stage,
    YEAR(load_date),
    MONTH(load_date),
    tou_period;
GO


-- validation
SELECT
    source_stage,
    tou_period,
    SUM(hourly_observations) AS hourly_observations,
    SUM(system_load_mwh_proxy) AS system_load_mwh_proxy
FROM gold.system_load_monthly_tou_summary
GROUP BY source_stage, tou_period
ORDER BY source_stage, tou_period;
