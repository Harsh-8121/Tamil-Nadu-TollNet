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
    "monthly_continuity_report.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - MONTHLY CONTINUITY CHECK")
print("=" * 70)

print()

print("Loading:")
print(INPUT_FILE)

data = pd.read_csv(
    INPUT_FILE
)

data["DATE"] = pd.to_datetime(
    data["DATE"],
    errors="coerce"
)

data["MONTH_NUMBER"] = pd.to_numeric(
    data["MONTH_NUMBER"],
    errors="coerce"
)

data["YEAR"] = pd.to_numeric(
    data["YEAR"],
    errors="coerce"
)


# ============================================================
# CREATE MONTH INDEX
# ============================================================

data["MONTH_INDEX"] = (
    data["YEAR"] * 12
    +
    data["MONTH_NUMBER"]
)


# ============================================================
# CHECK EACH PLAZA
# ============================================================

results = []

for plaza_id, group in data.groupby(
    "PLAZA_ID"
):

    group = group.sort_values(
        "DATE"
    )

    plaza_name = (
        group["PLAZA_NAME"]
        .iloc[0]
    )

    month_indices = sorted(
        group["MONTH_INDEX"]
        .dropna()
        .astype(int)
        .unique()
    )

    missing_months = []

    if len(month_indices) > 1:

        first_month = month_indices[0]

        last_month = month_indices[-1]

        expected_months = range(
            first_month,
            last_month + 1
        )

        existing_months = set(
            month_indices
        )

        for month_index in expected_months:

            if month_index not in existing_months:

                year = (
                    month_index - 1
                ) // 12

                month = (
                    month_index - 1
                ) % 12 + 1

                missing_months.append(
                    f"{year}-{month:02d}"
                )


    results.append(
        [
            plaza_id,
            plaza_name,
            len(month_indices),
            len(missing_months),
            ", ".join(missing_months)
        ]
    )


# ============================================================
# CREATE REPORT
# ============================================================

report = pd.DataFrame(
    results,
    columns=[
        "PLAZA_ID",
        "PLAZA_NAME",
        "AVAILABLE_MONTHS",
        "MISSING_MONTH_COUNT",
        "MISSING_MONTHS"
    ]
)


report["CONTINUOUS_HISTORY"] = (
    report["MISSING_MONTH_COUNT"] == 0
)


report = report.sort_values(
    by="PLAZA_NAME"
).reset_index(
    drop=True
)


# ============================================================
# SAVE
# ============================================================

report.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

continuous_count = int(
    report["CONTINUOUS_HISTORY"].sum()
)

gap_count = (
    len(report) -
    continuous_count
)


print()
print("=" * 70)
print("CONTINUITY RESULTS")
print("=" * 70)

print()

print(
    "Total toll plazas:",
    len(report)
)

print(
    "Plazas with continuous monthly history:",
    continuous_count
)

print(
    "Plazas with one or more missing months:",
    gap_count
)

print()

print("=" * 70)
print("PLAZAS WITH MISSING MONTHS")
print("=" * 70)

print()

gaps = report[
    report["CONTINUOUS_HISTORY"] == False
]

if len(gaps) > 0:

    print(
        gaps.to_string(
            index=False
        )
    )

else:

    print(
        "No monthly gaps found."
    )


print()

print(
    "Report saved at:"
)

print(
    OUTPUT_FILE
)

print()

print("=" * 70)
print("STEP 13B COMPLETED")
print("=" * 70)