import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = (
    PROCESSED_DIR /
    "tamil_nadu_toll_data.csv"
)

CLEAN_FILE = (
    PROCESSED_DIR /
    "tamil_nadu_toll_data_cleaned.csv"
)

QUALITY_FILE = (
    PROCESSED_DIR /
    "data_quality_report.csv"
)

MISSING_FILE = (
    PROCESSED_DIR /
    "missing_value_report.csv"
)

NEGATIVE_FILE = (
    PROCESSED_DIR /
    "negative_value_report.csv"
)


# ============================================================
# VEHICLE COUNT COLUMNS
# ============================================================

COUNT_COLUMNS = [
    "CAR_JEEP_CNT",
    "LCV_CNT",
    "BUS_TRUCK_CNT",
    "3_AXLE_CNT",
    "4_6_AXLE_CNT",
    "OSV_CNT"
]


# ============================================================
# VEHICLE REVENUE COLUMNS
# ============================================================

AMOUNT_COLUMNS = [
    "CAR_JEEP_AMT",
    "LCV_AMT",
    "BUS_TRUCK_AMT",
    "3_AXLE_AMT",
    "4_6_AXLE_AMT",
    "OSV_AMT"
]


# ============================================================
# ALL NUMERIC COLUMNS
# ============================================================

NUMERIC_COLUMNS = (
    COUNT_COLUMNS +
    AMOUNT_COLUMNS +
    [
        "TOTAL_CNT",
        "TOTAL_AMT"
    ]
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "PLAZA_ID",
    "PLAZA_NAME",
    "PIU",
    "RO",
    "STATE",
    "YEAR",
    "MONTH",
    "MONTH_NUMBER",
    "DATE",
    "TOTAL_CNT",
    "TOTAL_AMT"
]


# ============================================================
# START
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - DATA CLEANING & VALIDATION")
print("=" * 70)

print()

print("Loading:")
print(INPUT_FILE)

data = pd.read_csv(INPUT_FILE)

original_row_count = len(data)

print()
print("Rows loaded:", original_row_count)
print("Columns loaded:", len(data.columns))
print()


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

missing_required = []

for column in REQUIRED_COLUMNS:

    if column not in data.columns:
        missing_required.append(column)


if len(missing_required) > 0:

    print("ERROR: Required columns are missing:")

    for column in missing_required:
        print(" -", column)

    raise SystemExit


# ============================================================
# CLEAN TEXT COLUMNS
# ============================================================

TEXT_COLUMNS = [
    "PLAZA_ID",
    "PLAZA_NAME",
    "PIU",
    "RO",
    "STATE",
    "MONTH"
]

for column in TEXT_COLUMNS:

    data[column] = (
        data[column]
        .fillna("")
        .astype(str)
        .str.strip()
    )


# ============================================================
# REPLACE COMMON MISSING SYMBOLS
# ============================================================

data = data.replace(
    [
        "-",
        "--",
        "NA",
        "N/A",
        "na",
        "n/a",
        ""
    ],
    pd.NA
)


# ============================================================
# CONVERT NUMERIC COLUMNS
# ============================================================

for column in NUMERIC_COLUMNS:

    data[column] = pd.to_numeric(
        data[column],
        errors="coerce"
    )


# ============================================================
# CONVERT YEAR AND MONTH NUMBER
# ============================================================

data["YEAR"] = pd.to_numeric(
    data["YEAR"],
    errors="coerce"
)

data["MONTH_NUMBER"] = pd.to_numeric(
    data["MONTH_NUMBER"],
    errors="coerce"
)


# ============================================================
# CONVERT DATE
# ============================================================

data["DATE"] = pd.to_datetime(
    data["DATE"],
    errors="coerce"
)


# ============================================================
# DUPLICATE CHECK
# ============================================================

duplicate_count = int(
    data.duplicated().sum()
)


# ============================================================
# MISSING VALUE REPORT
# ============================================================

missing_rows = []

for column in data.columns:

    missing_count = int(
        data[column].isna().sum()
    )

    missing_percentage = (
        missing_count /
        original_row_count
    ) * 100

    missing_rows.append(
        [
            column,
            missing_count,
            round(
                missing_percentage,
                2
            )
        ]
    )


missing_report = pd.DataFrame(
    missing_rows,
    columns=[
        "COLUMN",
        "MISSING_COUNT",
        "MISSING_PERCENTAGE"
    ]
)


# ============================================================
# NEGATIVE VALUE CHECK
# ============================================================

negative_rows = []

for column in NUMERIC_COLUMNS:

    negative_count = int(
        (
            data[column] < 0
        ).sum()
    )

    negative_rows.append(
        [
            column,
            negative_count
        ]
    )


negative_report = pd.DataFrame(
    negative_rows,
    columns=[
        "COLUMN",
        "NEGATIVE_COUNT"
    ]
)


# ============================================================
# TOTAL TRAFFIC VALIDATION
#
# We validate only when ALL category counts are available.
# Missing categories should not automatically be treated as zero.
# ============================================================

complete_count_rows = (
    data[COUNT_COLUMNS]
    .notna()
    .all(axis=1)
    &
    data["TOTAL_CNT"].notna()
)


data["CALCULATED_TOTAL_CNT"] = pd.NA

data.loc[
    complete_count_rows,
    "CALCULATED_TOTAL_CNT"
] = (
    data.loc[
        complete_count_rows,
        COUNT_COLUMNS
    ]
    .sum(axis=1)
)


data["COUNT_DIFFERENCE"] = pd.NA

data.loc[
    complete_count_rows,
    "COUNT_DIFFERENCE"
] = (
    data.loc[
        complete_count_rows,
        "TOTAL_CNT"
    ]
    -
    data.loc[
        complete_count_rows,
        "CALCULATED_TOTAL_CNT"
    ]
)


count_mismatch_mask = (
    complete_count_rows
    &
    (
        data["COUNT_DIFFERENCE"]
        .abs()
        > 0
    )
)


count_mismatch_count = int(
    count_mismatch_mask.sum()
)


count_validation_unavailable = int(
    (
        ~complete_count_rows
    ).sum()
)


# ============================================================
# TOTAL REVENUE VALIDATION
#
# We validate only when ALL revenue categories are available.
# ============================================================

complete_amount_rows = (
    data[AMOUNT_COLUMNS]
    .notna()
    .all(axis=1)
    &
    data["TOTAL_AMT"].notna()
)


data["CALCULATED_TOTAL_AMT"] = pd.NA

data.loc[
    complete_amount_rows,
    "CALCULATED_TOTAL_AMT"
] = (
    data.loc[
        complete_amount_rows,
        AMOUNT_COLUMNS
    ]
    .sum(axis=1)
)


data["AMOUNT_DIFFERENCE"] = pd.NA

data.loc[
    complete_amount_rows,
    "AMOUNT_DIFFERENCE"
] = (
    data.loc[
        complete_amount_rows,
        "TOTAL_AMT"
    ]
    -
    data.loc[
        complete_amount_rows,
        "CALCULATED_TOTAL_AMT"
    ]
)


amount_mismatch_mask = (
    complete_amount_rows
    &
    (
        data["AMOUNT_DIFFERENCE"]
        .abs()
        > 0.01
    )
)


amount_mismatch_count = int(
    amount_mismatch_mask.sum()
)


amount_validation_unavailable = int(
    (
        ~complete_amount_rows
    ).sum()
)


# ============================================================
# INVALID YEAR CHECK
# ============================================================

invalid_year_count = int(
    (
        ~data["YEAR"].isin(
            [
                2022,
                2023,
                2024,
                2025,
                2026
            ]
        )
    ).sum()
)


# ============================================================
# INVALID MONTH CHECK
# ============================================================

invalid_month_count = int(
    (
        ~data["MONTH_NUMBER"].isin(
            list(range(1, 13))
        )
    ).sum()
)


# ============================================================
# MISSING PLAZA INFORMATION
# ============================================================

missing_plaza_id = int(
    data["PLAZA_ID"].isna().sum()
)

missing_plaza_name = int(
    data["PLAZA_NAME"].isna().sum()
)


# ============================================================
# MISSING DATE
# ============================================================

missing_date_count = int(
    data["DATE"].isna().sum()
)


# ============================================================
# REMOVE ONLY EXACT DUPLICATES
#
# We do NOT remove outliers or revenue mismatches here.
# ============================================================

if duplicate_count > 0:

    data = data.drop_duplicates()

else:

    print(
        "Exact duplicate rows found: 0"
    )


# ============================================================
# CREATE QUALITY REPORT
# ============================================================

quality_rows = [

    [
        "ORIGINAL_ROWS",
        original_row_count,
        "Rows loaded from Tamil Nadu dataset"
    ],

    [
        "DUPLICATE_ROWS",
        duplicate_count,
        "Exact duplicate rows found"
    ],

    [
        "ROWS_AFTER_DUPLICATE_REMOVAL",
        len(data),
        "Rows remaining after removing exact duplicates"
    ],

    [
        "COUNT_MISMATCH_ROWS",
        count_mismatch_count,
        "TOTAL_CNT differs from vehicle category count sum"
    ],

    [
        "COUNT_VALIDATION_UNAVAILABLE",
        count_validation_unavailable,
        "Rows where count validation could not be performed"
    ],

    [
        "REVENUE_MISMATCH_ROWS",
        amount_mismatch_count,
        "TOTAL_AMT differs from vehicle category revenue sum"
    ],

    [
        "REVENUE_VALIDATION_UNAVAILABLE",
        amount_validation_unavailable,
        "Rows where revenue validation could not be performed"
    ],

    [
        "NEGATIVE_NUMERIC_VALUES",
        int(
            negative_report["NEGATIVE_COUNT"].sum()
        ),
        "Total negative numeric values"
    ],

    [
        "INVALID_YEAR_ROWS",
        invalid_year_count,
        "Rows with invalid project year"
    ],

    [
        "INVALID_MONTH_ROWS",
        invalid_month_count,
        "Rows with invalid month number"
    ],

    [
        "MISSING_PLAZA_ID",
        missing_plaza_id,
        "Rows with missing plaza ID"
    ],

    [
        "MISSING_PLAZA_NAME",
        missing_plaza_name,
        "Rows with missing plaza name"
    ],

    [
        "MISSING_DATE",
        missing_date_count,
        "Rows with missing or invalid date"
    ]
]


quality_report = pd.DataFrame(
    quality_rows,
    columns=[
        "CHECK",
        "COUNT",
        "DESCRIPTION"
    ]
)


# ============================================================
# SAVE CLEANED DATA
# ============================================================

data.to_csv(
    CLEAN_FILE,
    index=False
)


# ============================================================
# SAVE QUALITY REPORT
# ============================================================

quality_report.to_csv(
    QUALITY_FILE,
    index=False
)


# ============================================================
# SAVE MISSING VALUE REPORT
# ============================================================

missing_report.to_csv(
    MISSING_FILE,
    index=False
)


# ============================================================
# SAVE NEGATIVE VALUE REPORT
# ============================================================

negative_report.to_csv(
    NEGATIVE_FILE,
    index=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("=" * 70)
print("DATA QUALITY RESULTS")
print("=" * 70)

print()

print(
    "Original rows:",
    original_row_count
)

print(
    "Duplicate rows found:",
    duplicate_count
)

print(
    "Rows after duplicate removal:",
    len(data)
)

print(
    "Traffic count mismatches:",
    count_mismatch_count
)

print(
    "Traffic validation unavailable:",
    count_validation_unavailable
)

print(
    "Revenue mismatches:",
    amount_mismatch_count
)

print(
    "Revenue validation unavailable:",
    amount_validation_unavailable
)

print(
    "Negative numeric values:",
    int(
        negative_report["NEGATIVE_COUNT"].sum()
    )
)

print(
    "Invalid year rows:",
    invalid_year_count
)

print(
    "Invalid month rows:",
    invalid_month_count
)

print(
    "Missing plaza IDs:",
    missing_plaza_id
)

print(
    "Missing plaza names:",
    missing_plaza_name
)

print(
    "Missing dates:",
    missing_date_count
)

print()

print(
    "Cleaned dataset saved at:"
)

print(
    CLEAN_FILE
)

print()

print(
    "Quality report saved at:"
)

print(
    QUALITY_FILE
)

print()

print(
    "Missing-value report saved at:"
)

print(
    MISSING_FILE
)

print()

print(
    "Negative-value report saved at:"
)

print(
    NEGATIVE_FILE
)

print()

print("=" * 70)
print("STEP 5 COMPLETED")
print("=" * 70)