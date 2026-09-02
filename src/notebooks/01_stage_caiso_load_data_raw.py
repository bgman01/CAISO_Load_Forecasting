#stage raw CAISO data to bronze (no cleaning or transformation)

from pathlib import Path
import pandas as pd


RAW_LOADS_ROOT = "/lakehouse/default/Files/bronze/loads"
STAGING_LOADS_ROOT = "/lakehouse/default/Files/staging/loads"

DATASETS = {
    "historical": "caiso_load_historical_raw.csv",
    "validation": "caiso_load_validation_raw.csv",
}

for dataset_role, output_file_name in DATASETS.items():
    input_directory = f"{RAW_LOADS_ROOT}/{dataset_role}"
    output_directory = Path(f"{STAGING_LOADS_ROOT}/{dataset_role}")

    excel_files = sorted(
        file.name
        for file in notebookutils.fs.ls(f"Files/bronze/loads/{dataset_role}")
        if file.name.lower().endswith(".xlsx")
    )

    raw_exports = []
    for file_name in excel_files:
        # dtype=object preserves the exported values as closely as possible.
        source = pd.read_excel(f"{input_directory}/{file_name}", dtype=object)
        source["source_file"] = file_name
        raw_exports.append(source)

    raw_loads = pd.concat(raw_exports, ignore_index=True, sort=False)
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / output_file_name
    raw_loads.to_csv(output_path, index=False)

    print(f"Files saved to {output_path}")
    print(f"Total source rows: {len(raw_loads)}")