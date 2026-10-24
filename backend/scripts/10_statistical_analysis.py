import pandas as pd
import numpy as np
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

STAT_DIR = (
    PROCESSED_DIR /
    "statistics"
)

STAT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - STATISTICAL ANALYSIS")
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


# ============================================================
# NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "TOTAL_CNT",
    "TOTAL_AMT",
    "CAR_JEEP_CNT",
    "LCV_CNT",
    "BUS_TRUCK_CNT",
    "3_AXLE_CNT",
    "4_6_AXLE_CNT",
    "OSV_CNT",
    "CAR_JEEP_AMT",
    "LCV_AMT",
    "BUS_TRUCK_AMT",
    "3_AXLE_AMT",
    "4_6_AXLE_AMT",
    "OSV_AMT",
    "REVENUE_PER_VEHICLE"
]


# ============================================================
# CONVERT NUMERIC
# ============================================================

for column in numeric_columns:

    data[column] = pd.to_numeric(
        data[column],
        errors="coerce"
    )


# ============================================================
# 1. DESCRIPTIVE STATISTICS
# ============================================================

print()
print("=" * 70)
print("DESCRIPTIVE STATISTICS")
print("=" * 70)

descriptive = (
    data[numeric_columns]
    .describe()
    .T
    .reset_index()
)

descriptive = descriptive.rename(
    columns={
        "index": "VARIABLE"
    }
)

descriptive.to_csv(
    STAT_DIR /
    "descriptive_statistics.csv",
    index=False
)


# ============================================================
# 2. ADD MODE
# ============================================================

mode_rows = []

for column in numeric_columns:

    mode_values = (
        data[column]
        .mode()
    )

    if len(mode_values) > 0:

        mode_value = mode_values.iloc[0]

    else:

        mode_value = np.nan

    mode_rows.append(
        [
            column,
            mode_value
        ]
    )


mode_data = pd.DataFrame(
    mode_rows,
    columns=[
        "VARIABLE",
        "MODE"
    ]
)


mode_data.to_csv(
    STAT_DIR /
    "mode_statistics.csv",
    index=False
)


# ============================================================
# 3. VARIANCE + STANDARD DEVIATION
# ============================================================

variation_rows = []

for column in numeric_columns:

    mean_value = data[column].mean()

    std_value = data[column].std()

    variance_value = data[column].var()

    if mean_value != 0:

        coefficient_variation = (
            std_value /
            mean_value
        ) * 100

    else:

        coefficient_variation = 0

    variation_rows.append(
        [
            column,
            mean_value,
            std_value,
            variance_value,
            coefficient_variation
        ]
    )


variation_data = pd.DataFrame(
    variation_rows,
    columns=[
        "VARIABLE",
        "MEAN",
        "STANDARD_DEVIATION",
        "VARIANCE",
        "COEFFICIENT_OF_VARIATION_PERCENT"
    ]
)


variation_data.to_csv(
    STAT_DIR /
    "variation_statistics.csv",
    index=False
)


# ============================================================
# 4. PEARSON CORRELATION
# ============================================================

traffic_revenue_corr = data[
    [
        "TOTAL_CNT",
        "TOTAL_AMT"
    ]
].corr(
    method="pearson"
)


pearson_value = (
    traffic_revenue_corr
    .loc[
        "TOTAL_CNT",
        "TOTAL_AMT"
    ]
)


pearson_summary = pd.DataFrame(
    {
        "VARIABLE_1": [
            "TOTAL_TRAFFIC"
        ],

        "VARIABLE_2": [
            "TOTAL_REVENUE"
        ],

        "PEARSON_CORRELATION": [
            pearson_value
        ]
    }
)


pearson_summary.to_csv(
    STAT_DIR /
    "pearson_traffic_revenue.csv",
    index=False
)


# ============================================================
# 5. FULL CORRELATION MATRIX
# ============================================================

correlation_matrix = (
    data[numeric_columns]
    .corr(
        method="pearson"
    )
)


correlation_matrix.to_csv(
    STAT_DIR /
    "full_correlation_matrix.csv"
)


# ============================================================
# 6. YEAR-WISE STATISTICS
# ============================================================

year_statistics = (
    data
    .groupby("YEAR")
    .agg(
        TOTAL_TRAFFIC=("TOTAL_CNT", "sum"),
        TOTAL_REVENUE=("TOTAL_AMT", "sum"),
        MEAN_TRAFFIC=("TOTAL_CNT", "mean"),
        MEDIAN_TRAFFIC=("TOTAL_CNT", "median"),
        STD_TRAFFIC=("TOTAL_CNT", "std"),
        VARIANCE_TRAFFIC=("TOTAL_CNT", "var"),
        MEAN_REVENUE=("TOTAL_AMT", "mean"),
        MEDIAN_REVENUE=("TOTAL_AMT", "median"),
        STD_REVENUE=("TOTAL_AMT", "std"),
        VARIANCE_REVENUE=("TOTAL_AMT", "var"),
        TOLL_PLAZAS=("PLAZA_NAME", "nunique")
    )
    .reset_index()
    .sort_values("YEAR")
)


# ============================================================
# YEAR-WISE GROWTH
# ============================================================

year_statistics["TRAFFIC_GROWTH_PERCENT"] = (
    year_statistics["TOTAL_TRAFFIC"]
    .pct_change()
    * 100
)


year_statistics["REVENUE_GROWTH_PERCENT"] = (
    year_statistics["TOTAL_REVENUE"]
    .pct_change()
    * 100
)


year_statistics.to_csv(
    STAT_DIR /
    "year_wise_statistics.csv",
    index=False
)


# ============================================================
# 7. VEHICLE CATEGORY STATISTICS
# ============================================================

count_columns = [
    "CAR_JEEP_CNT",
    "LCV_CNT",
    "BUS_TRUCK_CNT",
    "3_AXLE_CNT",
    "4_6_AXLE_CNT",
    "OSV_CNT"
]


amount_columns = [
    "CAR_JEEP_AMT",
    "LCV_AMT",
    "BUS_TRUCK_AMT",
    "3_AXLE_AMT",
    "4_6_AXLE_AMT",
    "OSV_AMT"
]


category_names = [
    "Car/Jeep",
    "LCV",
    "Bus/Truck",
    "3-Axle",
    "4-6 Axle",
    "OSV"
]


category_rows = []

for i in range(
    len(category_names)
):

    category = category_names[i]

    count_column = count_columns[i]

    amount_column = amount_columns[i]

    count_data = data[
        count_column
    ]

    amount_data = data[
        amount_column
    ]

    total_count = count_data.sum()

    total_revenue = amount_data.sum()

    mean_count = count_data.mean()

    median_count = count_data.median()

    std_count = count_data.std()

    mean_revenue = amount_data.mean()

    median_revenue = amount_data.median()

    std_revenue = amount_data.std()

    if total_count > 0:

        revenue_per_vehicle = (
            total_revenue /
            total_count
        )

    else:

        revenue_per_vehicle = 0

    category_rows.append(
        [
            category,
            total_count,
            total_revenue,
            mean_count,
            median_count,
            std_count,
            mean_revenue,
            median_revenue,
            std_revenue,
            revenue_per_vehicle
        ]
    )


category_statistics = pd.DataFrame(
    category_rows,
    columns=[
        "VEHICLE_CATEGORY",
        "TOTAL_TRAFFIC",
        "TOTAL_REVENUE",
        "MEAN_TRAFFIC",
        "MEDIAN_TRAFFIC",
        "STD_TRAFFIC",
        "MEAN_REVENUE",
        "MEDIAN_REVENUE",
        "STD_REVENUE",
        "REVENUE_PER_VEHICLE"
    ]
)


category_statistics.to_csv(
    STAT_DIR /
    "vehicle_category_statistics.csv",
    index=False
)


# ============================================================
# 8. PLAZA-WISE STATISTICS
# ============================================================

plaza_statistics = (
    data
    .groupby(
        [
            "PLAZA_ID",
            "PLAZA_NAME"
        ]
    )
    .agg(
        RECORD_COUNT=("PLAZA_NAME", "size"),
        TOTAL_TRAFFIC=("TOTAL_CNT", "sum"),
        TOTAL_REVENUE=("TOTAL_AMT", "sum"),
        MEAN_TRAFFIC=("TOTAL_CNT", "mean"),
        MEDIAN_TRAFFIC=("TOTAL_CNT", "median"),
        STD_TRAFFIC=("TOTAL_CNT", "std"),
        MIN_TRAFFIC=("TOTAL_CNT", "min"),
        MAX_TRAFFIC=("TOTAL_CNT", "max"),
        MEAN_REVENUE=("TOTAL_AMT", "mean"),
        MEDIAN_REVENUE=("TOTAL_AMT", "median"),
        STD_REVENUE=("TOTAL_AMT", "std"),
        MIN_REVENUE=("TOTAL_AMT", "min"),
        MAX_REVENUE=("TOTAL_AMT", "max")
    )
    .reset_index()
)


plaza_statistics.to_csv(
    STAT_DIR /
    "plaza_wise_statistics.csv",
    index=False
)


# ============================================================
# 9. MONTH-WISE STATISTICS
# ============================================================

month_statistics = (
    data
    .groupby(
        [
            "MONTH_NUMBER",
            "MONTH"
        ]
    )
    .agg(
        TOTAL_TRAFFIC=("TOTAL_CNT", "sum"),
        TOTAL_REVENUE=("TOTAL_AMT", "sum"),
        MEAN_TRAFFIC=("TOTAL_CNT", "mean"),
        MEDIAN_TRAFFIC=("TOTAL_CNT", "median"),
        STD_TRAFFIC=("TOTAL_CNT", "std"),
        MEAN_REVENUE=("TOTAL_AMT", "mean"),
        MEDIAN_REVENUE=("TOTAL_AMT", "median"),
        STD_REVENUE=("TOTAL_AMT", "std")
    )
    .reset_index()
    .sort_values(
        "MONTH_NUMBER"
    )
)


month_statistics.to_csv(
    STAT_DIR /
    "month_wise_statistics.csv",
    index=False
)


# ============================================================
# 10. TRAFFIC VS REVENUE CORRELATION BY VEHICLE CATEGORY
# ============================================================

category_correlation_rows = []

for i in range(
    len(category_names)
):

    category = category_names[i]

    count_column = count_columns[i]

    amount_column = amount_columns[i]

    correlation = (
        data[
            [
                count_column,
                amount_column
            ]
        ]
        .corr(
            method="pearson"
        )
        .loc[
            count_column,
            amount_column
        ]
    )

    category_correlation_rows.append(
        [
            category,
            count_column,
            amount_column,
            correlation
        ]
    )


category_correlation = pd.DataFrame(
    category_correlation_rows,
    columns=[
        "VEHICLE_CATEGORY",
        "TRAFFIC_COLUMN",
        "REVENUE_COLUMN",
        "PEARSON_CORRELATION"
    ]
)


category_correlation.to_csv(
    STAT_DIR /
    "category_traffic_revenue_correlation.csv",
    index=False
)


# ============================================================
# PRINT IMPORTANT RESULTS
# ============================================================

print()
print("=" * 70)
print("STATISTICAL ANALYSIS RESULTS")
print("=" * 70)

print()

print(
    "Total traffic:",
    data["TOTAL_CNT"].sum()
)

print(
    "Total revenue:",
    data["TOTAL_AMT"].sum()
)

print()

print(
    "Pearson correlation between traffic and revenue:"
)

print(
    round(
        pearson_value,
        6
    )
)

print()

print("=" * 70)
print("YEAR-WISE STATISTICS")
print("=" * 70)

print()

print(
    year_statistics[
        [
            "YEAR",
            "TOLL_PLAZAS",
            "TOTAL_TRAFFIC",
            "TOTAL_REVENUE",
            "TRAFFIC_GROWTH_PERCENT",
            "REVENUE_GROWTH_PERCENT"
        ]
    ].to_string(
        index=False
    )
)

print()

print("=" * 70)
print("VEHICLE CATEGORY STATISTICS")
print("=" * 70)

print()

print(
    category_statistics.to_string(
        index=False
    )
)

print()

print("=" * 70)
print("CATEGORY TRAFFIC-REVENUE CORRELATION")
print("=" * 70)

print()

print(
    category_correlation.to_string(
        index=False
    )
)

print()

print("=" * 70)
print("OUTPUT FILES")
print("=" * 70)

print()

print(
    "Statistics folder:"
)

print(
    STAT_DIR
)

print()

print(
    "Statistical analysis completed."
)

print()

print("=" * 70)
print("STEP 10 COMPLETED")
print("=" * 70)