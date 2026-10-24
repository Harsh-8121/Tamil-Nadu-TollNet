import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = (
    PROCESSED_DIR /
    "tamil_nadu_candidates.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "tn_master_review.csv"
)


# ============================================================
# LOAD CANDIDATE DATA
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - MASTER TABLE REVIEW")
print("=" * 70)

print()

print("Loading:")
print(INPUT_FILE)

data = pd.read_csv(
    INPUT_FILE
)


# ============================================================
# CLEAN TEXT
# ============================================================

for column in [
    "PLAZA_NAME",
    "PIU",
    "RO"
]:

    data[column] = (
        data[column]
        .fillna("")
        .astype(str)
        .str.strip()
    )


# ============================================================
# NORMALIZED PLAZA NAME
#
# Used only to help identify possible naming variations.
# It does NOT decide whether two plazas are the same.
# ============================================================

data["NORMALIZED_NAME"] = (
    data["PLAZA_NAME"]
    .str.upper()
    .str.replace("TOLL PLAZA", "", regex=False)
    .str.replace("TOLL PLAZA ", "", regex=False)
    .str.replace("TOLL", "", regex=False)
    .str.replace("PLAZA", "", regex=False)
    .str.replace("  ", " ", regex=False)
    .str.strip()
)


# ============================================================
# ADD REVIEW COLUMNS
#
# These will be completed after official verification.
# ============================================================

data["STATE"] = ""

data["DISTRICT"] = ""

data["STANDARD_NAME"] = ""

data["INCLUDE_TN"] = ""


# ============================================================
# SORT
# ============================================================

data = data.sort_values(
    by=[
        "PLAZA_NAME",
        "RO",
        "PIU"
    ]
)


data = data.reset_index(
    drop=True
)


# ============================================================
# ASSIGN REVIEW ID
# ============================================================

data.insert(
    0,
    "REVIEW_ID",
    range(
        1,
        len(data) + 1
    )
)


# ============================================================
# SAVE REVIEW FILE
# ============================================================

data.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# DISPLAY SUMMARY
# ============================================================

print()

print(
    "Candidate records:",
    len(data)
)

print(
    "Unique plaza names:",
    data["PLAZA_NAME"].nunique()
)

print()

print(
    "Review file created:"
)

print(
    OUTPUT_FILE
)

print()

print("Columns:")

for column in data.columns:

    print(
        " -",
        column
    )


# ============================================================
# DISPLAY ALL PLAZA NAMES
# ============================================================

print()
print("=" * 70)
print("CANDIDATE TOLL PLAZAS")
print("=" * 70)

unique_names = (
    data[
        [
            "PLAZA_NAME"
        ]
    ]
    .drop_duplicates()
    .sort_values(
        by="PLAZA_NAME"
    )
)


for index, row in unique_names.iterrows():

    print(
        row["PLAZA_NAME"]
    )


print()
print("=" * 70)
print("MASTER REVIEW PREPARATION COMPLETED")
print("=" * 70)