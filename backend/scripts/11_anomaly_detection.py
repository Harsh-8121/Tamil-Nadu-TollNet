import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = (
    PROCESSED_DIR /
    "tamil_nadu_analysis_data.csv"
)

ANOMALY_DIR = (
    PROCESSED_DIR /
    "anomalies"
)

ANOMALY_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# START
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - ANOMALY DETECTION")
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

data["TOTAL_CNT"] = pd.to_numeric(
    data["TOTAL_CNT"],
    errors="coerce"
)

data["TOTAL_AMT"] = pd.to_numeric(
    data["TOTAL_AMT"],
    errors="coerce"
)

print()
print("Rows:", len(data))
print("Toll plazas:", data["PLAZA_NAME"].nunique())
print()


# ============================================================
# FUNCTION TO CALCULATE IQR LIMITS
# ============================================================

def get_iqr_limits(values):

    q1 = values.quantile(0.25)

    q3 = values.quantile(0.75)

    iqr = q3 - q1

    lower_limit = q1 - (
        1.5 * iqr
    )

    upper_limit = q3 + (
        1.5 * iqr
    )

    return (
        q1,
        q3,
        iqr,
        lower_limit,
        upper_limit
    )


# ============================================================
# TRAFFIC ANOMALY DETECTION
# ============================================================

traffic_results = []

for plaza_name, group in data.groupby(
    "PLAZA_NAME"
):

    group = group.copy()

    values = group["TOTAL_CNT"].dropna()

    if len(values) < 4:

        group["TRAFFIC_Q1"] = np.nan
        group["TRAFFIC_Q3"] = np.nan
        group["TRAFFIC_IQR"] = np.nan
        group["TRAFFIC_LOWER_LIMIT"] = np.nan
        group["TRAFFIC_UPPER_LIMIT"] = np.nan
        group["TRAFFIC_ANOMALY"] = "Insufficient Data"

    else:

        (
            q1,
            q3,
            iqr,
            lower_limit,
            upper_limit
        ) = get_iqr_limits(values)

        group["TRAFFIC_Q1"] = q1

        group["TRAFFIC_Q3"] = q3

        group["TRAFFIC_IQR"] = iqr

        group["TRAFFIC_LOWER_LIMIT"] = (
            lower_limit
        )

        group["TRAFFIC_UPPER_LIMIT"] = (
            upper_limit
        )

        group["TRAFFIC_ANOMALY"] = "Normal"

        group.loc[
            group["TOTAL_CNT"] <
            lower_limit,
            "TRAFFIC_ANOMALY"
        ] = "Low Traffic Anomaly"

        group.loc[
            group["TOTAL_CNT"] >
            upper_limit,
            "TRAFFIC_ANOMALY"
        ] = "High Traffic Anomaly"

    traffic_results.append(
        group
    )


traffic_data = pd.concat(
    traffic_results,
    ignore_index=True
)


# ============================================================
# REVENUE ANOMALY DETECTION
# ============================================================

revenue_results = []

for plaza_name, group in data.groupby(
    "PLAZA_NAME"
):

    group = group.copy()

    values = group["TOTAL_AMT"].dropna()

    if len(values) < 4:

        group["REVENUE_Q1"] = np.nan
        group["REVENUE_Q3"] = np.nan
        group["REVENUE_IQR"] = np.nan
        group["REVENUE_LOWER_LIMIT"] = np.nan
        group["REVENUE_UPPER_LIMIT"] = np.nan
        group["REVENUE_ANOMALY"] = "Insufficient Data"

    else:

        (
            q1,
            q3,
            iqr,
            lower_limit,
            upper_limit
        ) = get_iqr_limits(values)

        group["REVENUE_Q1"] = q1

        group["REVENUE_Q3"] = q3

        group["REVENUE_IQR"] = iqr

        group["REVENUE_LOWER_LIMIT"] = (
            lower_limit
        )

        group["REVENUE_UPPER_LIMIT"] = (
            upper_limit
        )

        group["REVENUE_ANOMALY"] = "Normal"

        group.loc[
            group["TOTAL_AMT"] <
            lower_limit,
            "REVENUE_ANOMALY"
        ] = "Low Revenue Anomaly"

        group.loc[
            group["TOTAL_AMT"] >
            upper_limit,
            "REVENUE_ANOMALY"
        ] = "High Revenue Anomaly"

    revenue_results.append(
        group
    )


revenue_data = pd.concat(
    revenue_results,
    ignore_index=True
)


# ============================================================
# COMBINE TRAFFIC AND REVENUE RESULTS
# ============================================================

result_columns = [
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


anomaly_data = traffic_data[
    result_columns
].copy()


anomaly_data["TRAFFIC_ANOMALY"] = (
    traffic_data["TRAFFIC_ANOMALY"]
)


anomaly_data["REVENUE_ANOMALY"] = (
    revenue_data["REVENUE_ANOMALY"]
)


# ============================================================
# COMBINED ANOMALY STATUS
# ============================================================

anomaly_data["OVERALL_ANOMALY"] = "Normal"


anomaly_data.loc[
    (
        anomaly_data["TRAFFIC_ANOMALY"]
        .isin(
            [
                "High Traffic Anomaly",
                "Low Traffic Anomaly"
            ]
        )
    )
    |
    (
        anomaly_data["REVENUE_ANOMALY"]
        .isin(
            [
                "High Revenue Anomaly",
                "Low Revenue Anomaly"
            ]
        )
    ),
    "OVERALL_ANOMALY"
] = "Anomaly"


# ============================================================
# CREATE ANOMALY TYPE
# ============================================================

anomaly_data["ANOMALY_TYPE"] = "None"


traffic_only_high = (
    anomaly_data["TRAFFIC_ANOMALY"]
    == "High Traffic Anomaly"
)

traffic_only_low = (
    anomaly_data["TRAFFIC_ANOMALY"]
    == "Low Traffic Anomaly"
)

revenue_only_high = (
    anomaly_data["REVENUE_ANOMALY"]
    == "High Revenue Anomaly"
)

revenue_only_low = (
    anomaly_data["REVENUE_ANOMALY"]
    == "Low Revenue Anomaly"
)


anomaly_data.loc[
    traffic_only_high,
    "ANOMALY_TYPE"
] = "High Traffic"


anomaly_data.loc[
    traffic_only_low,
    "ANOMALY_TYPE"
] = "Low Traffic"


anomaly_data.loc[
    revenue_only_high,
    "ANOMALY_TYPE"
] = "High Revenue"


anomaly_data.loc[
    revenue_only_low,
    "ANOMALY_TYPE"
] = "Low Revenue"


both_high = (
    traffic_only_high &
    revenue_only_high
)


both_low = (
    traffic_only_low &
    revenue_only_low
)


mixed_high = (
    traffic_only_high &
    revenue_only_low
)


mixed_low = (
    traffic_only_low &
    revenue_only_high
)


anomaly_data.loc[
    both_high,
    "ANOMALY_TYPE"
] = "High Traffic + High Revenue"


anomaly_data.loc[
    both_low,
    "ANOMALY_TYPE"
] = "Low Traffic + Low Revenue"


anomaly_data.loc[
    mixed_high,
    "ANOMALY_TYPE"
] = "High Traffic + Low Revenue"


anomaly_data.loc[
    mixed_low,
    "ANOMALY_TYPE"
] = "Low Traffic + High Revenue"


# ============================================================
# SAVE COMPLETE ANOMALY DATA
# ============================================================

COMPLETE_FILE = (
    ANOMALY_DIR /
    "anomaly_results.csv"
)

anomaly_data.to_csv(
    COMPLETE_FILE,
    index=False
)


# ============================================================
# SAVE ONLY ANOMALOUS RECORDS
# ============================================================

ANOMALY_ONLY_FILE = (
    ANOMALY_DIR /
    "anomalous_records.csv"
)

anomalous_records = anomaly_data[
    anomaly_data["OVERALL_ANOMALY"]
    == "Anomaly"
].copy()


anomalous_records.to_csv(
    ANOMALY_ONLY_FILE,
    index=False
)


# ============================================================
# ANOMALY SUMMARY BY PLAZA
# ============================================================

plaza_anomaly_summary = (
    anomalous_records
    .groupby(
        [
            "PLAZA_ID",
            "PLAZA_NAME"
        ]
    )
    .agg(
        ANOMALY_COUNT=(
            "PLAZA_NAME",
            "size"
        ),

        HIGH_TRAFFIC_COUNT=(
            "TRAFFIC_ANOMALY",
            lambda x:
                (
                    x ==
                    "High Traffic Anomaly"
                ).sum()
        ),

        LOW_TRAFFIC_COUNT=(
            "TRAFFIC_ANOMALY",
            lambda x:
                (
                    x ==
                    "Low Traffic Anomaly"
                ).sum()
        ),

        HIGH_REVENUE_COUNT=(
            "REVENUE_ANOMALY",
            lambda x:
                (
                    x ==
                    "High Revenue Anomaly"
                ).sum()
        ),

        LOW_REVENUE_COUNT=(
            "REVENUE_ANOMALY",
            lambda x:
                (
                    x ==
                    "Low Revenue Anomaly"
                ).sum()
        )
    )
    .reset_index()
    .sort_values(
        "ANOMALY_COUNT",
        ascending=False
    )
)


plaza_anomaly_summary.to_csv(
    ANOMALY_DIR /
    "plaza_anomaly_summary.csv",
    index=False
)


# ============================================================
# ANOMALY COUNT BY YEAR
# ============================================================

year_anomaly_summary = (
    anomaly_data
    .groupby("YEAR")
    .agg(
        TOTAL_RECORDS=(
            "PLAZA_NAME",
            "size"
        ),

        ANOMALOUS_RECORDS=(
            "OVERALL_ANOMALY",
            lambda x:
                (
                    x ==
                    "Anomaly"
                ).sum()
        )
    )
    .reset_index()
)


year_anomaly_summary[
    "ANOMALY_PERCENTAGE"
] = (
    year_anomaly_summary["ANOMALOUS_RECORDS"]
    /
    year_anomaly_summary["TOTAL_RECORDS"]
    * 100
)


year_anomaly_summary.to_csv(
    ANOMALY_DIR /
    "year_anomaly_summary.csv",
    index=False
)


# ============================================================
# ANOMALY COUNT BY TYPE
# ============================================================

anomaly_type_summary = (
    anomaly_data
    .groupby(
        "ANOMALY_TYPE"
    )
    .size()
    .reset_index(
        name="COUNT"
    )
    .sort_values(
        "COUNT",
        ascending=False
    )
)


anomaly_type_summary.to_csv(
    ANOMALY_DIR /
    "anomaly_type_summary.csv",
    index=False
)


# ============================================================
# GRAPH 1 — ANOMALY COUNT BY TYPE
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.bar(
    anomaly_type_summary["ANOMALY_TYPE"],
    anomaly_type_summary["COUNT"]
)

plt.title(
    "Anomaly Distribution by Type"
)

plt.xlabel(
    "Anomaly Type"
)

plt.ylabel(
    "Number of Records"
)

plt.xticks(
    rotation=30,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    ANOMALY_DIR /
    "anomaly_distribution.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 2 — ANOMALIES BY YEAR
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.bar(
    year_anomaly_summary["YEAR"].astype(str),
    year_anomaly_summary["ANOMALOUS_RECORDS"]
)

plt.title(
    "Anomalous Records by Year"
)

plt.xlabel(
    "Year"
)

plt.ylabel(
    "Anomalous Records"
)

plt.tight_layout()

plt.savefig(
    ANOMALY_DIR /
    "anomalies_by_year.png",
    dpi=300
)

plt.close()


# ============================================================
# PRINT RESULTS
# ============================================================

print()
print("=" * 70)
print("ANOMALY DETECTION RESULTS")
print("=" * 70)

print()

print(
    "Total records:",
    len(anomaly_data)
)

print(
    "Anomalous records:",
    len(anomalous_records)
)

print(
    "Normal records:",
    len(anomaly_data)
    -
    len(anomalous_records)
)

print()

print(
    "Anomaly percentage:",
    round(
        (
            len(anomalous_records)
            /
            len(anomaly_data)
        ) * 100,
        2
    ),
    "%"
)

print()

print("=" * 70)
print("ANOMALY TYPES")
print("=" * 70)

print()

print(
    anomaly_type_summary.to_string(
        index=False
    )
)

print()

print("=" * 70)
print("TOP PLAZAS BY ANOMALY COUNT")
print("=" * 70)

print()

print(
    plaza_anomaly_summary.head(10).to_string(
        index=False
    )
)

print()

print("=" * 70)
print("OUTPUT FILES")
print("=" * 70)

print()

print(
    "Complete anomaly results:"
)

print(
    COMPLETE_FILE
)

print()

print(
    "Anomalous records:"
)

print(
    ANOMALY_ONLY_FILE
)

print()

print(
    "Anomaly folder:"
)

print(
    ANOMALY_DIR
)

print()

print("=" * 70)
print("STEP 11 COMPLETED")
print("=" * 70)