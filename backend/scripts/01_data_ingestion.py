import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# MONTH MAPPING
# Handles:
# Jan, Feb, Mar, Apr, May, Jun, Jul, July,
# Aug, Sep, Sept, Oct, Nov, Dec
# ============================================================

MONTH_MAP = {
    "jan": ("January", 1),
    "feb": ("February", 2),
    "mar": ("March", 3),
    "apr": ("April", 4),
    "may": ("May", 5),
    "jun": ("June", 6),
    "jul": ("July", 7),
    "july": ("July", 7),
    "aug": ("August", 8),
    "sep": ("September", 9),
    "sept": ("September", 9),
    "oct": ("October", 10),
    "nov": ("November", 11),
    "dec": ("December", 12)
}


# ============================================================
# EXPECTED ORIGINAL COLUMNS
# ============================================================

EXPECTED_COLUMNS = [
    "PLAZA_NAME",
    "PIU",
    "RO",
    "CAR_JEEP_CNT",
    "CAR_JEEP_AMT",
    "LCV_CNT",
    "LCV_AMT",
    "BUS_TRUCK_CNT",
    "BUS_TRUCK_AMT",
    "3_AXLE_CNT",
    "3_AXLE_AMT",
    "4_6_AXLE_CNT",
    "4_6_AXLE_AMT",
    "OSV_CNT",
    "OSV_AMT",
    "TOTAL_CNT",
    "TOTAL_AMT"
]


# ============================================================
# FIND HEADER ROW
# Some Excel files may have formatting/header issues.
# So we search for the row containing PLAZA_NAME.
# ============================================================

def find_header_row(file_path):
    temp = pd.read_excel(file_path, sheet_name=0, header=None)

    for row_number in range(min(15, len(temp))):

        row_values = temp.iloc[row_number].astype(str).str.strip().str.upper()

        if "PLAZA_NAME" in row_values.values:
            return row_number

    return 0


# ============================================================
# EXTRACT YEAR AND MONTH FROM FILE
# ============================================================

def get_year_month(file_path):

    file_name = file_path.stem

    parts = file_name.split("_")

    if len(parts) < 2:
        raise ValueError(
            "Filename format not understood: " + file_path.name
        )

    month_text = parts[0].strip().lower()
    year_text = parts[-1].strip()

    if month_text not in MONTH_MAP:
        raise ValueError(
            "Month not recognized in file: " + file_path.name
        )

    if not year_text.isdigit():
        raise ValueError(
            "Year not recognized in file: " + file_path.name
        )

    month_name, month_number = MONTH_MAP[month_text]

    year = int(year_text)

    return year, month_name, month_number


# ============================================================
# READ ONE EXCEL FILE
# ============================================================

def read_one_excel(file_path):

    year, month_name, month_number = get_year_month(file_path)

    header_row = find_header_row(file_path)

    df = pd.read_excel(
        file_path,
        sheet_name=0,
        header=header_row
    )

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    df.columns = [
        str(column).strip().upper()
        for column in df.columns
    ]

    # --------------------------------------------------------
    # Keep only expected columns when available
    # --------------------------------------------------------

    missing_columns = []

    for column in EXPECTED_COLUMNS:

        if column not in df.columns:
            missing_columns.append(column)

    if len(missing_columns) > 0:

        print()
        print("WARNING")
        print("File:", file_path.name)
        print("Missing columns:")

        for column in missing_columns:
            print("   ", column)

        print()

        return None

    df = df[EXPECTED_COLUMNS].copy()

    # --------------------------------------------------------
    # Remove completely empty rows
    # --------------------------------------------------------

    df = df.dropna(
        how="all"
    )

    # --------------------------------------------------------
    # Remove rows where plaza name is empty
    # --------------------------------------------------------

    df["PLAZA_NAME"] = (
        df["PLAZA_NAME"]
        .astype(str)
        .str.strip()
    )

    df = df[
        (df["PLAZA_NAME"] != "") &
        (df["PLAZA_NAME"].str.upper() != "NAN")
    ]

    # --------------------------------------------------------
    # Replace '-' with missing value
    # --------------------------------------------------------

    df = df.replace(
        ["-", "--", "NA", "N/A", "na", "n/a"],
        pd.NA
    )

    # --------------------------------------------------------
    # Add time information
    # --------------------------------------------------------

    df["YEAR"] = year
    df["MONTH"] = month_name
    df["MONTH_NUMBER"] = month_number

    df["DATE"] = pd.to_datetime(
        {
            "year": df["YEAR"],
            "month": df["MONTH_NUMBER"],
            "day": 1
        }
    )

    # --------------------------------------------------------
    # Keep source filename for traceability
    # --------------------------------------------------------

    df["SOURCE_FILE"] = file_path.name

    return df


# ============================================================
# FIND ALL EXCEL FILES
# ============================================================

excel_files = []

for year in [2022, 2023, 2024, 2025, 2026]:

    year_folder = RAW_DIR / str(year)

    if not year_folder.exists():

        print(
            "WARNING: Folder not found:",
            year_folder
        )

        continue

    files = list(
        year_folder.glob("*.xlsx")
    )

    excel_files.extend(files)


# ============================================================
# CHECK FILE COUNT
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - DATA INGESTION")
print("=" * 70)

print()
print("Excel files found:", len(excel_files))
print()


# ============================================================
# READ ALL FILES
# ============================================================

all_data = []

successful_files = 0
failed_files = 0

for file_path in sorted(excel_files):

    print(
        "Reading:",
        file_path.name
    )

    try:

        df = read_one_excel(file_path)

        if df is not None:

            all_data.append(df)

            successful_files += 1

    except Exception as error:

        failed_files += 1

        print(
            "ERROR:",
            file_path.name
        )

        print(
            error
        )

        print()


# ============================================================
# COMBINE ALL DATA
# ============================================================

if len(all_data) == 0:

    print()
    print("No valid data files were found.")
    print("Check your folder structure.")
    raise SystemExit


combined_data = pd.concat(
    all_data,
    ignore_index=True
)


# ============================================================
# SORT DATA
# ============================================================

combined_data = combined_data.sort_values(
    by=[
        "DATE",
        "PLAZA_NAME"
    ]
)


combined_data = combined_data.reset_index(
    drop=True
)


# ============================================================
# SAVE COMBINED DATA
# ============================================================

combined_file = (
    PROCESSED_DIR /
    "all_india_toll_data_2022_2026.csv"
)

combined_data.to_csv(
    combined_file,
    index=False
)


# ============================================================
# CREATE UNIQUE PLAZA CANDIDATE TABLE
#
# IMPORTANT:
# This is NOT YET our final Tamil Nadu master table.
#
# It contains every plaza appearing in the source data.
# We will verify which ones are actually in Tamil Nadu next.
# ============================================================

plaza_candidates = (
    combined_data[
        [
            "PLAZA_NAME",
            "PIU",
            "RO"
        ]
    ]
    .drop_duplicates()
    .sort_values(
        by="PLAZA_NAME"
    )
    .reset_index(
        drop=True
    )
)


candidate_file = (
    PROCESSED_DIR /
    "plaza_candidates.csv"
)

plaza_candidates.to_csv(
    candidate_file,
    index=False
)


# ============================================================
# CREATE SUMMARY BY PLAZA
# ============================================================

plaza_summary = (
    combined_data
    .groupby(
        "PLAZA_NAME",
        dropna=False
    )
    .agg(
        RECORD_COUNT=("PLAZA_NAME", "size"),
        FIRST_DATE=("DATE", "min"),
        LAST_DATE=("DATE", "max")
    )
    .reset_index()
    .sort_values(
        by="PLAZA_NAME"
    )
)


summary_file = (
    PROCESSED_DIR /
    "plaza_summary.csv"
)

plaza_summary.to_csv(
    summary_file,
    index=False
)


# ============================================================
# FINAL REPORT
# ============================================================

print()
print("=" * 70)
print("INGESTION COMPLETED")
print("=" * 70)

print()

print(
    "Successful files:",
    successful_files
)

print(
    "Failed files:",
    failed_files
)

print(
    "Total rows:",
    len(combined_data)
)

print(
    "Total unique raw plaza names:",
    combined_data["PLAZA_NAME"].nunique()
)

print()

print(
    "Combined dataset saved at:"
)

print(
    combined_file
)

print()

print(
    "Plaza candidate list saved at:"
)

print(
    candidate_file
)

print()

print(
    "Plaza summary saved at:"
)

print(
    summary_file
)

print()

print("Columns in combined dataset:")

for column in combined_data.columns:

    print(
        " -",
        column
    )

print()
print("=" * 70)