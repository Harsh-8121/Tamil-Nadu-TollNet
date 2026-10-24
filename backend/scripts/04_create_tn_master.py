import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "tn_master_review.csv"

MASTER_FILE = PROCESSED_DIR / "tamil_nadu_plaza_master.csv"

TN_DATA_FILE = PROCESSED_DIR / "tamil_nadu_toll_data.csv"


# ============================================================
# LOAD REVIEW FILE
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - FINAL TAMIL NADU MASTER")
print("=" * 70)

print()

print("Loading:")
print(INPUT_FILE)

review = pd.read_csv(INPUT_FILE)


# ============================================================
# CLEAN PLAZA NAME
# ============================================================

review["PLAZA_NAME"] = (
    review["PLAZA_NAME"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ============================================================
# STANDARD NAME MAPPING
# ============================================================

name_mapping = {

    "Madukkarai Toll Plaza": "Madukkarai",
    "Madukkarai": "Madukkarai",

    "Kotthatai": "Kothattai",
    "Kothattai": "Kothattai",

    "Vikkravandi Toll Plaza": "Vikravandi",

    "VAGAIKULAM  Toll Plaza": "Vagaikulam",
    "VAGAIKULAM Toll Plaza": "Vagaikulam",

    "Valvanthankottai": "Valavanthankottai",
    "Valavanthankottai": "Valavanthankottai",

    "SURAPATTU TOLL PLAZA": "Surapattu",
    "SURAPATTU": "Surapattu",

    "SriPerumbadur": "Sriperumbudur",

    "Pollachi Cochin Toll Plaza":
        "Pollachi Cochin Toll Plaza",

    "Pollachi Salem Toll Plaza":
        "Pollachi Salem Toll Plaza",

    "Trichy Salem":
        "Trichy Salem",

    "Trichy Cochin":
        "Trichy Cochin",

    "Pondicherry Tindivanam Toll P":
        "Pondicherry Tindivanam Toll P"
}


# ============================================================
# APPLY STANDARD NAME
# ============================================================

review["STANDARD_NAME"] = (
    review["PLAZA_NAME"]
    .map(name_mapping)
    .fillna(review["PLAZA_NAME"])
    .str.strip()
)


# ============================================================
# TAMIL NADU FILTER
#
# Pondicherry Tindivanam is excluded.
# ============================================================

review["INCLUDE_TN"] = True

review.loc[
    review["PLAZA_NAME"].str.upper()
    == "PONDICHERRY TINDIVANAM TOLL P",
    "INCLUDE_TN"
] = False


# ============================================================
# STATE
# ============================================================

review["STATE"] = "Tamil Nadu"

review.loc[
    review["INCLUDE_TN"] == False,
    "STATE"
] = "Puducherry"


# ============================================================
# KEEP ONLY TAMIL NADU
# ============================================================

tn_review = review[
    review["INCLUDE_TN"] == True
].copy()


# ============================================================
# CREATE PLAZA MASTER
#
# ONE ROW PER STANDARD PLAZA
# ============================================================

master = (
    tn_review[
        [
            "STANDARD_NAME",
            "PIU",
            "RO",
            "STATE"
        ]
    ]
    .groupby(
        "STANDARD_NAME",
        as_index=False
    )
    .agg(
        PIU=("PIU", "first"),
        RO=("RO", "first"),
        STATE=("STATE", "first")
    )
)


# ============================================================
# RENAME STANDARD NAME
# ============================================================

master = master.rename(
    columns={
        "STANDARD_NAME": "PLAZA_NAME"
    }
)


# ============================================================
# SORT MASTER
# ============================================================

master = master.sort_values(
    by="PLAZA_NAME"
).reset_index(
    drop=True
)


# ============================================================
# ASSIGN PLAZA ID
# ============================================================

master.insert(
    0,
    "PLAZA_ID",
    [
        "TN" + str(i).zfill(3)
        for i in range(
            1,
            len(master) + 1
        )
    ]
)


# ============================================================
# SAVE PLAZA MASTER
# ============================================================

master.to_csv(
    MASTER_FILE,
    index=False
)


# ============================================================
# LOAD COMBINED ALL-INDIA DATA
# ============================================================

ALL_INDIA_FILE = (
    PROCESSED_DIR /
    "all_india_toll_data_2022_2026.csv"
)

all_data = pd.read_csv(
    ALL_INDIA_FILE
)


# ============================================================
# STANDARDIZE SOURCE PLAZA NAMES
# ============================================================

all_data["STANDARD_NAME"] = (
    all_data["PLAZA_NAME"]
    .fillna("")
    .astype(str)
    .str.strip()
    .map(name_mapping)
    .fillna(
        all_data["PLAZA_NAME"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
)


# ============================================================
# MERGE ONLY PLAZA ID + STATE
#
# IMPORTANT:
# We DO NOT merge PIU and RO because they already exist
# in the original source dataset.
# ============================================================

master_for_merge = master[
    [
        "PLAZA_ID",
        "PLAZA_NAME",
        "STATE"
    ]
].copy()


tn_data = all_data.merge(
    master_for_merge,
    left_on="STANDARD_NAME",
    right_on="PLAZA_NAME",
    how="inner"
)


# ============================================================
# RENAME ORIGINAL PLAZA NAME
# ============================================================

tn_data = tn_data.rename(
    columns={
        "PLAZA_NAME_x": "RAW_PLAZA_NAME",
        "PLAZA_NAME_y": "PLAZA_NAME"
    }
)


# ============================================================
# DROP TEMPORARY COLUMN
# ============================================================

if "STANDARD_NAME" in tn_data.columns:

    tn_data = tn_data.drop(
        columns=["STANDARD_NAME"]
    )


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

final_columns = [
    "PLAZA_ID",
    "PLAZA_NAME",
    "PIU",
    "RO",
    "STATE",

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
    "TOTAL_AMT",

    "YEAR",
    "MONTH",
    "MONTH_NUMBER",
    "DATE",
    "SOURCE_FILE"
]


# ============================================================
# KEEP AVAILABLE COLUMNS
# ============================================================

available_columns = []

for column in final_columns:

    if column in tn_data.columns:

        available_columns.append(column)


tn_data = tn_data[
    available_columns
]


# ============================================================
# SORT FINAL DATASET
# ============================================================

tn_data = tn_data.sort_values(
    by=[
        "DATE",
        "PLAZA_NAME"
    ]
).reset_index(
    drop=True
)


# ============================================================
# SAVE TAMIL NADU DATASET
# ============================================================

tn_data.to_csv(
    TN_DATA_FILE,
    index=False
)


# ============================================================
# FINAL REPORT
# ============================================================

print()
print("=" * 70)
print("MASTER TABLE CREATED")
print("=" * 70)

print()

print(
    "Tamil Nadu toll plazas:",
    len(master)
)

print(
    "Tamil Nadu data records:",
    len(tn_data)
)

print()

print(
    "Master table saved:"
)

print(
    MASTER_FILE
)

print()

print(
    "Tamil Nadu dataset saved:"
)

print(
    TN_DATA_FILE
)

print()

print("Tamil Nadu dataset columns:")

for column in tn_data.columns:

    print(
        " -",
        column
    )

print()

print("=" * 70)
print("STEP 4 COMPLETED SUCCESSFULLY")
print("=" * 70)