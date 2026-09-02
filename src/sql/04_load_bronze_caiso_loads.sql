-- Raw CAISO Excel files stay unchanged in OneLake under:
-- Files/bronze/loads/historical and Files/bronze/loads/validation.
--run notebook 01_stage_caiso_excel_in_fabric.py first. 

-- Rebuild these queryable bronze tables from the immutable OneLake files.
DROP TABLE IF EXISTS bronze.caiso_load_historical_raw;
DROP TABLE IF EXISTS bronze.caiso_load_validation_raw;
GO

--preview the historical staging file
SELECT TOP 10 *
FROM OPENROWSET(
    BULK 'https://onelake.dfs.fabric.microsoft.com/1514dadc-9182-486a-a8f8-fb2bf6665fea/fb6f8ecc-6d7d-4a98-b8fd-0f82f2cf6ff4/Files/staging/loads/historical/caiso_load_historical_raw.csv',
    FORMAT = 'CSV',
    HEADER_ROW = TRUE
) 
WITH (
    Date VARCHAR(50),
    HR VARCHAR(20),
    PGE VARCHAR(50),
    SCE VARCHAR(50),
    SDGE VARCHAR(50),
    VEA VARCHAR(50),
    CAISO VARCHAR(50),
    source_file VARCHAR(50)
) AS source;
GO

--create bronze historical table
CREATE TABLE bronze.caiso_load_historical_raw
AS
SELECT *
FROM OPENROWSET(
    BULK 'https://onelake.dfs.fabric.microsoft.com/1514dadc-9182-486a-a8f8-fb2bf6665fea/fb6f8ecc-6d7d-4a98-b8fd-0f82f2cf6ff4/Files/staging/loads/historical/caiso_load_historical_raw.csv',
    FORMAT = 'CSV',
    HEADER_ROW = TRUE
)
WITH (
    Date VARCHAR(50),
    HR VARCHAR(20),
    PGE VARCHAR(50),
    SCE VARCHAR(50),
    SDGE VARCHAR(50),
    VEA VARCHAR(50),
    CAISO VARCHAR(50),
    source_file VARCHAR(50)
) AS source;
GO


--create bronze validation table
CREATE TABLE bronze.caiso_load_validation_raw
AS
SELECT *
FROM OPENROWSET(
    BULK 'https://onelake.dfs.fabric.microsoft.com/1514dadc-9182-486a-a8f8-fb2bf6665fea/fb6f8ecc-6d7d-4a98-b8fd-0f82f2cf6ff4/Files/staging/loads/validation/caiso_load_validation_raw.csv',
    FORMAT = 'CSV',
    HEADER_ROW = TRUE
) 
WITH (
    Date VARCHAR(50),
    HR VARCHAR(20),
    PGE VARCHAR(50),
    SCE VARCHAR(50),
    SDGE VARCHAR(50),
    VEA VARCHAR(50),
    CAISO VARCHAR(50),
    source_file VARCHAR(50)
) AS source;
GO

--confirm the expected row totals
SELECT COUNT(*) AS historical_row_count
FROM bronze.caiso_load_historical_raw;

SELECT COUNT(*) AS validation_row_count
FROM bronze.caiso_load_validation_raw;
