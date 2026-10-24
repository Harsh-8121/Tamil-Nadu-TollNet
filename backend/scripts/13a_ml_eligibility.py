import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

ANALYSIS_FILE = (
    PROCESSED_DIR /
    "tamil_nadu_analysis_data.csv"
)

ML_FILE = (
    PROCESSED_DIR /
    "ml_dataset.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "ml_plaza_eligibility.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

analysis_data = pd.read_csv(
    ANALYSIS_FILE
)

ml_data = pd.read_csv(
    ML_FILE
)


# ============================================================
# ALL PLAZAS
# ============================================================

all_plazas = (
    analysis_data[
        [
            "PLAZA_ID",
            "PLAZA_NAME"
        ]
    ]
    .drop_duplicates()
)


# ============================================================
# ML ELIGIBLE PLAZAS
# ============================================================

ml_plazas = (
    ml_data[
        [
            "PLAZA_ID",
            "PLAZA_NAME"
        ]
    ]
    .drop_duplicates()
)


# ============================================================
# MERGE
# ============================================================

eligibility = all_plazas.merge(
    ml_plazas,
    on=[
        "PLAZA_ID",
        "PLAZA_NAME"
    ],
    how="left",
    indicator=True
)


# ============================================================
# ELIGIBILITY STATUS
# ============================================================

eligibility["ML_ELIGIBLE"] = (
    eligibility["_merge"]
    == "both"
)


eligibility = eligibility.drop(
    columns=["_merge"]
)


# ============================================================
# REASON
# ============================================================

eligibility["REASON"] = ""

eligibility.loc[
    eligibility["ML_ELIGIBLE"] == True,
    "REASON"
] = "Sufficient historical data"


eligibility.loc[
    eligibility["ML_ELIGIBLE"] == False,
    "REASON"
] = (
    "Insufficient continuous history "
    "for 3-month lag features"
)


# ============================================================
# SORT
# ============================================================

eligibility = eligibility.sort_values(
    by="PLAZA_NAME"
).reset_index(
    drop=True
)


# ============================================================
# SAVE
# ============================================================

eligibility.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# RESULTS
# ============================================================

eligible_count = int(
    eligibility["ML_ELIGIBLE"].sum()
)

not_eligible_count = (
    len(eligibility) -
    eligible_count
)


print("=" * 70)
print("TAMIL NADU TOLLNET - ML PLAZA ELIGIBILITY")
print("=" * 70)

print()

print(
    "Total plazas:",
    len(eligibility)
)

print(
    "ML eligible plazas:",
    eligible_count
)

print(
    "ML ineligible plazas:",
    not_eligible_count
)

print()

print("=" * 70)
print("INELIGIBLE PLAZAS")
print("=" * 70)

print()

ineligible = eligibility[
    eligibility["ML_ELIGIBLE"] == False
]

if len(ineligible) > 0:

    print(
        ineligible.to_string(
            index=False
        )
    )

else:

    print(
        "All plazas are ML eligible."
    )


print()

print(
    "Eligibility file saved at:"
)

print(
    OUTPUT_FILE
)

print()

print("=" * 70)
print("STEP 13A COMPLETED")
print("=" * 70)