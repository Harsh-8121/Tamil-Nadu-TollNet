import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = (
    PROCESSED_DIR /
    "tamil_nadu_toll_data_cleaned.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "missing_value_analysis.csv"
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
print("TAMIL NADU TOLLNET - MISSING VALUE ANALYSIS")
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
# MISSING VALUES BY COLUMN
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
# KNOWN COUNT SUM
# ============================================================

data["KNOWN_COUNT_SUM"] = (
    data[COUNT_COLUMNS]
    .sum(
        axis=1,
        skipna=True
    )
)


# ============================================================
# COUNT DIFFERENCE
# ============================================================

data["COUNT_MISSING_DIFFERENCE"] = (
    data["TOTAL_CNT"] -
    data["KNOWN_COUNT_SUM"]
)


# ============================================================
# COUNT STATUS
# ============================================================

data["COUNT_STATUS"] = "No Missing Count"


count_missing_mask = (
    data[COUNT_COLUMNS]
    .isna()
    .any(axis=1)
)


data.loc[
    count_missing_mask,
    "COUNT_STATUS"
] = "Cannot determine"


data.loc[
    count_missing_mask
    &
    (
        data["COUNT_MISSING_DIFFERENCE"]
        .abs()
        < 0.01
    ),
    "COUNT_STATUS"
] = "Missing categories are consistent with ZERO"


data.loc[
    count_missing_mask
    &
    (
        data["COUNT_MISSING_DIFFERENCE"]
        .abs()
        >= 0.01
    ),
    "COUNT_STATUS"
] = "Missing count may contain actual vehicles"


# ============================================================
# KNOWN REVENUE SUM
# ============================================================

data["KNOWN_AMOUNT_SUM"] = (
    data[AMOUNT_COLUMNS]
    .sum(
        axis=1,
        skipna=True
    )
)


# ============================================================
# REVENUE DIFFERENCE
# ============================================================

data["AMOUNT_MISSING_DIFFERENCE"] = (
    data["TOTAL_AMT"] -
    data["KNOWN_AMOUNT_SUM"]
)


# ============================================================
# REVENUE STATUS
# ============================================================

data["AMOUNT_STATUS"] = "No Missing Revenue"


amount_missing_mask = (
    data[AMOUNT_COLUMNS]
    .isna()
    .any(axis=1)
)


data.loc[
    amount_missing_mask,
    "AMOUNT_STATUS"
] = "Cannot determine"


data.loc[
    amount_missing_mask
    &
    (
        data["AMOUNT_MISSING_DIFFERENCE"]
        .abs()
        < 0.01
    ),
    "AMOUNT_STATUS"
] = "Missing revenue is consistent with ZERO"


data.loc[
    amount_missing_mask
    &
    (
        data["AMOUNT_MISSING_DIFFERENCE"]
        .abs()
        >= 0.01
    ),
    "AMOUNT_STATUS"
] = "Missing revenue may contain actual value"


# ============================================================
# SELECT ONLY RELEVANT RECORDS
# ============================================================

analysis = data.loc[
    count_missing_mask |
    amount_missing_mask
].copy()


# ============================================================
# COLUMNS FOR OUTPUT
# ============================================================

analysis_columns = [
    "PLAZA_ID",
    "PLAZA_NAME",
    "PIU",
    "RO",
    "YEAR",
    "MONTH",
    "DATE"
] + COUNT_COLUMNS + [
    "TOTAL_CNT",
    "KNOWN_COUNT_SUM",
    "COUNT_MISSING_DIFFERENCE",
    "COUNT_STATUS"
] + AMOUNT_COLUMNS + [
    "TOTAL_AMT",
    "KNOWN_AMOUNT_SUM",
    "AMOUNT_MISSING_DIFFERENCE",
    "AMOUNT_STATUS"
]


analysis = analysis[
    analysis_columns
]


# ============================================================
# SAVE
# ============================================================

analysis.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("MISSING VALUE ANALYSIS RESULTS")
print("=" * 70)

print()

print(
    "Rows with missing count values:",
    int(count_missing_mask.sum())
)

print(
    "Rows with missing revenue values:",
    int(amount_missing_mask.sum())
)

print(
    "Rows requiring investigation:",
    len(analysis)
)

print()

# Count classification

count_zero = int(
    (
        data["COUNT_STATUS"]
        ==
        "Missing categories are consistent with ZERO"
    ).sum()
)

count_nonzero = int(
    (
        data["COUNT_STATUS"]
        ==
        "Missing count may contain actual vehicles"
    ).sum()
)

print("Count missing-value classification:")
print(
    "  Consistent with ZERO:",
    count_zero
)
print(
    "  May contain actual vehicles:",
    count_nonzero
)

print()

# Revenue classification

amount_zero = int(
    (
        data["AMOUNT_STATUS"]
        ==
        "Missing revenue is consistent with ZERO"
    ).sum()
)

amount_nonzero = int(
    (
        data["AMOUNT_STATUS"]
        ==
        "Missing revenue may contain actual value"
    ).sum()
)

print("Revenue missing-value classification:")
print(
    "  Consistent with ZERO:",
    amount_zero
)
print(
    "  May contain actual revenue:",
    amount_nonzero
)

print()

print(
    "Detailed analysis saved at:"
)

print(
    OUTPUT_FILE
)

print()

print("=" * 70)
print("STEP 7 COMPLETED")
print("=" * 70)