--create clean hourly load from the bronze tables (fix CAISO footer rows in date column)

DROP TABLE IF EXISTS silver.caiso_load_hourly;
GO

CREATE TABLE silver.caiso_load_hourly
AS
WITH all_load_rows AS (
    -- Keep the historical and validation sources identifiable after combining them.
    SELECT
        'historical' AS source_stage,
        [Date], [HR], [PGE], [SCE], [SDGE], [VEA], [CAISO], source_file
    FROM bronze.caiso_load_historical_raw

    UNION ALL

    SELECT
        'validation' AS source_stage,
        [Date], [HR], [PGE], [SCE], [SDGE], [VEA], [CAISO], source_file
    FROM bronze.caiso_load_validation_raw
),
source_rows_without_footers AS (
    --Some monthly CAISO exports end with a blank row and a "CAISO Public" footer row so remove those
    SELECT
        source_stage,
        [Date], [HR], [PGE], [SCE], [SDGE], [VEA], [CAISO], source_file
    FROM all_load_rows
    WHERE NULLIF(LTRIM(RTRIM([Date])), '') IS NOT NULL
      AND LTRIM(RTRIM([Date])) <> 'CAISO Public'
),
typed_load_rows AS (
    SELECT
        source_stage,
        TRY_CAST([Date] AS date) AS load_date,
        TRY_CAST([HR] AS int) AS hour_ending,
        TRY_CAST([PGE] AS decimal(12, 3)) AS pge_mw,
        TRY_CAST([SCE] AS decimal(12, 3)) AS sce_mw,
        TRY_CAST([SDGE] AS decimal(12, 3)) AS sdge_mw,
        TRY_CAST([VEA] AS decimal(12, 3)) AS vea_mw,
        TRY_CAST([CAISO] AS decimal(12, 3)) AS caiso_mw,
        source_file
    FROM source_rows_without_footers
),
numbered_load_rows AS (
    SELECT
        *,
        --fall DST day has two HR = 1 rows. Make each row distinguishable without removing either observation
        ROW_NUMBER() OVER (
            PARTITION BY load_date, hour_ending
            ORDER BY source_file, caiso_mw
        ) AS hour_instance,
        COUNT(*) OVER (
            PARTITION BY load_date, hour_ending
        ) AS records_at_hour_label
    FROM typed_load_rows
    WHERE load_date IS NOT NULL
      AND hour_ending BETWEEN 1 AND 24
      AND pge_mw IS NOT NULL
      AND sce_mw IS NOT NULL
      AND sdge_mw IS NOT NULL
      AND vea_mw IS NOT NULL
      AND caiso_mw IS NOT NULL
)
SELECT
    source_stage,
    load_date,
    hour_ending,
    hour_instance,
    records_at_hour_label,
    DATEADD(hour, hour_ending - 1, CAST(load_date AS datetime2(0))) AS local_timestamp_label,
    pge_mw,
    sce_mw,
    sdge_mw,
    vea_mw,
    caiso_mw,
    pge_mw + sce_mw + sdge_mw + vea_mw AS regional_total_mw,
    caiso_mw - (pge_mw + sce_mw + sdge_mw + vea_mw) AS caiso_minus_regional_mw,
    source_file
FROM numbered_load_rows;
GO

--expected 35,064 historical rows + 8,760 validation rows = 43,824 
SELECT source_stage, COUNT_BIG(*) AS row_count
FROM silver.caiso_load_hourly
GROUP BY source_stage;
