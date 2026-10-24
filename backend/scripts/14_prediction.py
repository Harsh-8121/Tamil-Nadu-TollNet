import os
import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from difflib import SequenceMatcher

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ============================================================
# TAMIL NADU TOLLNET
# STEP 14 - PREDICTION API
# ============================================================

print("=" * 70)
print("TAMIL NADU TOLLNET - PREDICTION API")
print("=" * 70)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

ANALYSIS_FILE = (
    PROCESSED_DIR
    / "tamil_nadu_analysis_data.csv"
)

ML_DATASET_FILE = (
    PROCESSED_DIR
    / "ml_dataset.csv"
)

ELIGIBILITY_FILE = (
    PROCESSED_DIR
    / "ml_plaza_eligibility.csv"
)

MODEL_DIR = (
    PROCESSED_DIR
    / "models"
)

RESULT_DIR = (
    PROCESSED_DIR
    / "prediction"
)

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

BEST_MODELS_FILE = (
    PROCESSED_DIR
    / "model_results"
    / "best_models.csv"
)

PREPROCESSOR_FILE = (
    MODEL_DIR
    / "preprocessor.pkl"
)

TRAFFIC_MODEL_FILE = (
    MODEL_DIR
    / "best_traffic_model.pkl"
)

REVENUE_MODEL_FILE = (
    MODEL_DIR
    / "best_revenue_model.pkl"
)


# ============================================================
# EXACT FEATURES USED BY STEP 13
# ============================================================

FEATURE_COLUMNS = [

    "PLAZA_ID",

    "RO",

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


print()
print(
    "Expected Step 13 features:",
    len(FEATURE_COLUMNS)
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Tamil Nadu TollNet",
    description=(
        "Tamil Nadu toll traffic, revenue "
        "comparison and prediction API."
    ),
    version="2.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# LOAD ANALYSIS DATA
# ============================================================

print()
print("Loading analysis data:")
print(ANALYSIS_FILE)

if not ANALYSIS_FILE.exists():
    raise FileNotFoundError(
        "tamil_nadu_analysis_data.csv not found."
    )

data = pd.read_csv(
    ANALYSIS_FILE
)

print(
    "Analysis records loaded:",
    len(data)
)


# ============================================================
# LOAD ML DATASET
# ============================================================

print()
print("Loading ML dataset:")
print(ML_DATASET_FILE)

if not ML_DATASET_FILE.exists():
    raise FileNotFoundError(
        "ml_dataset.csv not found."
    )

ml_dataset = pd.read_csv(
    ML_DATASET_FILE
)

print(
    "ML records loaded:",
    len(ml_dataset)
)


# ============================================================
# LOAD ELIGIBILITY
# ============================================================

print()
print("Loading ML eligibility:")
print(ELIGIBILITY_FILE)

if not ELIGIBILITY_FILE.exists():
    raise FileNotFoundError(
        "ml_plaza_eligibility.csv not found."
    )

eligibility = pd.read_csv(
    ELIGIBILITY_FILE
)

eligible_ids = (
    eligibility[
        eligibility["ML_ELIGIBLE"] == True
    ]["PLAZA_ID"]
    .astype(str)
    .tolist()
)

print(
    "Prediction eligible plazas:",
    len(eligible_ids)
)


# ============================================================
# BASIC CLEANING
# ============================================================

data["PLAZA_ID"] = (
    data["PLAZA_ID"]
    .astype(str)
    .str.strip()
)

if "PLAZA_NAME" in data.columns:

    data["PLAZA_NAME"] = (
        data["PLAZA_NAME"]
        .astype(str)
        .str.strip()
    )

if "RO" in data.columns:

    data["RO"] = (
        data["RO"]
        .astype(str)
        .str.strip()
        .replace(
            ["nan", "None", ""],
            "Unknown"
        )
    )

else:

    data["RO"] = "Unknown"


# ============================================================
# NUMERIC COLUMNS
# ============================================================

numeric_columns = [

    "YEAR",
    "MONTH_NUMBER",

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


for column in numeric_columns:

    if column in data.columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        ).fillna(0)


# ============================================================
# YEAR / MONTH
# ============================================================

data["YEAR"] = (
    data["YEAR"]
    .astype(int)
)

data["MONTH_NUMBER"] = (
    data["MONTH_NUMBER"]
    .astype(int)
)


# ============================================================
# AGGREGATE SAME PLAZA + MONTH
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


def first_non_null(series):

    values = series.dropna()

    if len(values) > 0:

        return values.iloc[0]

    return "Unknown"


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


data = (
    data
    .groupby(
        [
            "PLAZA_ID",
            "YEAR",
            "MONTH_NUMBER"
        ],
        as_index=False
    )
    .agg(aggregation)
)


# ============================================================
# DATE
# ============================================================

data["DATE"] = pd.to_datetime(
    {
        "year":
            data["YEAR"].astype(int),

        "month":
            data["MONTH_NUMBER"].astype(int),

        "day":
            1
    }
)


data = (
    data
    .sort_values(
        [
            "PLAZA_ID",
            "DATE"
        ]
    )
    .reset_index(drop=True)
)


# ============================================================
# KEEP ONLY ELIGIBLE PLAZAS FOR PREDICTION
# ============================================================

prediction_base = data[
    data["PLAZA_ID"]
    .isin(eligible_ids)
].copy()


# ============================================================
# COMPLETE MONTHLY CALENDAR
#
# Missing months become zero-valued months.
# ============================================================

print()
print("Building complete prediction calendar...")

calendar_parts = []


for plaza_id in eligible_ids:

    plaza_data = (
        prediction_base[
            prediction_base["PLAZA_ID"]
            == plaza_id
        ]
        .sort_values("DATE")
        .copy()
    )

    if len(plaza_data) == 0:
        continue

    start_date = plaza_data["DATE"].min()
    end_date = plaza_data["DATE"].max()

    all_dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="MS"
    )

    calendar = pd.DataFrame(
        {
            "DATE": all_dates
        }
    )

    calendar["PLAZA_ID"] = plaza_id

    existing = plaza_data.copy()

    merged = calendar.merge(
        existing,
        on=[
            "PLAZA_ID",
            "DATE"
        ],
        how="left",
        suffixes=(
            "",
            "_OLD"
        )
    )


    # --------------------------------------------------------
    # Restore plaza metadata
    # --------------------------------------------------------

    plaza_name = "Unknown"
    ro = "Unknown"
    piu = "Unknown"
    state = "Tamil Nadu"

    if "PLAZA_NAME" in plaza_data.columns:

        values = plaza_data[
            "PLAZA_NAME"
        ].dropna()

        if len(values) > 0:

            plaza_name = str(
                values.iloc[0]
            )

    if "RO" in plaza_data.columns:

        values = plaza_data[
            "RO"
        ].dropna()

        if len(values) > 0:

            ro = str(
                values.iloc[0]
            )

    if "PIU" in plaza_data.columns:

        values = plaza_data[
            "PIU"
        ].dropna()

        if len(values) > 0:

            piu = str(
                values.iloc[0]
            )

    if "STATE" in plaza_data.columns:

        values = plaza_data[
            "STATE"
        ].dropna()

        if len(values) > 0:

            state = str(
                values.iloc[0]
            )


    merged["PLAZA_NAME"] = (
        merged["PLAZA_NAME"]
        .fillna(plaza_name)
    )

    merged["RO"] = (
        merged["RO"]
        .fillna(ro)
    )

    merged["PIU"] = (
        merged["PIU"]
        .fillna(piu)
    )

    merged["STATE"] = (
        merged["STATE"]
        .fillna(state)
    )


    # --------------------------------------------------------
    # Numeric missing months = zero
    # --------------------------------------------------------

    for column in sum_columns:

        if column in merged.columns:

            merged[column] = (
                pd.to_numeric(
                    merged[column],
                    errors="coerce"
                )
                .fillna(0)
            )


    merged["YEAR"] = (
        merged["DATE"]
        .dt.year
        .astype(int)
    )

    merged["MONTH_NUMBER"] = (
        merged["DATE"]
        .dt.month
        .astype(int)
    )


    calendar_parts.append(
        merged
    )


if len(calendar_parts) == 0:

    raise RuntimeError(
        "No prediction data available."
    )


calendar_data = pd.concat(
    calendar_parts,
    ignore_index=True
)

calendar_data = (
    calendar_data
    .sort_values(
        [
            "PLAZA_ID",
            "DATE"
        ]
    )
    .reset_index(drop=True)
)


print(
    "Calendar records:",
    len(calendar_data)
)


# ============================================================
# STEP 13 FEATURE ENGINEERING
#
# These calculations match the features used during training.
# ============================================================


# ============================================================
# MONTH SIN / COS
# ============================================================

calendar_data["MONTH_SIN"] = (
    np.sin(
        2
        * np.pi
        * calendar_data["MONTH_NUMBER"]
        / 12
    )
)

calendar_data["MONTH_COS"] = (
    np.cos(
        2
        * np.pi
        * calendar_data["MONTH_NUMBER"]
        / 12
    )
)


# ============================================================
# REVENUE PER VEHICLE
# ============================================================

calendar_data["REVENUE_PER_VEHICLE"] = np.where(

    calendar_data["TOTAL_CNT"] > 0,

    calendar_data["TOTAL_AMT"]
    /
    calendar_data["TOTAL_CNT"],

    0

)


# ============================================================
# VEHICLE PROPORTIONS
# ============================================================

calendar_data["car_jeep_PROPORTION"] = np.where(

    calendar_data["TOTAL_CNT"] > 0,

    calendar_data["CAR_JEEP_CNT"]
    /
    calendar_data["TOTAL_CNT"],

    0

)

calendar_data["lcv_PROPORTION"] = np.where(

    calendar_data["TOTAL_CNT"] > 0,

    calendar_data["LCV_CNT"]
    /
    calendar_data["TOTAL_CNT"],

    0

)

calendar_data["bus_truck_PROPORTION"] = np.where(

    calendar_data["TOTAL_CNT"] > 0,

    calendar_data["BUS_TRUCK_CNT"]
    /
    calendar_data["TOTAL_CNT"],

    0

)

calendar_data["3_axle_PROPORTION"] = np.where(

    calendar_data["TOTAL_CNT"] > 0,

    calendar_data["3_AXLE_CNT"]
    /
    calendar_data["TOTAL_CNT"],

    0

)

calendar_data["4_6_axle_PROPORTION"] = np.where(

    calendar_data["TOTAL_CNT"] > 0,

    calendar_data["4_6_AXLE_CNT"]
    /
    calendar_data["TOTAL_CNT"],

    0

)

calendar_data["osv_PROPORTION"] = np.where(

    calendar_data["TOTAL_CNT"] > 0,

    calendar_data["OSV_CNT"]
    /
    calendar_data["TOTAL_CNT"],

    0

)


# ============================================================
# GROUP BY PLAZA
# ============================================================

grouped = calendar_data.groupby(
    "PLAZA_ID"
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
# ROLLING TRAFFIC
# ============================================================

calendar_data["TRAFFIC_ROLLING_3"] = (

    calendar_data
    .groupby("PLAZA_ID")["TOTAL_CNT"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            3,
            min_periods=3
        )
        .mean()
    )

)


# ============================================================
# ROLLING REVENUE
# ============================================================

calendar_data["REVENUE_ROLLING_3"] = (

    calendar_data
    .groupby("PLAZA_ID")["TOTAL_AMT"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            3,
            min_periods=3
        )
        .mean()
    )

)


# ============================================================
# LOAD TRAINED MODELS
# ============================================================

print()
print("Loading trained models...")


if not PREPROCESSOR_FILE.exists():

    raise FileNotFoundError(
        "preprocessor.pkl not found."
    )


if not TRAFFIC_MODEL_FILE.exists():

    raise FileNotFoundError(
        "best_traffic_model.pkl not found."
    )


if not REVENUE_MODEL_FILE.exists():

    raise FileNotFoundError(
        "best_revenue_model.pkl not found."
    )


preprocessor = joblib.load(
    PREPROCESSOR_FILE
)

traffic_model = joblib.load(
    TRAFFIC_MODEL_FILE
)

revenue_model = joblib.load(
    REVENUE_MODEL_FILE
)


print(
    "Models loaded successfully."
)


# ============================================================
# LOAD BEST MODEL RESULTS
# ============================================================

if BEST_MODELS_FILE.exists():

    best_models = pd.read_csv(
        BEST_MODELS_FILE
    )

    print(
        "Best model results loaded."
    )

else:

    best_models = pd.DataFrame()


# ============================================================
# MODEL NAMES
# ============================================================

TRAFFIC_MODEL_NAME = "LightGBM"

REVENUE_MODEL_NAME = "XGBoost"


# ============================================================
# PLAZA MASTER
# ============================================================

plaza_list = (

    calendar_data[
        [
            "PLAZA_ID",
            "PLAZA_NAME"
        ]
    ]

    .drop_duplicates()

    .sort_values(
        "PLAZA_NAME"
    )

    .reset_index(
        drop=True
    )

)


print(
    "Plaza master:",
    len(plaza_list)
)


# ============================================================
# SEARCH HELPERS
# ============================================================

def normalize_search_text(text):

    return (
        str(text)
        .strip()
        .lower()
    )


def search_score(
    query,
    plaza_id,
    plaza_name
):

    query = normalize_search_text(
        query
    )

    plaza_id = normalize_search_text(
        plaza_id
    )

    plaza_name = normalize_search_text(
        plaza_name
    )


    if query == plaza_id:

        return 1000


    if query == plaza_name:

        return 1000


    if query in plaza_id:

        return 900


    if query in plaza_name:

        return 850


    id_ratio = SequenceMatcher(
        None,
        query,
        plaza_id
    ).ratio()


    name_ratio = SequenceMatcher(
        None,
        query,
        plaza_name
    ).ratio()


    ratio = max(
        id_ratio,
        name_ratio
    )


    if ratio >= 0.45:

        return ratio * 100


    return -1

# ============================================================
# BUILD EXACT STEP 13 FEATURE ROW
# ============================================================

def build_feature_row(row):

    feature_row = {}

    for column in FEATURE_COLUMNS:

        if column not in row:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Prediction feature missing: "
                    + column
                )
            )

        feature_row[column] = row[column]

    return feature_row


# ============================================================
# PREDICT FROM FEATURE ROW
# ============================================================

def predict_from_features(
    feature_row,
    target
):

    feature_df = pd.DataFrame(
        [feature_row],
        columns=FEATURE_COLUMNS
    )


    # --------------------------------------------------------
    # Categorical columns
    # --------------------------------------------------------

    feature_df["PLAZA_ID"] = (
        feature_df["PLAZA_ID"]
        .astype(str)
    )

    feature_df["RO"] = (
        feature_df["RO"]
        .astype(str)
    )


    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    numeric_features = [

        column

        for column in FEATURE_COLUMNS

        if column
        not in [
            "PLAZA_ID",
            "RO"
        ]

    ]


    for column in numeric_features:

        feature_df[column] = pd.to_numeric(
            feature_df[column],
            errors="coerce"
        )


    if feature_df[numeric_features].isna().any().any():

        bad_columns = (

            feature_df[
                numeric_features
            ]

            .columns[

                feature_df[
                    numeric_features
                ]

                .isna()
                .any()

            ]

            .tolist()

        )


        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction feature values "
                "contain invalid numbers: "
                + str(bad_columns)
            )
        )


    # --------------------------------------------------------
    # IMPORTANT:
    #
    # The preprocessor receives exactly the
    # same feature columns used during Step 13.
    # --------------------------------------------------------

    transformed = preprocessor.transform(
        feature_df
    )


    # --------------------------------------------------------
    # Select target model
    # --------------------------------------------------------

    if target == "traffic":

        prediction = traffic_model.predict(
            transformed
        )[0]

    else:

        prediction = revenue_model.predict(
            transformed
        )[0]


    prediction = float(
        max(
            0,
            prediction
        )
    )


    return prediction


# ============================================================
# CREATE FUTURE ROW
# ============================================================

def create_future_row(
    current_row,
    next_date,
    predicted_traffic,
    predicted_revenue
):

    future = {}


    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    future["PLAZA_ID"] = str(
        current_row["PLAZA_ID"]
    )

    future["PLAZA_NAME"] = str(
        current_row["PLAZA_NAME"]
    )

    future["RO"] = str(
        current_row["RO"]
    )

    future["PIU"] = str(
        current_row.get(
            "PIU",
            "Unknown"
        )
    )

    future["STATE"] = str(
        current_row.get(
            "STATE",
            "Tamil Nadu"
        )
    )


    future["DATE"] = next_date

    future["YEAR"] = (
        next_date.year
    )

    future["MONTH_NUMBER"] = (
        next_date.month
    )


    # --------------------------------------------------------
    # Month encoding
    # --------------------------------------------------------

    future["MONTH_SIN"] = np.sin(
        2
        * np.pi
        * future["MONTH_NUMBER"]
        / 12
    )

    future["MONTH_COS"] = np.cos(
        2
        * np.pi
        * future["MONTH_NUMBER"]
        / 12
    )


    # --------------------------------------------------------
    # Predicted actual values
    #
    # These become the current values for
    # the next recursive prediction.
    # --------------------------------------------------------

    future["TOTAL_CNT"] = float(
        predicted_traffic
    )

    future["TOTAL_AMT"] = float(
        predicted_revenue
    )


    # --------------------------------------------------------
    # Revenue per vehicle
    # --------------------------------------------------------

    if predicted_traffic > 0:

        future["REVENUE_PER_VEHICLE"] = (

            predicted_revenue
            /
            predicted_traffic

        )

    else:

        future["REVENUE_PER_VEHICLE"] = 0


    # --------------------------------------------------------
    # Keep vehicle proportions from previous month
    #
    # Future category counts are not separately predicted.
    # Therefore the latest observed composition is carried
    # forward.
    # --------------------------------------------------------

    proportion_columns = [

        "car_jeep_PROPORTION",

        "lcv_PROPORTION",

        "bus_truck_PROPORTION",

        "3_axle_PROPORTION",

        "4_6_axle_PROPORTION",

        "osv_PROPORTION"

    ]


    for column in proportion_columns:

        future[column] = float(
            current_row[column]
        )


    # --------------------------------------------------------
    # Approximate future category counts
    # --------------------------------------------------------

    future["CAR_JEEP_CNT"] = (

        predicted_traffic
        *
        future[
            "car_jeep_PROPORTION"
        ]

    )

    future["LCV_CNT"] = (

        predicted_traffic
        *
        future[
            "lcv_PROPORTION"
        ]

    )

    future["BUS_TRUCK_CNT"] = (

        predicted_traffic
        *
        future[
            "bus_truck_PROPORTION"
        ]

    )

    future["3_AXLE_CNT"] = (

        predicted_traffic
        *
        future[
            "3_axle_PROPORTION"
        ]

    )

    future["4_6_AXLE_CNT"] = (

        predicted_traffic
        *
        future[
            "4_6_axle_PROPORTION"
        ]

    )

    future["OSV_CNT"] = (

        predicted_traffic
        *
        future[
            "osv_PROPORTION"
        ]

    )


    # --------------------------------------------------------
    # Amounts
    #
    # Keep the previous month's revenue composition.
    # --------------------------------------------------------

    amount_pairs = [

        (
            "CAR_JEEP_CNT",
            "CAR_JEEP_AMT"
        ),

        (
            "LCV_CNT",
            "LCV_AMT"
        ),

        (
            "BUS_TRUCK_CNT",
            "BUS_TRUCK_AMT"
        ),

        (
            "3_AXLE_CNT",
            "3_AXLE_AMT"
        ),

        (
            "4_6_AXLE_CNT",
            "4_6_AXLE_AMT"
        ),

        (
            "OSV_CNT",
            "OSV_AMT"
        )

    ]


    previous_total_amt = float(
        current_row["TOTAL_AMT"]
    )


    if previous_total_amt > 0:

        for count_column, amount_column in amount_pairs:

            previous_amount = float(
                current_row[amount_column]
            )

            share = (
                previous_amount
                /
                previous_total_amt
            )

            future[amount_column] = (

                predicted_revenue
                *
                share

            )

    else:

        for count_column, amount_column in amount_pairs:

            future[amount_column] = (

                predicted_revenue
                *
                future[
                    count_column
                ]
                /
                max(
                    predicted_traffic,
                    1
                )

            )


    # --------------------------------------------------------
    # TRAFFIC LAGS
    # --------------------------------------------------------

    future["TRAFFIC_LAG_1"] = float(
        current_row["TOTAL_CNT"]
    )

    future["TRAFFIC_LAG_2"] = float(
        current_row["TRAFFIC_LAG_1"]
    )

    future["TRAFFIC_LAG_3"] = float(
        current_row["TRAFFIC_LAG_2"]
    )


    # --------------------------------------------------------
    # REVENUE LAGS
    # --------------------------------------------------------

    future["REVENUE_LAG_1"] = float(
        current_row["TOTAL_AMT"]
    )

    future["REVENUE_LAG_2"] = float(
        current_row["REVENUE_LAG_1"]
    )

    future["REVENUE_LAG_3"] = float(
        current_row["REVENUE_LAG_2"]
    )


    # --------------------------------------------------------
    # REVENUE PER VEHICLE LAGS
    # --------------------------------------------------------

    future[
        "REVENUE_PER_VEHICLE_LAG_1"
    ] = float(

        current_row[
            "REVENUE_PER_VEHICLE"
        ]

    )

    future[
        "REVENUE_PER_VEHICLE_LAG_2"
    ] = float(

        current_row[
            "REVENUE_PER_VEHICLE_LAG_1"
        ]

    )


    # --------------------------------------------------------
    # PROPORTION LAGS
    # --------------------------------------------------------

    future[
        "car_jeep_PROPORTION_LAG_1"
    ] = float(

        current_row[
            "car_jeep_PROPORTION"
        ]

    )

    future[
        "lcv_PROPORTION_LAG_1"
    ] = float(

        current_row[
            "lcv_PROPORTION"
        ]

    )

    future[
        "bus_truck_PROPORTION_LAG_1"
    ] = float(

        current_row[
            "bus_truck_PROPORTION"
        ]

    )

    future[
        "3_axle_PROPORTION_LAG_1"
    ] = float(

        current_row[
            "3_axle_PROPORTION"
        ]

    )

    future[
        "4_6_axle_PROPORTION_LAG_1"
    ] = float(

        current_row[
            "4_6_axle_PROPORTION"
        ]

    )

    future[
        "osv_PROPORTION_LAG_1"
    ] = float(

        current_row[
            "osv_PROPORTION"
        ]

    )


    # --------------------------------------------------------
    # ROLLING FEATURES
    #
    # Step 13 uses the previous 3 months:
    #
    # current value
    # lag 1
    # lag 2
    #
    # after shifting one month before rolling.
    # --------------------------------------------------------

    traffic_values = [

        float(
            current_row[
                "TOTAL_CNT"
            ]
        ),

        float(
            current_row[
                "TRAFFIC_LAG_1"
            ]
        ),

        float(
            current_row[
                "TRAFFIC_LAG_2"
            ]
        )

    ]


    revenue_values = [

        float(
            current_row[
                "TOTAL_AMT"
            ]
        ),

        float(
            current_row[
                "REVENUE_LAG_1"
            ]
        ),

        float(
            current_row[
                "REVENUE_LAG_2"
            ]
        )

    ]


    future[
        "TRAFFIC_ROLLING_3"
    ] = np.mean(
        traffic_values
    )

    future[
        "REVENUE_ROLLING_3"
    ] = np.mean(
        revenue_values
    )


    return future


# ============================================================
# RECURSIVE FORECAST
# ============================================================

def recursive_forecast(
    plaza_id,
    requested_date
):

    plaza_history = (

        calendar_data[
            calendar_data["PLAZA_ID"]
            == plaza_id
        ]

        .sort_values(
            "DATE"
        )

        .reset_index(
            drop=True
        )

    )


    if len(plaza_history) < 4:

        raise HTTPException(
            status_code=400,
            detail=(
                "Not enough historical data "
                "for this toll plaza."
            )
        )


    latest_row = (
        plaza_history
        .iloc[-1]
        .copy()
    )


    latest_date = pd.Timestamp(
        latest_row["DATE"]
    )


    if requested_date <= latest_date:

        raise HTTPException(
            status_code=400,
            detail=(
                "Forecast month must be after "
                + latest_date.strftime(
                    "%B %Y"
                )
                + "."
            )
        )


    current_row = latest_row

    current_date = latest_date


    current_value_traffic = float(
        latest_row["TOTAL_CNT"]
    )

    current_value_revenue = float(
        latest_row["TOTAL_AMT"]
    )


    forecast_path = []


    # ========================================================
    # FORECAST MONTH BY MONTH
    # ========================================================

    while current_date < requested_date:

        next_date = (
            current_date
            + pd.DateOffset(
                months=1
            )
        )


        # ----------------------------------------------------
        # Build current 22-feature row
        # ----------------------------------------------------

        feature_row = build_feature_row(
            current_row
        )


        # ----------------------------------------------------
        # Predict traffic
        # ----------------------------------------------------

        predicted_traffic = (
            predict_from_features(
                feature_row,
                "traffic"
            )
        )


        # ----------------------------------------------------
        # Predict revenue
        # ----------------------------------------------------

        predicted_revenue = (
            predict_from_features(
                feature_row,
                "revenue"
            )
        )


        # ----------------------------------------------------
        # Store forecast month
        # ----------------------------------------------------

        forecast_path.append(
            {
                "month":
                    next_date.strftime(
                        "%Y-%m"
                    ),

                "traffic":
                    float(
                        predicted_traffic
                    ),

                "revenue":
                    float(
                        predicted_revenue
                    )
            }
        )


        # ----------------------------------------------------
        # Create next recursive row
        # ----------------------------------------------------

        future_row = create_future_row(

            current_row,

            next_date,

            predicted_traffic,

            predicted_revenue

        )


        current_row = future_row

        current_date = next_date


    final_prediction = None


    if len(forecast_path) > 0:

        final_item = (
            forecast_path[-1]
        )

        final_prediction = (
            final_item
        )


    if final_prediction is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to generate forecast."
            )
        )


    return (
        latest_row,
        latest_date,
        final_prediction,
        forecast_path
    )


# ============================================================
# REQUEST MODEL
# ============================================================

class PredictionRequest(BaseModel):

    plaza_id: str

    target: str

    forecast_month: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def home():

    return {

        "project":
            "Tamil Nadu TollNet",

        "status":
            "running",

        "version":
            "2.0.0",

        "endpoints": [

            "/health",

            "/plazas",

            "/plazas/search",

            "/comparison",

            "/predict"

        ]

    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {

        "status":
            "healthy",

        "models_loaded":
            True,

        "prediction_eligible_plazas":
            len(eligible_ids),

        "traffic_model":
            TRAFFIC_MODEL_NAME,

        "revenue_model":
            REVENUE_MODEL_NAME,

        "step13_features":
            len(FEATURE_COLUMNS)

    }


# ============================================================
# ALL PLAZAS
# ============================================================

@app.get("/plazas")
def get_all_plazas():

    return {

        "count":
            len(plaza_list),

        "results":
            plaza_list.to_dict(
                orient="records"
            )

    }


# ============================================================
# SEARCH PLAZAS
# ============================================================

@app.get("/plazas/search")
def search_plazas(
    q: str = "",
    limit: int = 20
):

    query = normalize_search_text(
        q
    )


    if query == "":

        results = (
            plaza_list
            .head(limit)
            .copy()
        )

        return {

            "query":
                q,

            "count":
                len(results),

            "results":
                results.to_dict(
                    orient="records"
                )

        }


    matches = []


    for i in range(
        len(plaza_list)
    ):

        row = plaza_list.iloc[i]


        score = search_score(

            query,

            row["PLAZA_ID"],

            row["PLAZA_NAME"]

        )


        if score >= 0:

            matches.append(
                {

                    "PLAZA_ID":
                        row["PLAZA_ID"],

                    "PLAZA_NAME":
                        row["PLAZA_NAME"],

                    "score":
                        score

                }
            )


    if len(matches) == 0:

        return {

            "query":
                q,

            "count":
                0,

            "results":
                []

        }


    results = pd.DataFrame(
        matches
    )


    results = (

        results

        .sort_values(

            [
                "score",
                "PLAZA_NAME"
            ],

            ascending=[
                False,
                True
            ]

        )

        .head(
            max(
                limit,
                1
            )
        )

        .drop(
            columns=[
                "score"
            ]
        )

        .reset_index(
            drop=True
        )

    )


    return {

        "query":
            q,

        "count":
            len(results),

        "results":
            results.to_dict(
                orient="records"
            )

    }


# ============================================================
# PREDICTION
# ============================================================

@app.post("/predict")
def predict(
    request: PredictionRequest
):

    plaza_id = str(
        request.plaza_id
    ).strip()


    target = str(
        request.target
    ).strip().lower()


    forecast_month_text = str(
        request.forecast_month
    ).strip()


    # ========================================================
    # TARGET VALIDATION
    # ========================================================

    if target not in [
        "traffic",
        "revenue"
    ]:

        raise HTTPException(
            status_code=400,
            detail=(
                "Target must be "
                "'traffic' or 'revenue'."
            )
        )


    # ========================================================
    # PLAZA VALIDATION
    # ========================================================

    if plaza_id not in eligible_ids:

        raise HTTPException(
            status_code=400,
            detail=(
                "Selected toll plaza is "
                "not eligible for ML prediction."
            )
        )


    # ========================================================
    # FORECAST MONTH
    # ========================================================

    try:

        requested_date = pd.to_datetime(
            forecast_month_text
            + "-01"
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail=(
                "Forecast month must use "
                "YYYY-MM format."
            )
        )


    # ========================================================
    # RECURSIVE FORECAST
    # ========================================================

    try:

        (
            latest_row,
            latest_date,
            final_prediction,
            forecast_path

        ) = recursive_forecast(

            plaza_id,

            requested_date

        )


    except HTTPException:

        raise


    except Exception as error:

        print()
        print(
            "PREDICTION ERROR:"
        )

        print(
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction failed: "
                + str(error)
            )
        )


    # ========================================================
    # CURRENT VALUE
    # ========================================================

    if target == "traffic":

        current_value = float(
            latest_row[
                "TOTAL_CNT"
            ]
        )

        final_value = float(
            final_prediction[
                "traffic"
            ]
        )

        model_name = (
            TRAFFIC_MODEL_NAME
        )

        result_label = (
            "Traffic Forecast"
        )

    else:

        current_value = float(
            latest_row[
                "TOTAL_AMT"
            ]
        )

        final_value = float(
            final_prediction[
                "revenue"
            ]
        )

        model_name = (
            REVENUE_MODEL_NAME
        )

        result_label = (
            "Revenue Forecast"
        )


    # ========================================================
    # EXPECTED CHANGE
    # ========================================================

    if current_value != 0:

        expected_change = (

            (

                final_value
                -
                current_value

            )
            /
            current_value

        ) * 100

    else:

        expected_change = None


    # ========================================================
    # FORMAT FORECAST PATH
    # ========================================================

    formatted_path = []


    for item in forecast_path:

        formatted_path.append(

            {

                "month":
                    item["month"],

                "traffic":
                    round(
                        float(
                            item["traffic"]
                        ),
                        2
                    ),

                "revenue":
                    round(
                        float(
                            item["revenue"]
                        ),
                        2
                    )

            }

        )


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {

        "plaza_id":
            str(
                latest_row[
                    "PLAZA_ID"
                ]
            ),

        "plaza_name":
            str(
                latest_row[
                    "PLAZA_NAME"
                ]
            ),

        "latest_actual_month":
            latest_date.strftime(
                "%Y-%m-%d"
            ),

        "predicted_month":
            requested_date.strftime(
                "%Y-%m-%d"
            ),

        "target":
            result_label,

        "model":
            model_name,

        "current_value":
            round(
                current_value,
                2
            ),

        "prediction":
            round(
                final_value,
                2
            ),

        "expected_change_percent":

            (
                round(
                    float(
                        expected_change
                    ),
                    2
                )

                if expected_change is not None

                else None
            ),

        "forecast_path":
            formatted_path

    }



# ============================================================
# ANALYSIS API
# ============================================================

@app.get("/analysis")
def analyze_data(
    plaza_ids: str = "ALL",
    year: str = "ALL",
    month: str = "ALL",
    categories: str = "ALL"
):
    df = data.copy()

    # --------------------------------------------------------
    # FILTER BY TOLL PLAZA
    # --------------------------------------------------------
    selected_plazas = [
        item.strip()
        for item in plaza_ids.split(",")
        if item.strip()
    ]

    if selected_plazas and "ALL" not in [
        item.upper() for item in selected_plazas
    ]:
        df = df[df["PLAZA_ID"].isin(selected_plazas)].copy()

    # --------------------------------------------------------
    # FILTER BY YEAR
    # --------------------------------------------------------
    if str(year).upper() != "ALL":
        try:
            selected_year = int(year)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Year must be a valid year or ALL."
            )

        df = df[df["YEAR"] == selected_year].copy()

    # --------------------------------------------------------
    # FILTER BY MONTH
    # --------------------------------------------------------
    if str(month).upper() != "ALL":
        try:
            selected_month = int(month)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Month must be between 1 and 12, or ALL."
            )

        if selected_month < 1 or selected_month > 12:
            raise HTTPException(
                status_code=400,
                detail="Month must be between 1 and 12."
            )

        df = df[df["MONTH_NUMBER"] == selected_month].copy()

    # --------------------------------------------------------
    # VEHICLE CATEGORY COLUMNS
    # --------------------------------------------------------
    category_columns = {
        "CAR_JEEP": ("CAR_JEEP_CNT", "CAR_JEEP_AMT"),
        "LCV": ("LCV_CNT", "LCV_AMT"),
        "BUS_TRUCK": ("BUS_TRUCK_CNT", "BUS_TRUCK_AMT"),
        "3_AXLE": ("3_AXLE_CNT", "3_AXLE_AMT"),
        "4_6_AXLE": ("4_6_AXLE_CNT", "4_6_AXLE_AMT"),
        "OSV": ("OSV_CNT", "OSV_AMT")
    }

    selected_categories = [
        item.strip().upper()
        for item in categories.split(",")
        if item.strip()
    ]

    if not selected_categories or "ALL" in selected_categories:
        selected_categories = ["ALL"]
        traffic_column = "TOTAL_CNT"
        revenue_column = "TOTAL_AMT"
    else:
        invalid_categories = [
            item for item in selected_categories
            if item not in category_columns
        ]

        if invalid_categories:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid vehicle category.",
                    "valid_categories": list(category_columns.keys())
                    + ["ALL"]
                }
            )

        traffic_columns = [
            category_columns[item][0]
            for item in selected_categories
        ]

        revenue_columns = [
            category_columns[item][1]
            for item in selected_categories
        ]

        traffic_column = "ANALYSIS_TRAFFIC"
        revenue_column = "ANALYSIS_REVENUE"

        df[traffic_column] = df[traffic_columns].sum(axis=1)
        df[revenue_column] = df[revenue_columns].sum(axis=1)

    # --------------------------------------------------------
    # CHECK FILTERED DATA
    # --------------------------------------------------------
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="No records found for the selected filters."
        )

    df[traffic_column] = pd.to_numeric(
        df[traffic_column], errors="coerce"
    ).fillna(0)

    df[revenue_column] = pd.to_numeric(
        df[revenue_column], errors="coerce"
    ).fillna(0)

    traffic = df[traffic_column]
    revenue = df[revenue_column]

    # --------------------------------------------------------
    # KPI VALUES
    # --------------------------------------------------------
    total_traffic = float(traffic.sum())
    total_revenue = float(revenue.sum())

    average_traffic = float(traffic.mean())
    average_revenue = float(revenue.mean())

    median_traffic = float(traffic.median())
    median_revenue = float(revenue.median())

    # Revenue per vehicle for the selected records
    revenue_per_vehicle = (
        total_revenue / total_traffic
        if total_traffic > 0 else 0
    )

    correlation = None

    if len(df) >= 2 and traffic.std() > 0 and revenue.std() > 0:
        correlation = float(traffic.corr(revenue))

    # --------------------------------------------------------
    # STATISTICAL SUMMARY
    # --------------------------------------------------------
    statistics = {
        "traffic": {
            "mean": average_traffic,
            "median": median_traffic,
            "minimum": float(traffic.min()),
            "maximum": float(traffic.max()),
            "standard_deviation": float(traffic.std(ddof=1))
            if len(df) > 1 else 0,
            "variance": float(traffic.var(ddof=1))
            if len(df) > 1 else 0
        },
        "revenue": {
            "mean": average_revenue,
            "median": median_revenue,
            "minimum": float(revenue.min()),
            "maximum": float(revenue.max()),
            "standard_deviation": float(revenue.std(ddof=1))
            if len(df) > 1 else 0,
            "variance": float(revenue.var(ddof=1))
            if len(df) > 1 else 0
        }
    }

    # --------------------------------------------------------
    # PLAZA SUMMARY
    # --------------------------------------------------------
    plaza_summary = (
        df.groupby(
            ["PLAZA_ID", "PLAZA_NAME"],
            as_index=False
        )
        .agg(
            traffic=(traffic_column, "sum"),
            revenue=(revenue_column, "sum")
        )
        .sort_values("traffic", ascending=False)
    )

    # --------------------------------------------------------
    # MONTHLY SUMMARY
    # --------------------------------------------------------
    monthly = (
        df.groupby(
            ["YEAR", "MONTH_NUMBER"],
            as_index=False
        )
        .agg(
            traffic=(traffic_column, "sum"),
            revenue=(revenue_column, "sum")
        )
        .sort_values(["YEAR", "MONTH_NUMBER"])
    )

    monthly["month"] = (
        monthly["YEAR"].astype(str)
        + "-"
        + monthly["MONTH_NUMBER"].astype(str).str.zfill(2)
    )

    # --------------------------------------------------------
    # YEARLY SUMMARY
    # --------------------------------------------------------
    yearly = (
        df.groupby("YEAR", as_index=False)
        .agg(
            traffic=(traffic_column, "sum"),
            revenue=(revenue_column, "sum")
        )
        .sort_values("YEAR")
    )

    # --------------------------------------------------------
    # VEHICLE COMPOSITION
    # Composition is based on the selected records.
    # --------------------------------------------------------


    # --------------------------------------------------------
    # VEHICLE COMPOSITION
    # --------------------------------------------------------

    composition = []

    for category_name, (count_col, amount_col) in category_columns.items():

        if selected_categories != ["ALL"]:
            if category_name not in selected_categories:
                continue

        if count_col in df.columns and amount_col in df.columns:
            composition.append({
                "category": category_name,
                "traffic": float(df[count_col].sum()),
                "revenue": float(df[amount_col].sum())
            })



    # --------------------------------------------------------
    # FILTERED RECORDS
    # --------------------------------------------------------
    records = df.copy()

    records["ANALYSIS_TRAFFIC"] = traffic
    records["ANALYSIS_REVENUE"] = revenue

    # Convert NumPy/Pandas missing values to JSON-safe values.
    records = records.astype(object).where(
        pd.notna(records), None
    )

    def clean_records(frame):
        frame = frame.astype(object).where(pd.notna(frame), None)
        return frame.to_dict(orient="records")

    return {
        "filters": {
            "plaza_ids": selected_plazas,
            "year": year,
            "month": month,
            "categories": selected_categories
        },
        "record_count": int(len(df)),
        "kpis": {
            "total_traffic": total_traffic,
            "total_revenue": total_revenue,
            "average_traffic": average_traffic,
            "average_revenue": average_revenue,
            "median_traffic": median_traffic,
            "median_revenue": median_revenue,
            "revenue_per_vehicle": revenue_per_vehicle,
            "traffic_revenue_correlation": correlation
        },
        "statistics": statistics,
        "plaza_summary": clean_records(plaza_summary),
        "monthly": clean_records(monthly),
        "yearly": clean_records(yearly),
        "composition": composition,
        "records": clean_records(records)
    }



# ============================================================
# COMPARISON API
# ============================================================

@app.get("/comparison")
def comparison(

    plaza_ids: str,

    category: str = "ALL",

    period: str = "all"

):

    selected_ids = [

        item.strip()

        for item in plaza_ids.split(",")

        if item.strip()

    ]


    if len(selected_ids) == 0:

        raise HTTPException(
            status_code=400,
            detail=(
                "At least one toll plaza "
                "must be selected."
            )
        )


    df = data.copy()


    df["PLAZA_ID"] = (

        df["PLAZA_ID"]

        .astype(str)

        .str.strip()

    )


    # ========================================================
    # PLAZA FILTER
    # ========================================================

    df = df[

        df["PLAZA_ID"]

        .isin(selected_ids)

    ].copy()


    if len(df) == 0:

        raise HTTPException(
            status_code=404,
            detail=(
                "No data found for "
                "selected toll plazas."
            )
        )


    # ========================================================
    # PERIOD FILTER
    # ========================================================

    if str(period).lower() != "all":

        try:

            selected_year = int(
                period
            )

        except Exception:

            raise HTTPException(
                status_code=400,
                detail="Invalid period."
            )


        df = df[

            df["YEAR"]

            ==

            selected_year

        ].copy()


        if len(df) == 0:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No data found for "
                    "selected period."
                )
            )


    # ========================================================
    # CATEGORY
    # ========================================================

    category = str(
        category
    ).upper()


    category_columns = {

        "CAR_JEEP":
            (
                "CAR_JEEP_CNT",
                "CAR_JEEP_AMT"
            ),

        "LCV":
            (
                "LCV_CNT",
                "LCV_AMT"
            ),

        "BUS_TRUCK":
            (
                "BUS_TRUCK_CNT",
                "BUS_TRUCK_AMT"
            ),

        "3_AXLE":
            (
                "3_AXLE_CNT",
                "3_AXLE_AMT"
            ),

        "4_6_AXLE":
            (
                "4_6_AXLE_CNT",
                "4_6_AXLE_AMT"
            ),

        "OSV":
            (
                "OSV_CNT",
                "OSV_AMT"
            )

    }


    if category in category_columns:

        count_column = (
            category_columns[
                category
            ][0]
        )

        amount_column = (
            category_columns[
                category
            ][1]
        )

    else:

        count_column = "TOTAL_CNT"

        amount_column = "TOTAL_AMT"


    # ========================================================
    # SUMMARY BY PLAZA
    # ========================================================

    summary = (

        df

        .groupby(

            [
                "PLAZA_ID",
                "PLAZA_NAME"
            ],

            as_index=False

        )

        .agg(

            traffic=(
                count_column,
                "sum"
            ),

            revenue=(
                amount_column,
                "sum"
            )

        )

    )


    # ========================================================
    # MONTHLY DATA
    # ========================================================

    monthly = (

        df

        .groupby(

            [
                "YEAR",
                "MONTH_NUMBER",
                "PLAZA_ID",
                "PLAZA_NAME"
            ],

            as_index=False

        )

        .agg(

            traffic=(
                count_column,
                "sum"
            ),

            revenue=(
                amount_column,
                "sum"
            )

        )

    )


    monthly["MONTH"] = (

        monthly["YEAR"].astype(str)

        + "-"

        + monthly["MONTH_NUMBER"]
        .astype(str)
        .str.zfill(2)

    )


    # ========================================================
    # VEHICLE COMPOSITION
    # ========================================================

    composition = []


    composition_columns = [

        (
            "CAR_JEEP",
            "CAR_JEEP_CNT"
        ),

        (
            "LCV",
            "LCV_CNT"
        ),

        (
            "BUS_TRUCK",
            "BUS_TRUCK_CNT"
        ),

        (
            "3_AXLE",
            "3_AXLE_CNT"
        ),

        (
            "4_6_AXLE",
            "4_6_AXLE_CNT"
        ),

        (
            "OSV",
            "OSV_CNT"
        )

    ]


    for plaza_id in selected_ids:

        plaza_df = df[
            df["PLAZA_ID"]
            == plaza_id
        ]


        if len(plaza_df) == 0:
            continue


        plaza_name = str(
            plaza_df[
                "PLAZA_NAME"
            ].iloc[0]
        )


        total_traffic = float(
            plaza_df[
                "TOTAL_CNT"
            ].sum()
        )


        for category_name, column in composition_columns:

            category_traffic = float(
                plaza_df[
                    column
                ].sum()
            )


            share = 0

            if total_traffic > 0:

                share = (
                    category_traffic
                    /
                    total_traffic
                ) * 100


            composition.append(

                {

                    "plaza_id":
                        plaza_id,

                    "plaza_name":
                        plaza_name,

                    "category":
                        category_name,

                    "traffic":
                        round(
                            category_traffic,
                            2
                        ),

                    "share":
                        round(
                            share,
                            2
                        )

                }

            )


    # ========================================================
    # TRAFFIC / REVENUE CORRELATION
    # ========================================================

    correlation = None


    if len(df) >= 2:

        try:

            correlation = float(

                df[
                    [
                        "TOTAL_CNT",
                        "TOTAL_AMT"
                    ]
                ]

                .corr()

                .iloc[0, 1]

            )

        except Exception:

            correlation = None


    # ========================================================
    # HIGHEST TRAFFIC
    # ========================================================

    highest_traffic = None


    if len(summary) > 0:

        row = summary.loc[
            summary["traffic"].idxmax()
        ]


        highest_traffic = {

            "plaza_id":
                str(
                    row["PLAZA_ID"]
                ),

            "plaza_name":
                str(
                    row["PLAZA_NAME"]
                ),

            "traffic":
                float(
                    row["traffic"]
                )

        }


    # ========================================================
    # HIGHEST REVENUE
    # ========================================================

    highest_revenue = None


    if len(summary) > 0:

        row = summary.loc[
            summary["revenue"].idxmax()
        ]


        highest_revenue = {

            "plaza_id":
                str(
                    row["PLAZA_ID"]
                ),

            "plaza_name":
                str(
                    row["PLAZA_NAME"]
                ),

            "revenue":
                float(
                    row["revenue"]
                )

        }


    # ========================================================
    # GROWTH CALCULATION
    # ========================================================

    traffic_growth = None

    revenue_growth = None


    sorted_monthly = (

        monthly

        .sort_values(
            [
                "YEAR",
                "MONTH_NUMBER"
            ]
        )

    )


    if len(sorted_monthly) >= 2:

        first_traffic = float(
            sorted_monthly[
                "traffic"
            ].iloc[0]
        )

        last_traffic = float(
            sorted_monthly[
                "traffic"
            ].iloc[-1]
        )


        first_revenue = float(
            sorted_monthly[
                "revenue"
            ].iloc[0]
        )

        last_revenue = float(
            sorted_monthly[
                "revenue"
            ].iloc[-1]
        )


        if first_traffic != 0:

            traffic_growth = (

                (
                    last_traffic
                    -
                    first_traffic
                )
                /
                first_traffic

            ) * 100


        if first_revenue != 0:

            revenue_growth = (

                (
                    last_revenue
                    -
                    first_revenue
                )
                /
                first_revenue

            ) * 100


    # ========================================================
    # PLAZA GROWTH / TREND DATA
    # ========================================================

    trend = []


    for plaza_id in selected_ids:

        plaza_monthly = (

            monthly[
                monthly["PLAZA_ID"]
                == plaza_id
            ]

            .sort_values(
                [
                    "YEAR",
                    "MONTH_NUMBER"
                ]
            )

        )


        if len(plaza_monthly) == 0:
            continue


        plaza_name = str(
            plaza_monthly[
                "PLAZA_NAME"
            ].iloc[0]
        )


        first_traffic = float(
            plaza_monthly[
                "traffic"
            ].iloc[0]
        )

        last_traffic = float(
            plaza_monthly[
                "traffic"
            ].iloc[-1]
        )


        first_revenue = float(
            plaza_monthly[
                "revenue"
            ].iloc[0]
        )

        last_revenue = float(
            plaza_monthly[
                "revenue"
            ].iloc[-1]
        )


        if first_traffic != 0:

            plaza_traffic_growth = (

                (
                    last_traffic
                    -
                    first_traffic
                )
                /
                first_traffic

            ) * 100

        else:

            plaza_traffic_growth = None


        if first_revenue != 0:

            plaza_revenue_growth = (

                (
                    last_revenue
                    -
                    first_revenue
                )
                /
                first_revenue

            ) * 100

        else:

            plaza_revenue_growth = None


        trend.append(

            {

                "plaza_id":
                    plaza_id,

                "plaza_name":
                    plaza_name,

                "traffic_growth_percent":
                    (
                        round(
                            plaza_traffic_growth,
                            2
                        )

                        if plaza_traffic_growth
                        is not None

                        else None
                    ),

                "revenue_growth_percent":
                    (
                        round(
                            plaza_revenue_growth,
                            2
                        )

                        if plaza_revenue_growth
                        is not None

                        else None
                    )

            }

        )


    # ========================================================
    # FINAL COMPARISON RESPONSE
    # ========================================================

    return {

        "selected_plazas":
            selected_ids,

        "category":
            category,

        "period":
            period,

        "summary":
            summary.to_dict(
                orient="records"
            ),

        "monthly":
            monthly.to_dict(
                orient="records"
            ),

        "composition":
            composition,

        "correlation":
            correlation,

        "highest_traffic":
            highest_traffic,

        "highest_revenue":
            highest_revenue,

        "traffic_growth_percent":
            (
                round(
                    traffic_growth,
                    2
                )

                if traffic_growth
                is not None

                else None
            ),

        "revenue_growth_percent":
            (
                round(
                    revenue_growth,
                    2
                )

                if revenue_growth
                is not None

                else None
            ),

        "trend":
            trend

    }


# ============================================================
# STARTUP MESSAGE
# ============================================================

print()
print("=" * 70)
print("TAMIL NADU TOLLNET API READY")
print("=" * 70)
print()
print("Available endpoints:")
print("  GET  /")
print("  GET  /health")
print("  GET  /plazas")
print("  GET  /plazas/search")
print("  GET  /comparison")
print("  POST /predict")
print()
print("Swagger UI:")
print("  http://127.0.0.1:8000/docs")
print("=" * 70)


if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )