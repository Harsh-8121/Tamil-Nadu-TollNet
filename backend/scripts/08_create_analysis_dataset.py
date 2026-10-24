import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = (
    PROCESSED_DIR /
    "tamil_nadu_toll_data_cleaned.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "tamil_nadu_analysis_data.csv"
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
# START
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - FINAL ANALYSIS DATASET")
print("=" * 70)

print()

print("Loading:")
print(INPUT_FILE)

data = pd.read_csv(
    INPUT_FILE
)

print()

print(
    "Rows before missing-value treatment:",
    len(data)
)

print()


# ============================================================
# CONVERT VEHICLE COLUMNS TO NUMERIC
# ============================================================

for column in COUNT_COLUMNS + AMOUNT_COLUMNS:

    data[column] = pd.to_numeric(
        data[column],
        errors="coerce"
    )


# ============================================================
# COUNT MISSING VALUES BEFORE IMPUTATION
# ============================================================

missing_before = (
    data[COUNT_COLUMNS + AMOUNT_COLUMNS]
    .isna()
    .sum()
)


# ============================================================
# REPLACE MISSING VEHICLE VALUES WITH ZERO
#
# Step 7 showed that every missing category value is
# consistent with zero.
# ============================================================

for column in COUNT_COLUMNS + AMOUNT_COLUMNS:

    data[column] = data[column].fillna(0)


# ============================================================
# VERIFY NO MISSING VEHICLE VALUES REMAIN
# ============================================================

missing_after = (
    data[COUNT_COLUMNS + AMOUNT_COLUMNS]
    .isna()
    .sum()
)


# ============================================================
# CREATE REVENUE PER VEHICLE
#
# TOTAL_AMT / TOTAL_CNT
# ============================================================

data["REVENUE_PER_VEHICLE"] = 0.0

valid_rows = (
    data["TOTAL_CNT"] > 0
)

data.loc[
    valid_rows,
    "REVENUE_PER_VEHICLE"
] = (
    data.loc[
        valid_rows,
        "TOTAL_AMT"
    ]
    /
    data.loc[
        valid_rows,
        "TOTAL_CNT"
    ]
)


# ============================================================
# CREATE YEAR-MONTH LABEL
# ============================================================

data["YEAR_MONTH"] = (
    data["DATE"]
    .astype(str)
    .str[:7]
)


# ============================================================
# VEHICLE SHARE FEATURES
# ============================================================

for count_column in COUNT_COLUMNS:

    category_name = (
        count_column
        .replace("_CNT", "")
        .lower()
    )

    share_column = (
        category_name +
        "_SHARE"
    )

    data[share_column] = 0.0

    data.loc[
        valid_rows,
        share_column
    ] = (
        data.loc[
            valid_rows,
            count_column
        ]
        /
        data.loc[
            valid_rows,
            "TOTAL_CNT"
        ]
    )


# ============================================================
# SAVE FINAL DATASET
# ============================================================

data.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL REPORT
# ============================================================

print()
print("=" * 70)
print("MISSING VALUE TREATMENT")
print("=" * 70)

print()

print("Missing values before treatment:")

for column in COUNT_COLUMNS + AMOUNT_COLUMNS:

    print(
        " -",
        column,
        ":",
        int(missing_before[column])
    )

print()

print("Missing values after treatment:")

for column in COUNT_COLUMNS + AMOUNT_COLUMNS:

    print(
        " -",
        column,
        ":",
        int(missing_after[column])
    )

print()

print(
    "Total missing vehicle values treated:",
    int(missing_before.sum())
)

print()

print(
    "Final rows:",
    len(data)
)

print(
    "Final columns:",
    len(data.columns)
)

print()

print(
    "Analysis-ready dataset saved at:"
)

print(
    OUTPUT_FILE
)

print()

print("Final dataset columns:")

for column in data.columns:

    print(
        " -",
        column
    )

print()

print("=" * 70)
print("STEP 8 COMPLETED")
print("=" * 70)