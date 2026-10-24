import pandas as pd
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

EDA_DIR = (
    PROCESSED_DIR /
    "eda"
)

EDA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# START
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - EXPLORATORY DATA ANALYSIS")
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

print()
print("Rows:", len(data))
print("Columns:", len(data.columns))
print()


# ============================================================
# VEHICLE CATEGORY DEFINITIONS
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


# ============================================================
# BASIC NUMERIC CONVERSION
# ============================================================

numeric_columns = (
    count_columns +
    amount_columns +
    [
        "TOTAL_CNT",
        "TOTAL_AMT",
        "REVENUE_PER_VEHICLE"
    ]
)

for column in numeric_columns:

    data[column] = pd.to_numeric(
        data[column],
        errors="coerce"
    )


# ============================================================
# 1. OVERALL SUMMARY
# ============================================================

overall_summary = pd.DataFrame(
    {
        "METRIC": [
            "Total Toll Plazas",
            "Total Records",
            "Total Traffic",
            "Total Revenue",
            "Average Traffic per Record",
            "Median Traffic per Record",
            "Maximum Traffic",
            "Minimum Traffic",
            "Average Revenue per Record",
            "Median Revenue per Record",
            "Maximum Revenue",
            "Minimum Revenue"
        ],

        "VALUE": [
            data["PLAZA_NAME"].nunique(),
            len(data),
            data["TOTAL_CNT"].sum(),
            data["TOTAL_AMT"].sum(),
            data["TOTAL_CNT"].mean(),
            data["TOTAL_CNT"].median(),
            data["TOTAL_CNT"].max(),
            data["TOTAL_CNT"].min(),
            data["TOTAL_AMT"].mean(),
            data["TOTAL_AMT"].median(),
            data["TOTAL_AMT"].max(),
            data["TOTAL_AMT"].min()
        ]
    }
)

overall_summary.to_csv(
    EDA_DIR / "overall_summary.csv",
    index=False
)


# ============================================================
# 2. YEAR-WISE SUMMARY
# ============================================================

year_summary = (
    data
    .groupby("YEAR")
    .agg(
        TOLL_PLAZAS=("PLAZA_NAME", "nunique"),
        TOTAL_TRAFFIC=("TOTAL_CNT", "sum"),
        TOTAL_REVENUE=("TOTAL_AMT", "sum"),
        AVERAGE_TRAFFIC=("TOTAL_CNT", "mean"),
        MEDIAN_TRAFFIC=("TOTAL_CNT", "median"),
        AVERAGE_REVENUE=("TOTAL_AMT", "mean"),
        MEDIAN_REVENUE=("TOTAL_AMT", "median")
    )
    .reset_index()
    .sort_values("YEAR")
)

year_summary.to_csv(
    EDA_DIR / "year_summary.csv",
    index=False
)


# ============================================================
# 3. MONTH-WISE SUMMARY
# ============================================================

month_summary = (
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
        AVERAGE_TRAFFIC=("TOTAL_CNT", "mean"),
        AVERAGE_REVENUE=("TOTAL_AMT", "mean")
    )
    .reset_index()
    .sort_values("MONTH_NUMBER")
)

month_summary.to_csv(
    EDA_DIR / "month_summary.csv",
    index=False
)


# ============================================================
# 4. TOLL PLAZA SUMMARY
# ============================================================

plaza_summary = (
    data
    .groupby(
        [
            "PLAZA_ID",
            "PLAZA_NAME",
            "RO"
        ]
    )
    .agg(
        RECORDS=("PLAZA_NAME", "size"),
        TOTAL_TRAFFIC=("TOTAL_CNT", "sum"),
        TOTAL_REVENUE=("TOTAL_AMT", "sum"),
        AVERAGE_TRAFFIC=("TOTAL_CNT", "mean"),
        AVERAGE_REVENUE=("TOTAL_AMT", "mean"),
        MAX_TRAFFIC=("TOTAL_CNT", "max"),
        MIN_TRAFFIC=("TOTAL_CNT", "min")
    )
    .reset_index()
)


plaza_summary["REVENUE_PER_VEHICLE"] = 0.0

valid_plaza_rows = (
    plaza_summary["TOTAL_TRAFFIC"] > 0
)

plaza_summary.loc[
    valid_plaza_rows,
    "REVENUE_PER_VEHICLE"
] = (
    plaza_summary.loc[
        valid_plaza_rows,
        "TOTAL_REVENUE"
    ]
    /
    plaza_summary.loc[
        valid_plaza_rows,
        "TOTAL_TRAFFIC"
    ]
)


plaza_summary = plaza_summary.sort_values(
    "TOTAL_TRAFFIC",
    ascending=False
)

plaza_summary.to_csv(
    EDA_DIR / "plaza_summary.csv",
    index=False
)


# ============================================================
# 5. VEHICLE CATEGORY SUMMARY
# ============================================================

vehicle_rows = []

for i in range(
    len(category_names)
):

    category = category_names[i]

    count_column = count_columns[i]

    amount_column = amount_columns[i]

    total_count = data[count_column].sum()

    total_amount = data[amount_column].sum()

    average_count = data[count_column].mean()

    average_amount = data[amount_column].mean()

    if total_count > 0:
        revenue_per_vehicle = (
            total_amount /
            total_count
        )

    else:
        revenue_per_vehicle = 0

    vehicle_rows.append(
        [
            category,
            total_count,
            total_amount,
            average_count,
            average_amount,
            revenue_per_vehicle
        ]
    )


vehicle_summary = pd.DataFrame(
    vehicle_rows,
    columns=[
        "VEHICLE_CATEGORY",
        "TOTAL_TRAFFIC",
        "TOTAL_REVENUE",
        "AVERAGE_TRAFFIC",
        "AVERAGE_REVENUE",
        "REVENUE_PER_VEHICLE"
    ]
)


vehicle_summary.to_csv(
    EDA_DIR / "vehicle_category_summary.csv",
    index=False
)


# ============================================================
# 6. TOP 10 PLAZAS BY TRAFFIC
# ============================================================

top_traffic = (
    plaza_summary
    .sort_values(
        "TOTAL_TRAFFIC",
        ascending=False
    )
    .head(10)
)


top_traffic.to_csv(
    EDA_DIR / "top_10_traffic_plazas.csv",
    index=False
)


# ============================================================
# 7. TOP 10 PLAZAS BY REVENUE
# ============================================================

top_revenue = (
    plaza_summary
    .sort_values(
        "TOTAL_REVENUE",
        ascending=False
    )
    .head(10)
)


top_revenue.to_csv(
    EDA_DIR / "top_10_revenue_plazas.csv",
    index=False
)


# ============================================================
# 8. TRAFFIC AND REVENUE CORRELATION
# ============================================================

traffic_revenue_correlation = (
    data[
        [
            "TOTAL_CNT",
            "TOTAL_AMT"
        ]
    ]
    .corr(
        method="pearson"
    )
)


correlation_value = (
    traffic_revenue_correlation
    .loc[
        "TOTAL_CNT",
        "TOTAL_AMT"
    ]
)


correlation_summary = pd.DataFrame(
    {
        "VARIABLE_1": [
            "TOTAL_TRAFFIC"
        ],

        "VARIABLE_2": [
            "TOTAL_REVENUE"
        ],

        "PEARSON_CORRELATION": [
            correlation_value
        ]
    }
)


correlation_summary.to_csv(
    EDA_DIR / "traffic_revenue_correlation.csv",
    index=False
)


# ============================================================
# 9. VEHICLE CATEGORY CORRELATION
# ============================================================

category_correlation = data[
    count_columns + amount_columns
].corr(
    method="pearson"
)


category_correlation.to_csv(
    EDA_DIR / "vehicle_category_correlation.csv"
)


# ============================================================
# 10. YEAR-MONTH TREND DATA
# ============================================================

year_month_summary = (
    data
    .groupby(
        [
            "DATE",
            "YEAR",
            "MONTH",
            "MONTH_NUMBER"
        ]
    )
    .agg(
        TOTAL_TRAFFIC=("TOTAL_CNT", "sum"),
        TOTAL_REVENUE=("TOTAL_AMT", "sum"),
        AVERAGE_TRAFFIC=("TOTAL_CNT", "mean"),
        AVERAGE_REVENUE=("TOTAL_AMT", "mean"),
        TOLL_PLAZAS=("PLAZA_NAME", "nunique")
    )
    .reset_index()
    .sort_values("DATE")
)


year_month_summary.to_csv(
    EDA_DIR / "year_month_summary.csv",
    index=False
)


# ============================================================
# GRAPH 1 — YEARLY TRAFFIC
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.plot(
    year_summary["YEAR"],
    year_summary["TOTAL_TRAFFIC"],
    marker="o"
)

plt.title(
    "Year-wise Total Traffic"
)

plt.xlabel(
    "Year"
)

plt.ylabel(
    "Total Traffic"
)

plt.xticks(
    year_summary["YEAR"]
)

plt.grid(
    True,
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    EDA_DIR / "yearly_traffic.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 2 — YEARLY REVENUE
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.plot(
    year_summary["YEAR"],
    year_summary["TOTAL_REVENUE"],
    marker="o"
)

plt.title(
    "Year-wise Total Revenue"
)

plt.xlabel(
    "Year"
)

plt.ylabel(
    "Total Revenue"
)

plt.xticks(
    year_summary["YEAR"]
)

plt.grid(
    True,
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    EDA_DIR / "yearly_revenue.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 3 — MONTHLY TRAFFIC
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.plot(
    month_summary["MONTH_NUMBER"],
    month_summary["TOTAL_TRAFFIC"],
    marker="o"
)

plt.title(
    "Month-wise Total Traffic"
)

plt.xlabel(
    "Month"
)

plt.ylabel(
    "Total Traffic"
)

plt.xticks(
    month_summary["MONTH_NUMBER"],
    month_summary["MONTH"],
    rotation=45
)

plt.grid(
    True,
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    EDA_DIR / "monthly_traffic.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 4 — MONTHLY REVENUE
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.plot(
    month_summary["MONTH_NUMBER"],
    month_summary["TOTAL_REVENUE"],
    marker="o"
)

plt.title(
    "Month-wise Total Revenue"
)

plt.xlabel(
    "Month"
)

plt.ylabel(
    "Total Revenue"
)

plt.xticks(
    month_summary["MONTH_NUMBER"],
    month_summary["MONTH"],
    rotation=45
)

plt.grid(
    True,
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    EDA_DIR / "monthly_revenue.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 5 — VEHICLE CATEGORY TRAFFIC
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.bar(
    vehicle_summary["VEHICLE_CATEGORY"],
    vehicle_summary["TOTAL_TRAFFIC"]
)

plt.title(
    "Traffic by Vehicle Category"
)

plt.xlabel(
    "Vehicle Category"
)

plt.ylabel(
    "Total Traffic"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()

plt.savefig(
    EDA_DIR / "vehicle_category_traffic.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 6 — VEHICLE CATEGORY REVENUE
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.bar(
    vehicle_summary["VEHICLE_CATEGORY"],
    vehicle_summary["TOTAL_REVENUE"]
)

plt.title(
    "Revenue by Vehicle Category"
)

plt.xlabel(
    "Vehicle Category"
)

plt.ylabel(
    "Total Revenue"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()

plt.savefig(
    EDA_DIR / "vehicle_category_revenue.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 7 — TOP 10 TRAFFIC PLAZAS
# ============================================================

plt.figure(
    figsize=(12, 7)
)

plt.barh(
    top_traffic["PLAZA_NAME"],
    top_traffic["TOTAL_TRAFFIC"]
)

plt.title(
    "Top 10 Toll Plazas by Traffic"
)

plt.xlabel(
    "Total Traffic"
)

plt.ylabel(
    "Toll Plaza"
)

plt.gca().invert_yaxis()

plt.tight_layout()

plt.savefig(
    EDA_DIR / "top_10_traffic_plazas.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 8 — TOP 10 REVENUE PLAZAS
# ============================================================

plt.figure(
    figsize=(12, 7)
)

plt.barh(
    top_revenue["PLAZA_NAME"],
    top_revenue["TOTAL_REVENUE"]
)

plt.title(
    "Top 10 Toll Plazas by Revenue"
)

plt.xlabel(
    "Total Revenue"
)

plt.ylabel(
    "Toll Plaza"
)

plt.gca().invert_yaxis()

plt.tight_layout()

plt.savefig(
    EDA_DIR / "top_10_revenue_plazas.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 9 — TRAFFIC VS REVENUE
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.scatter(
    data["TOTAL_CNT"],
    data["TOTAL_AMT"],
    alpha=0.5
)

plt.title(
    "Traffic vs Revenue"
)

plt.xlabel(
    "Total Traffic"
)

plt.ylabel(
    "Total Revenue"
)

plt.grid(
    True,
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    EDA_DIR / "traffic_vs_revenue.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 10 — REVENUE PER VEHICLE BY CATEGORY
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.bar(
    vehicle_summary["VEHICLE_CATEGORY"],
    vehicle_summary["REVENUE_PER_VEHICLE"]
)

plt.title(
    "Revenue per Vehicle by Category"
)

plt.xlabel(
    "Vehicle Category"
)

plt.ylabel(
    "Revenue per Vehicle"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()

plt.savefig(
    EDA_DIR / "revenue_per_vehicle_category.png",
    dpi=300
)

plt.close()


# ============================================================
# PRINT RESULTS
# ============================================================

print()
print("=" * 70)
print("EDA SUMMARY")
print("=" * 70)

print()

print(
    "Total toll plazas:",
    data["PLAZA_NAME"].nunique()
)

print(
    "Total records:",
    len(data)
)

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
    "Date range:"
)

print(
    data["DATE"].min()
)

print(
    "to"
)

print(
    data["DATE"].max()
)

print()

print(
    "Pearson correlation between traffic and revenue:"
)

print(
    correlation_value
)

print()

print("=" * 70)
print("YEAR-WISE SUMMARY")
print("=" * 70)

print()

print(
    year_summary.to_string(
        index=False
    )
)

print()

print("=" * 70)
print("VEHICLE CATEGORY SUMMARY")
print("=" * 70)

print()

print(
    vehicle_summary.to_string(
        index=False
    )
)

print()

print("=" * 70)
print("TOP 10 TRAFFIC PLAZAS")
print("=" * 70)

print()

print(
    top_traffic[
        [
            "PLAZA_NAME",
            "TOTAL_TRAFFIC"
        ]
    ].to_string(
        index=False
    )
)

print()

print("=" * 70)
print("TOP 10 REVENUE PLAZAS")
print("=" * 70)

print()

print(
    top_revenue[
        [
            "PLAZA_NAME",
            "TOTAL_REVENUE"
        ]
    ].to_string(
        index=False
    )
)

print()

print("=" * 70)
print("EDA OUTPUT FILES")
print("=" * 70)

print()

print(
    "EDA folder:"
)

print(
    EDA_DIR
)

print()

print(
    "10 graphs created"
)

print(
    "Multiple numerical summary files created"
)

print()

print("=" * 70)
print("STEP 9 COMPLETED")
print("=" * 70)