import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = (
    PROCESSED_DIR /
    "all_india_toll_data_2022_2026.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "tamil_nadu_candidates.csv"
)


# ============================================================
# LOAD COMBINED DATA
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - TAMIL NADU PLAZA CANDIDATES")
print("=" * 70)

print()

print("Loading:")
print(INPUT_FILE)

data = pd.read_csv(
    INPUT_FILE
)


# ============================================================
# CLEAN RO
# ============================================================

data["RO"] = (
    data["RO"]
    .astype(str)
    .str.strip()
    .str.upper()
)


# ============================================================
# GET TAMIL NADU CANDIDATES
#
# Chennai and Madurai are used only as CANDIDATE ROs.
# We will verify the final list separately.
# ============================================================

tn_candidates = data[
    data["RO"].isin(
        [
            "CHENNAI",
            "MADURAI"
        ]
    )
].copy()


# ============================================================
# UNIQUE PLAZA INFORMATION
# ============================================================

tn_plazas = (
    tn_candidates[
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


# ============================================================
# ADD A TEMPORARY ID
# ============================================================

tn_plazas.insert(
    0,
    "CANDIDATE_ID",
    range(
        1,
        len(tn_plazas) + 1
    )
)


# ============================================================
# SAVE CANDIDATES
# ============================================================

tn_plazas.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()

print(
    "Total candidate records:",
    len(tn_candidates)
)

print(
    "Unique candidate toll plazas:",
    tn_plazas["PLAZA_NAME"].nunique()
)

print()

print(
    "Candidate file saved at:"
)

print(
    OUTPUT_FILE
)

print()

print("=" * 70)
print("CANDIDATE EXTRACTION COMPLETED")
print("=" * 70)