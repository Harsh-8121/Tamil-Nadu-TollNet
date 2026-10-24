import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# TAMIL NADU TOLLNET
# STEP 12 - ML FEATURE ENGINEERING
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - ML FEATURE ENGINEERING")
print("=" * 70)


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
    "ml_dataset.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print()
print("Loading:")
print(INPUT_FILE)

data = pd.read_csv(INPUT_FILE)

print()
print("Original records:", len(data))
print("Toll plazas:", data["PLAZA_ID"].nunique())


# ============================================================
# BASIC CLEANING
# ============================================================

data["YEAR"] = pd.to_numeric(
    data["YEAR"],
    errors="coerce"
)

data["MONTH_NUMBER"] = pd.to_numeric(
    data["MONTH_NUMBER"],
    errors="coerce"
)

data = data.dropna(
    subset=[
        "PLAZA_ID",
        "YEAR",
        "MONTH_NUMBER"
    ]
).copy()

data["YEAR"] = data["YEAR"].astype(int)
data["MONTH_NUMBER"] = data["MONTH_NUMBER"].astype(int)


# ============================================================
# MONTH INDEX
# ============================================================

data["MONTH_INDEX"] = (
    data["YEAR"] * 12
    +
    data["MONTH_NUMBER"]
)


# ============================================================
# CLEAN TEXT COLUMNS
# ============================================================

text_columns = [
    "PLAZA_ID",
    "PLAZA_NAME",
    "PIU",
    "RO",
    "STATE"
]

for column in text_columns:

    if column in data.columns:

        data[column] = (
            data[column]
            .astype("string")
            .str.strip()
        )

        data[column] = data[column].replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "None": pd.NA
            }
        )


# ============================================================
# HELPER
# ============================================================

def first_non_null(series):

    valid_values = series.dropna()

    if len(valid_values) > 0:
        return valid_values.iloc[0]

    return np.nan


# ============================================================
# AGGREGATE PLAZA-MONTH RECORDS
# ============================================================

print()
print("=" * 70)
print("AGGREGATING PLAZA-MONTH RECORDS")
print("=" * 70)


duplicate_mask = data.duplicated(
    subset=[
        "PLAZA_ID",
        "MONTH_INDEX"
    ],
    keep=False
)

duplicate_rows = data[
    duplicate_mask
].copy()

duplicate_groups = (
    duplicate_rows[
        [
            "PLAZA_ID",
            "MONTH_INDEX"
        ]
    ]
    .drop_duplicates()
)


print()
print(
    "Rows involved in duplicate plaza-month groups:",
    len(duplicate_rows)
)

print(
    "Duplicate plaza-month groups:",
    len(duplicate_groups)
)


# ============================================================
# NUMERIC COLUMNS
# ============================================================

sum_columns = [

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
    "TOTAL_AMT"
]


for column in sum_columns:

    if column in data.columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

        data[column] = data[column].fillna(0)


# ============================================================
# AGGREGATION DICTIONARY
# ============================================================

aggregation = {}

for column in sum_columns:

    if column in data.columns:
        aggregation[column] = "sum"


for column in [
    "PLAZA_NAME",
    "PIU",
    "RO",
    "STATE"
]:

    if column in data.columns:
        aggregation[column] = first_non_null


# ============================================================
# AGGREGATE
# ============================================================

data = (
    data
    .groupby(
        [
            "PLAZA_ID",
            "YEAR",
            "MONTH_NUMBER",
            "MONTH_INDEX"
        ],
        as_index=False
    )
    .agg(aggregation)
)


# ============================================================
# MONTH NAME
# ============================================================

month_names = {

    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}


data["MONTH"] = data["MONTH_NUMBER"].map(
    month_names
)


# ============================================================
# DATE
# ============================================================

data["DATE"] = pd.to_datetime(
    {
        "year": data["YEAR"].astype(int),
        "month": data["MONTH_NUMBER"].astype(int),
        "day": 1
    }
)


# ============================================================
# CHECK DUPLICATES
# ============================================================

remaining_duplicates = data.duplicated(
    subset=[
        "PLAZA_ID",
        "MONTH_INDEX"
    ],
    keep=False
)

remaining_duplicate_count = (
    remaining_duplicates.sum()
)


print()

print(
    "Records after Plaza-Month aggregation:",
    len(data)
)

print(
    "Toll plazas after aggregation:",
    data["PLAZA_ID"].nunique()
)

print(
    "Remaining duplicate plaza-month rows:",
    remaining_duplicate_count
)


# ============================================================
# BASE DERIVED FEATURES
# ============================================================

data["REVENUE_PER_VEHICLE"] = np.nan

valid_traffic = (
    data["TOTAL_CNT"] > 0
)

data.loc[
    valid_traffic,
    "REVENUE_PER_VEHICLE"
] = (
    data.loc[
        valid_traffic,
        "TOTAL_AMT"
    ]
    /
    data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


# ============================================================
# VEHICLE PROPORTIONS
# ============================================================

proportion_columns = [

    "car_jeep_PROPORTION",
    "lcv_PROPORTION",
    "bus_truck_PROPORTION",
    "3_axle_PROPORTION",
    "4_6_axle_PROPORTION",
    "osv_PROPORTION"
]

for column in proportion_columns:
    data[column] = np.nan


data.loc[
    valid_traffic,
    "car_jeep_PROPORTION"
] = (
    data.loc[
        valid_traffic,
        "CAR_JEEP_CNT"
    ]
    /
    data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


data.loc[
    valid_traffic,
    "lcv_PROPORTION"
] = (
    data.loc[
        valid_traffic,
        "LCV_CNT"
    ]
    /
    data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


data.loc[
    valid_traffic,
    "bus_truck_PROPORTION"
] = (
    data.loc[
        valid_traffic,
        "BUS_TRUCK_CNT"
    ]
    /
    data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


data.loc[
    valid_traffic,
    "3_axle_PROPORTION"
] = (
    data.loc[
        valid_traffic,
        "3_AXLE_CNT"
    ]
    /
    data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


data.loc[
    valid_traffic,
    "4_6_axle_PROPORTION"
] = (
    data.loc[
        valid_traffic,
        "4_6_AXLE_CNT"
    ]
    /
    data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


data.loc[
    valid_traffic,
    "osv_PROPORTION"
] = (
    data.loc[
        valid_traffic,
        "OSV_CNT"
    ]
    /
    data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


# ============================================================
# SORT DATA
# ============================================================

data = data.sort_values(
    [
        "PLAZA_ID",
        "MONTH_INDEX"
    ]
).reset_index(drop=True)


# ============================================================
# CREATE CALENDAR-COMPLETE DATA
# ============================================================

print()
print("=" * 70)
print("CREATING CALENDAR-COMPLETE MONTHLY DATA")
print("=" * 70)


calendar_parts = []

plaza_ids = (
    data["PLAZA_ID"]
    .dropna()
    .unique()
)


for plaza_id in plaza_ids:

    plaza_data = (
        data[
            data["PLAZA_ID"] == plaza_id
        ]
        .sort_values("MONTH_INDEX")
        .copy()
    )

    first_month = int(
        plaza_data["MONTH_INDEX"].min()
    )

    last_month = int(
        plaza_data["MONTH_INDEX"].max()
    )

    complete_months = pd.Index(
        range(
            first_month,
            last_month + 1
        ),
        name="MONTH_INDEX"
    )

    plaza_indexed = (
        plaza_data
        .set_index("MONTH_INDEX")
        .sort_index()
    )

    expanded = (
        plaza_indexed
        .reindex(complete_months)
    )


    # --------------------------------------------------------
    # RESTORE PLAZA INFORMATION
    # --------------------------------------------------------

    expanded["PLAZA_ID"] = plaza_id

    plaza_name = first_non_null(
        plaza_data["PLAZA_NAME"]
    )

    piu = first_non_null(
        plaza_data["PIU"]
    )

    ro = first_non_null(
        plaza_data["RO"]
    )

    state = first_non_null(
        plaza_data["STATE"]
    )

    expanded["PLAZA_NAME"] = plaza_name
    expanded["PIU"] = piu
    expanded["RO"] = ro
    expanded["STATE"] = state


    # --------------------------------------------------------
    # RECONSTRUCT YEAR / MONTH
    # --------------------------------------------------------

    month_index_zero = (
        expanded.index.to_numpy()
        - 1
    )

    expanded["YEAR"] = (
        month_index_zero // 12
    )

    expanded["MONTH_NUMBER"] = (
        month_index_zero % 12
        + 1
    )

    expanded["MONTH"] = (
        expanded["MONTH_NUMBER"]
        .map(month_names)
    )


    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    expanded["DATE"] = pd.to_datetime(
        {
            "year":
                expanded["YEAR"].astype(int),

            "month":
                expanded["MONTH_NUMBER"].astype(int),

            "day": 1
        }
    )


    # --------------------------------------------------------
    # ORIGINAL RECORD FLAG
    # --------------------------------------------------------

    expanded["IS_ORIGINAL_RECORD"] = (
        expanded["TOTAL_CNT"]
        .notna()
        .astype(int)
    )


    calendar_parts.append(
        expanded.reset_index()
    )


# ============================================================
# COMBINE
# ============================================================

calendar_data = pd.concat(
    calendar_parts,
    ignore_index=True
)


calendar_data = calendar_data.sort_values(
    [
        "PLAZA_ID",
        "MONTH_INDEX"
    ]
).reset_index(
    drop=True
)


print()

print(
    "Calendar-complete records:",
    len(calendar_data)
)

print(
    "Toll plazas:",
    calendar_data["PLAZA_ID"].nunique()
)

print(
    "Inserted missing calendar months:",
    (
        len(calendar_data)
        -
        len(data)
    )
)


# ============================================================
# RECALCULATE DERIVED FEATURES
# AFTER CALENDAR EXPANSION
# ============================================================

calendar_data["REVENUE_PER_VEHICLE"] = np.nan

valid_traffic = (
    calendar_data["TOTAL_CNT"] > 0
)

calendar_data.loc[
    valid_traffic,
    "REVENUE_PER_VEHICLE"
] = (
    calendar_data.loc[
        valid_traffic,
        "TOTAL_AMT"
    ]
    /
    calendar_data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


# ============================================================
# VEHICLE PROPORTIONS
# ============================================================

for column in proportion_columns:
    calendar_data[column] = np.nan


calendar_data.loc[
    valid_traffic,
    "car_jeep_PROPORTION"
] = (
    calendar_data.loc[
        valid_traffic,
        "CAR_JEEP_CNT"
    ]
    /
    calendar_data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


calendar_data.loc[
    valid_traffic,
    "lcv_PROPORTION"
] = (
    calendar_data.loc[
        valid_traffic,
        "LCV_CNT"
    ]
    /
    calendar_data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


calendar_data.loc[
    valid_traffic,
    "bus_truck_PROPORTION"
] = (
    calendar_data.loc[
        valid_traffic,
        "BUS_TRUCK_CNT"
    ]
    /
    calendar_data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


calendar_data.loc[
    valid_traffic,
    "3_axle_PROPORTION"
] = (
    calendar_data.loc[
        valid_traffic,
        "3_AXLE_CNT"
    ]
    /
    calendar_data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


calendar_data.loc[
    valid_traffic,
    "4_6_axle_PROPORTION"
] = (
    calendar_data.loc[
        valid_traffic,
        "4_6_AXLE_CNT"
    ]
    /
    calendar_data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


calendar_data.loc[
    valid_traffic,
    "osv_PROPORTION"
] = (
    calendar_data.loc[
        valid_traffic,
        "OSV_CNT"
    ]
    /
    calendar_data.loc[
        valid_traffic,
        "TOTAL_CNT"
    ]
)


# ============================================================
# SEASONAL FEATURES
# ============================================================

calendar_data["MONTH_SIN"] = np.sin(
    2 * np.pi *
    calendar_data["MONTH_NUMBER"] / 12
)

calendar_data["MONTH_COS"] = np.cos(
    2 * np.pi *
    calendar_data["MONTH_NUMBER"] / 12
)


# ============================================================
# SORT BEFORE LAGS
# ============================================================

calendar_data = calendar_data.sort_values(
    [
        "PLAZA_ID",
        "MONTH_INDEX"
    ]
).reset_index(drop=True)


# ============================================================
# GROUP BY PLAZA
# ============================================================

grouped = (
    calendar_data
    .groupby("PLAZA_ID")
)


# ============================================================
# TRAFFIC LAGS
# ============================================================

calendar_data["TRAFFIC_LAG_1"] = (
    grouped["TOTAL_CNT"]
    .shift(1)
)

calendar_data["TRAFFIC_LAG_2"] = (
    grouped["TOTAL_CNT"]
    .shift(2)
)

calendar_data["TRAFFIC_LAG_3"] = (
    grouped["TOTAL_CNT"]
    .shift(3)
)


# ============================================================
# REVENUE LAGS
# ============================================================

calendar_data["REVENUE_LAG_1"] = (
    grouped["TOTAL_AMT"]
    .shift(1)
)

calendar_data["REVENUE_LAG_2"] = (
    grouped["TOTAL_AMT"]
    .shift(2)
)

calendar_data["REVENUE_LAG_3"] = (
    grouped["TOTAL_AMT"]
    .shift(3)
)


# ============================================================
# REVENUE PER VEHICLE LAGS
# ============================================================

calendar_data["REVENUE_PER_VEHICLE_LAG_1"] = (
    grouped["REVENUE_PER_VEHICLE"]
    .shift(1)
)

calendar_data["REVENUE_PER_VEHICLE_LAG_2"] = (
    grouped["REVENUE_PER_VEHICLE"]
    .shift(2)
)


# ============================================================
# VEHICLE PROPORTION LAGS
# ============================================================

calendar_data["car_jeep_PROPORTION_LAG_1"] = (
    grouped["car_jeep_PROPORTION"]
    .shift(1)
)

calendar_data["lcv_PROPORTION_LAG_1"] = (
    grouped["lcv_PROPORTION"]
    .shift(1)
)

calendar_data["bus_truck_PROPORTION_LAG_1"] = (
    grouped["bus_truck_PROPORTION"]
    .shift(1)
)

calendar_data["3_axle_PROPORTION_LAG_1"] = (
    grouped["3_axle_PROPORTION"]
    .shift(1)
)

calendar_data["4_6_axle_PROPORTION_LAG_1"] = (
    grouped["4_6_axle_PROPORTION"]
    .shift(1)
)

calendar_data["osv_PROPORTION_LAG_1"] = (
    grouped["osv_PROPORTION"]
    .shift(1)
)


# ============================================================
# ROLLING FEATURES
# ============================================================

print()
print("=" * 70)
print("CREATING ROLLING FEATURES")
print("=" * 70)


calendar_data["TRAFFIC_ROLLING_3"] = (

    calendar_data
    .groupby("PLAZA_ID")["TOTAL_CNT"]
    .transform(
        lambda x:
            x.shift(1)
            .rolling(
                window=3,
                min_periods=3
            )
            .mean()
    )
)


calendar_data["REVENUE_ROLLING_3"] = (

    calendar_data
    .groupby("PLAZA_ID")["TOTAL_AMT"]
    .transform(
        lambda x:
            x.shift(1)
            .rolling(
                window=3,
                min_periods=3
            )
            .mean()
    )
)


# ============================================================
# NEXT-MONTH TARGETS
# ============================================================

print()
print("=" * 70)
print("CREATING NEXT-MONTH TARGETS")
print("=" * 70)


calendar_data["NEXT_MONTH_TRAFFIC"] = (
    calendar_data
    .groupby("PLAZA_ID")["TOTAL_CNT"]
    .shift(-1)
)


calendar_data["NEXT_MONTH_REVENUE"] = (
    calendar_data
    .groupby("PLAZA_ID")["TOTAL_AMT"]
    .shift(-1)
)


# ============================================================
# KEEP ONLY ORIGINAL SOURCE MONTHS
# ============================================================

ml_data = calendar_data[
    calendar_data["IS_ORIGINAL_RECORD"] == 1
].copy()


print()

print(
    "Original monthly records available for ML:",
    len(ml_data)
)


# ============================================================
# REQUIRED HISTORY
# ============================================================

required_history_columns = [

    "TRAFFIC_LAG_1",
    "TRAFFIC_LAG_2",
    "TRAFFIC_LAG_3",

    "REVENUE_LAG_1",
    "REVENUE_LAG_2",
    "REVENUE_LAG_3"
]


required_target_columns = [

    "NEXT_MONTH_TRAFFIC",
    "NEXT_MONTH_REVENUE"
]


before_history_filter = len(ml_data)


ml_data = ml_data.dropna(
    subset=required_history_columns
)


after_history_filter = len(ml_data)


print(
    "Rows removed due to incomplete 3-month history:",
    (
        before_history_filter
        -
        after_history_filter
    )
)


before_target_filter = len(ml_data)


ml_data = ml_data.dropna(
    subset=required_target_columns
)


after_target_filter = len(ml_data)


print(
    "Rows removed due to missing next-month target:",
    (
        before_target_filter
        -
        after_target_filter
    )
)


# ============================================================
# FINAL SORT
# ============================================================

ml_data = ml_data.sort_values(
    [
        "PLAZA_ID",
        "MONTH_INDEX"
    ]
).reset_index(
    drop=True
)


# ============================================================
# CLEAN INFINITE VALUES
# ============================================================

ml_data = ml_data.replace(
    [
        np.inf,
        -np.inf
    ],
    np.nan
)


# ============================================================
# CORRECT ML FEATURE SET
# ============================================================

feature_columns = [

    "YEAR",

    "MONTH_NUMBER",

    "MONTH_SIN",

    "MONTH_COS",

    "TRAFFIC_LAG_1",

    "TRAFFIC_LAG_2",

    "TRAFFIC_LAG_3",

    "REVENUE_LAG_1",

    "REVENUE_LAG_2",

    "REVENUE_LAG_3",

    "REVENUE_PER_VEHICLE_LAG_1",

    "REVENUE_PER_VEHICLE_LAG_2",

    "car_jeep_PROPORTION_LAG_1",

    "lcv_PROPORTION_LAG_1",

    "bus_truck_PROPORTION_LAG_1",

    "3_axle_PROPORTION_LAG_1",

    "4_6_axle_PROPORTION_LAG_1",

    "osv_PROPORTION_LAG_1",

    "TRAFFIC_ROLLING_3",

    "REVENUE_ROLLING_3"
]


# ============================================================
# CHECK FEATURES
# ============================================================

missing_features = []

for column in feature_columns:

    if column not in ml_data.columns:

        missing_features.append(column)


if len(missing_features) > 0:

    print()

    print(
        "ERROR: Missing feature columns:"
    )

    for column in missing_features:

        print(
            " -",
            column
        )

    raise ValueError(
        "Required ML feature columns are missing."
    )


print()
print("=" * 70)
print("CORRECT ML FEATURE SET")
print("=" * 70)

print()

print(
    "Number of features:",
    len(feature_columns)
)

print()

for column in feature_columns:
    print(" -", column)


# ============================================================
# DROP ROWS WITH MISSING ML FEATURES
# ============================================================

before_feature_filter = len(ml_data)


ml_data = ml_data.dropna(
    subset=feature_columns
)


after_feature_filter = len(ml_data)


print()

print(
    "Rows removed due to missing ML features:",
    (
        before_feature_filter
        -
        after_feature_filter
    )
)


# ============================================================
# FINAL TARGET CHECK
# ============================================================

ml_data = ml_data.dropna(
    subset=[
        "NEXT_MONTH_TRAFFIC",
        "NEXT_MONTH_REVENUE"
    ]
)


# ============================================================
# RESET INDEX
# ============================================================

ml_data = ml_data.reset_index(
    drop=True
)


# ============================================================
# SAVE FINAL ML DATASET
# ============================================================

ml_data.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("FINAL ML DATASET SUMMARY")
print("=" * 70)

print()

print(
    "Final ML records:",
    len(ml_data)
)

print(
    "Toll plazas represented:",
    ml_data["PLAZA_ID"].nunique()
)

print(
    "Number of ML features:",
    len(feature_columns)
)

print(
    "Target 1: NEXT_MONTH_TRAFFIC"
)

print(
    "Target 2: NEXT_MONTH_REVENUE"
)

print()

print(
    "Date range in ML dataset:"
)

if len(ml_data) > 0:

    print(
        ml_data["DATE"].min(),
        "to",
        ml_data["DATE"].max()
    )

print()

print(
    "Output saved at:"
)

print(
    OUTPUT_FILE
)


# ============================================================
# ML ELIGIBILITY BY PLAZA
# ============================================================

print()
print("=" * 70)
print("ML ELIGIBILITY BY PLAZA")
print("=" * 70)


plaza_counts = (

    ml_data
    .groupby("PLAZA_ID")
    .size()
    .reset_index(
        name="ML_RECORDS"
    )
)


print()

print(
    "Plazas with ML records:",
    len(plaza_counts)
)


# ============================================================
# FINAL COMPLETION
# ============================================================

print()
print("=" * 70)
print("STEP 12 COMPLETED SUCCESSFULLY")
print("=" * 70)



