import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = (
    PROCESSED_DIR /
    "tamil_nadu_analysis_data.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "plaza_month_duplicates.csv"
)


# ============================================================
# START
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - PLAZA-MONTH DUPLICATE CHECK")
print("=" * 70)

print()

print("Loading:")
print(INPUT_FILE)

data = pd.read_csv(
    INPUT_FILE
)


# ============================================================
# CREATE MONTH INDEX
# ============================================================

data["YEAR"] = pd.to_numeric(
    data["YEAR"],
    errors="coerce"
)

data["MONTH_NUMBER"] = pd.to_numeric(
    data["MONTH_NUMBER"],
    errors="coerce"
)


data["MONTH_INDEX"] = (
    data["YEAR"] * 12
    +
    data["MONTH_NUMBER"]
)


# ============================================================
# FIND DUPLICATE PLAZA + MONTH
# ============================================================

duplicate_mask = data.duplicated(
    subset=[
        "PLAZA_ID",
        "MONTH_INDEX"
    ],
    keep=False
)


duplicates = data[
    duplicate_mask
].copy()


# ============================================================
# SORT
# ============================================================

duplicates = duplicates.sort_values(
    by=[
        "PLAZA_ID",
        "MONTH_INDEX",
        "SOURCE_FILE"
    ]
)


# ============================================================
# SAVE
# ============================================================

duplicates.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()

print("=" * 70)
print("RESULTS")
print("=" * 70)

print()

print(
    "Duplicate plaza-month rows:",
    len(duplicates)
)

print(
    "Duplicate plaza-month groups:",
    duplicates[
        [
            "PLAZA_ID",
            "MONTH_INDEX"
        ]
    ]
    .drop_duplicates()
    .shape[0]
)

print()


# ============================================================
# DISPLAY DUPLICATES
# ============================================================

if len(duplicates) > 0:

    print("=" * 70)
    print("DUPLICATE PLAZA-MONTH RECORDS")
    print("=" * 70)

    print()

    display_columns = [
        "PLAZA_ID",
        "PLAZA_NAME",
        "YEAR",
        "MONTH",
        "PIU",
        "RO",
        "TOTAL_CNT",
        "TOTAL_AMT",
        "SOURCE_FILE"
    ]

    print(
        duplicates[
            display_columns
        ].to_string(
            index=False
        )
    )

else:

    print(
        "No plaza-month duplicates found."
    )


print()

print(
    "Detailed duplicate file saved at:"
)

print(
    OUTPUT_FILE
)

print()

print("=" * 70)
print("STEP 13C COMPLETED")
print("=" * 70)