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

MISSING_OUTPUT = (
    PROCESSED_DIR /
    "detailed_missing_records.csv"
)

COUNT_OUTPUT = (
    PROCESSED_DIR /
    "count_validation_details.csv"
)

REVENUE_OUTPUT = (
    PROCESSED_DIR /
    "revenue_validation_details.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - QUALITY INVESTIGATION")
print("=" * 70)

print()

print("Loading:")
print(INPUT_FILE)

data = pd.read_csv(
    INPUT_FILE
)

print()
print("Rows:", len(data))
print()


# ============================================================
# VEHICLE COLUMNS
# ============================================================

COUNT_COLUMNS = [
    "CAR_JEEP_CNT",
    "LCV_CNT",
    "BUS_TRUCK_CNT",
    "3_AXLE_CNT",
    "4_6_AXLE_CNT",
    "OSV_CNT"
]

AMOUNT_COLUMNS = [
    "CAR_JEEP_AMT",
    "LCV_AMT",
    "BUS_TRUCK_AMT",
    "3_AXLE_AMT",
    "4_6_AXLE_AMT",
    "OSV_AMT"
]


# ============================================================
# SHOW MISSING VALUES BY COLUMN
# ============================================================

print("=" * 70)
print("MISSING VALUES BY COLUMN")
print("=" * 70)

print()

for column in COUNT_COLUMNS + AMOUNT_COLUMNS:

    missing_count = int(
        data[column].isna().sum()
    )

    if missing_count > 0:

        print(
            column,
            ":",
            missing_count
        )


# ============================================================
# CREATE DETAILED MISSING RECORDS
# ============================================================

all_vehicle_columns = (
    COUNT_COLUMNS +
    AMOUNT_COLUMNS
)

missing_mask = (
    data[all_vehicle_columns]
    .isna()
    .any(axis=1)
)

missing_records = data.loc[
    missing_mask,
    [
        "PLAZA_ID",
        "PLAZA_NAME",
        "PIU",
        "RO",
        "YEAR",
        "MONTH",
        "DATE"
    ] + all_vehicle_columns
].copy()


missing_records.to_csv(
    MISSING_OUTPUT,
    index=False
)


# ============================================================
# COUNT VALIDATION
# ============================================================

data["CALCULATED_TOTAL_CNT"] = (
    data[COUNT_COLUMNS]
    .sum(
        axis=1,
        min_count=1
    )
)

data["COUNT_DIFFERENCE"] = (
    data["TOTAL_CNT"] -
    data["CALCULATED_TOTAL_CNT"]
)


count_problem_mask = (
    data["COUNT_DIFFERENCE"].abs() > 0
)


count_details = data.loc[
    count_problem_mask,
    [
        "PLAZA_ID",
        "PLAZA_NAME",
        "YEAR",
        "MONTH",
        "TOTAL_CNT",
        "CALCULATED_TOTAL_CNT",
        "COUNT_DIFFERENCE"
    ] + COUNT_COLUMNS
].copy()


count_details.to_csv(
    COUNT_OUTPUT,
    index=False
)


# ============================================================
# REVENUE VALIDATION
# ============================================================

data["CALCULATED_TOTAL_AMT"] = (
    data[AMOUNT_COLUMNS]
    .sum(
        axis=1,
        min_count=1
    )
)

data["AMOUNT_DIFFERENCE"] = (
    data["TOTAL_AMT"] -
    data["CALCULATED_TOTAL_AMT"]
)


revenue_problem_mask = (
    data["AMOUNT_DIFFERENCE"].abs() > 0.01
)


revenue_details = data.loc[
    revenue_problem_mask,
    [
        "PLAZA_ID",
        "PLAZA_NAME",
        "YEAR",
        "MONTH",
        "TOTAL_AMT",
        "CALCULATED_TOTAL_AMT",
        "AMOUNT_DIFFERENCE"
    ] + AMOUNT_COLUMNS
].copy()


revenue_details.to_csv(
    REVENUE_OUTPUT,
    index=False
)


# ============================================================
# PRINT SUMMARY
# ============================================================

print()
print("=" * 70)
print("QUALITY INVESTIGATION RESULTS")
print("=" * 70)

print()

print(
    "Rows with at least one missing vehicle value:",
    len(missing_records)
)

print(
    "Rows with traffic-total mismatch:",
    len(count_details)
)

print(
    "Rows with revenue-total mismatch:",
    len(revenue_details)
)

print()

print(
    "Missing records saved at:"
)

print(
    MISSING_OUTPUT
)

print()

print(
    "Count validation details saved at:"
)

print(
    COUNT_OUTPUT
)

print()

print(
    "Revenue validation details saved at:"
)

print(
    REVENUE_OUTPUT
)

print()

# ============================================================
# DISPLAY REVENUE MISMATCHES
# ============================================================

if len(revenue_details) > 0:

    print("=" * 70)
    print("REVENUE MISMATCHES")
    print("=" * 70)

    print()

    print(
        revenue_details[
            [
                "PLAZA_ID",
                "PLAZA_NAME",
                "YEAR",
                "MONTH",
                "TOTAL_AMT",
                "CALCULATED_TOTAL_AMT",
                "AMOUNT_DIFFERENCE"
            ]
        ].to_string(
            index=False
        )
    )

print()

print("=" * 70)
print("STEP 6 COMPLETED")
print("=" * 70)