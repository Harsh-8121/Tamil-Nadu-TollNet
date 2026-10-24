# ============================================================
# TAMIL NADU TOLLNET
# STEP 13 - ML MODEL TRAINING
# ============================================================

import pandas as pd
import numpy as np
import joblib
import time

from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor


print("=" * 70)
print("TAMIL NADU TOLLNET - ML MODEL TRAINING")
print("=" * 70)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "ml_dataset.csv"

MODEL_DIR = PROCESSED_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

RESULT_DIR = PROCESSED_DIR / "model_results"
RESULT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print()
print("Loading:")
print(INPUT_FILE)

data = pd.read_csv(INPUT_FILE)

print()
print("Dataset loaded successfully.")
print("Rows:", len(data))


# ============================================================
# DATE
# ============================================================

data["DATE"] = pd.to_datetime(
    data["DATE"],
    errors="coerce"
)

# Step 12 creates NEXT_MONTH_TRAFFIC and
# NEXT_MONTH_REVENUE, but does not create NEXT_MONTH_DATE.

data["NEXT_MONTH_DATE"] = (
    data["DATE"] + pd.DateOffset(months=1)
)


# ============================================================
# BASIC INFORMATION
# ============================================================

print()
print("Total ML records:", len(data))
print("Toll plazas:", data["PLAZA_ID"].nunique())
print()

# ============================================================
# CORRECT FEATURE SET
# ============================================================

# 22 total features
# 2 categorical
# 20 numeric

NUMERIC_FEATURE_COLUMNS = [

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


CATEGORICAL_FEATURE_COLUMNS = [

    "PLAZA_ID",

    "RO"
]


FEATURE_COLUMNS = (
    CATEGORICAL_FEATURE_COLUMNS
    +
    NUMERIC_FEATURE_COLUMNS
)


# ============================================================
# TARGETS
# ============================================================

TARGETS = [

    "NEXT_MONTH_TRAFFIC",

    "NEXT_MONTH_REVENUE"
]


# ============================================================
# PRINT FEATURE INFORMATION
# ============================================================

print("=" * 70)
print("MODEL FEATURES")
print("=" * 70)

print()

print("Original input features:", len(FEATURE_COLUMNS))
print("Numeric features:", len(NUMERIC_FEATURE_COLUMNS))
print("Categorical features:", len(CATEGORICAL_FEATURE_COLUMNS))

print()

for feature in FEATURE_COLUMNS:
    print(" -", feature)

print()

# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

print("=" * 70)
print("CHECKING REQUIRED COLUMNS")
print("=" * 70)

print()

missing_columns = []

for column in FEATURE_COLUMNS + TARGETS:

    if column not in data.columns:
        missing_columns.append(column)


if len(missing_columns) > 0:

    print("ERROR: Missing columns:")
    print()

    for column in missing_columns:
        print(" -", column)

    raise SystemExit(
        "Required columns are missing from ml_dataset.csv"
    )


print("All required columns found.")
print()


# ============================================================
# REMOVE INVALID DATES
# ============================================================

before_date_filter = len(data)

data = data.dropna(
    subset=[
        "DATE",
        "NEXT_MONTH_DATE"
    ]
).copy()

after_date_filter = len(data)

print(
    "Rows removed due to invalid dates:",
    before_date_filter - after_date_filter
)

print()


# ============================================================
# CLEAN CATEGORICAL FEATURES
# ============================================================

for column in CATEGORICAL_FEATURE_COLUMNS:

    data[column] = (
        data[column]
        .astype("string")
        .fillna("Unknown")
    )


# ============================================================
# TIME-BASED TRAIN / TEST SPLIT
# ============================================================

# Training:
# Target months before 2026
#
# Testing:
# Target months during 2026
#
# This prevents 2026 target information from entering
# the training data.

train_data = data[
    data["NEXT_MONTH_DATE"].dt.year < 2026
].copy()


test_data = data[
    data["NEXT_MONTH_DATE"].dt.year == 2026
].copy()


print("=" * 70)
print("TIME-BASED DATA SPLIT")
print("=" * 70)

print()

print(
    "Training rows:",
    len(train_data)
)

print(
    "Testing rows:",
    len(test_data)
)

print()

print("Training target period:")

print(
    train_data["NEXT_MONTH_DATE"].min()
)

print("to")

print(
    train_data["NEXT_MONTH_DATE"].max()
)

print()

print("Testing target period:")

print(
    test_data["NEXT_MONTH_DATE"].min()
)

print("to")

print(
    test_data["NEXT_MONTH_DATE"].max()
)

print()


# ============================================================
# CHECK SPLIT
# ============================================================

if len(train_data) == 0:

    raise SystemExit(
        "Training dataset is empty."
    )


if len(test_data) == 0:

    raise SystemExit(
        "Testing dataset is empty."
    )


# ============================================================
# CREATE X DATA
# ============================================================

X_train = train_data[
    FEATURE_COLUMNS
].copy()


X_test = test_data[
    FEATURE_COLUMNS
].copy()

# ============================================================
# CREATE PREPROCESSOR
# ============================================================

preprocessor = ColumnTransformer(

    transformers=[

        (
            "categorical",

            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),

            CATEGORICAL_FEATURE_COLUMNS
        ),

        (
            "numeric",

            "passthrough",

            NUMERIC_FEATURE_COLUMNS
        )
    ]
)


# ============================================================
# ENCODE FEATURES
# ============================================================

print("=" * 70)
print("ENCODING FEATURES")
print("=" * 70)

print()


X_train_encoded = preprocessor.fit_transform(
    X_train
)


X_test_encoded = preprocessor.transform(
    X_test
)


print(
    "Original input features:",
    len(FEATURE_COLUMNS)
)

print(
    "Numeric features:",
    len(NUMERIC_FEATURE_COLUMNS)
)

print(
    "Categorical features:",
    len(CATEGORICAL_FEATURE_COLUMNS)
)

print(
    "Encoded training shape:",
    X_train_encoded.shape
)

print(
    "Encoded testing shape:",
    X_test_encoded.shape
)

print()


# ============================================================
# MODEL DEFINITIONS
# ============================================================

def create_models():

    models = {

        "XGBoost": XGBRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1
        ),

        "LightGBM": LGBMRegressor(
            n_estimators=300,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbosity=-1,
            n_jobs=-1
        ),

        "Random Forest": RandomForestRegressor(
            n_estimators=300,
            random_state=42,
            n_jobs=-1
        )
    }

    return models


# ============================================================
# RESULT STORAGE
# ============================================================

all_results = []

all_predictions = []


# ============================================================
# TRAIN EACH TARGET
# ============================================================

for target in TARGETS:

    print()
    print("=" * 70)
    print("TARGET:", target)
    print("=" * 70)
    print()

    y_train = train_data[target].values

    y_test = test_data[target].values


    # Create fresh models for each target

    models = create_models()


    # ========================================================
    # TRAIN EACH MODEL
    # ========================================================

    for model_name, model in models.items():

        print()
        print("Training:", model_name)

        start_time = time.time()


        # ----------------------------------------------------
        # TRAIN
        # ----------------------------------------------------

        model.fit(
            X_train_encoded,
            y_train
        )


        training_time = (
            time.time() - start_time
        )


        # ----------------------------------------------------
        # PREDICT
        # ----------------------------------------------------

        predictions = model.predict(
            X_test_encoded
        )


        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        mae = mean_absolute_error(
            y_test,
            predictions
        )


        rmse = np.sqrt(
            mean_squared_error(
                y_test,
                predictions
            )
        )


        r2 = r2_score(
            y_test,
            predictions
        )


        # ----------------------------------------------------
        # SAVE RESULT
        # ----------------------------------------------------

        all_results.append(
            [
                target,
                model_name,
                training_time,
                mae,
                rmse,
                r2
            ]
        )


        # ----------------------------------------------------
        # SAVE PREDICTIONS
        # ----------------------------------------------------

        prediction_frame = test_data[
            [
                "PLAZA_ID",
                "PLAZA_NAME",
                "RO",
                "DATE",
                "NEXT_MONTH_DATE"
            ]
        ].copy()


        prediction_frame["TARGET"] = target

        prediction_frame["ACTUAL"] = y_test

        prediction_frame["PREDICTED"] = predictions

        prediction_frame["MODEL"] = model_name


        all_predictions.append(
            prediction_frame
        )


        # ----------------------------------------------------
        # PRINT METRICS
        # ----------------------------------------------------

        print(
            "Training Time:",
            round(training_time, 2),
            "seconds"
        )

        print(
            "MAE:",
            round(mae, 2)
        )

        print(
            "RMSE:",
            round(rmse, 2)
        )

        print(
            "R2:",
            round(r2, 4)
        )


# ============================================================
# CREATE RESULTS DATAFRAME
# ============================================================

results = pd.DataFrame(

    all_results,

    columns=[

        "TARGET",

        "MODEL",

        "TRAINING_TIME_SECONDS",

        "MAE",

        "RMSE",

        "R2"
    ]
)


# ============================================================
# SAVE MODEL COMPARISON
# ============================================================

results_file = (
    RESULT_DIR /
    "model_comparison.csv"
)


results.to_csv(
    results_file,
    index=False
)


# ============================================================
# COMBINE ALL PREDICTIONS
# ============================================================

predictions_data = pd.concat(
    all_predictions,
    ignore_index=True
)


predictions_file = (
    RESULT_DIR /
    "all_model_predictions.csv"
)


predictions_data.to_csv(
    predictions_file,
    index=False
)


# ============================================================
# FIND BEST MODEL
# ============================================================

# Primary metric:
# Lowest RMSE
#
# Secondary metric:
# Lowest MAE

best_models = []


for target in TARGETS:

    target_results = results[
        results["TARGET"] == target
    ].copy()


    target_results = target_results.sort_values(

        by=[
            "RMSE",
            "MAE"
        ],

        ascending=[
            True,
            True
        ]
    )


    best_row = target_results.iloc[0]


    best_models.append(
        [
            target,
            best_row["MODEL"],
            best_row["MAE"],
            best_row["RMSE"],
            best_row["R2"]
        ]
    )


best_models_data = pd.DataFrame(

    best_models,

    columns=[

        "TARGET",

        "BEST_MODEL",

        "MAE",

        "RMSE",

        "R2"
    ]
)


# ============================================================
# SAVE BEST MODELS SUMMARY
# ============================================================

best_models_file = (
    RESULT_DIR /
    "best_models.csv"
)


best_models_data.to_csv(
    best_models_file,
    index=False
)


# ============================================================
# SAVE FEATURE INFORMATION
# ============================================================

feature_information = pd.DataFrame(

    {
        "FEATURE": FEATURE_COLUMNS,

        "TYPE": [

            (
                "categorical"

                if column in CATEGORICAL_FEATURE_COLUMNS

                else "numeric"
            )

            for column in FEATURE_COLUMNS
        ]
    }
)


feature_information_file = (
    RESULT_DIR /
    "model_features.csv"
)


feature_information.to_csv(
    feature_information_file,
    index=False
)


# ============================================================
# SAVE EVALUATION PREPROCESSOR
# ============================================================

evaluation_preprocessor_file = (
    MODEL_DIR /
    "evaluation_preprocessor.pkl"
)


joblib.dump(
    preprocessor,
    evaluation_preprocessor_file
)


# ============================================================
# RETRAIN BEST MODELS ON ALL AVAILABLE LABELED DATA
# ============================================================

print()

print("=" * 70)
print("RETRAINING BEST MODELS ON ALL LABELED DATA")
print("=" * 70)

print()


# ============================================================
# ALL LABELED DATA
# ============================================================

deployment_data = data.dropna(

    subset=[

        "NEXT_MONTH_TRAFFIC",

        "NEXT_MONTH_REVENUE"
    ]

).copy()


X_all = deployment_data[
    FEATURE_COLUMNS
].copy()


# ============================================================
# DEPLOYMENT PREPROCESSOR
# ============================================================

deployment_preprocessor = ColumnTransformer(

    transformers=[

        (
            "categorical",

            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),

            CATEGORICAL_FEATURE_COLUMNS
        ),

        (
            "numeric",

            "passthrough",

            NUMERIC_FEATURE_COLUMNS
        )
    ]
)


# ============================================================
# FIT DEPLOYMENT PREPROCESSOR
# ============================================================

X_all_encoded = (
    deployment_preprocessor.fit_transform(
        X_all
    )
)


print(
    "Deployment input features:",
    len(FEATURE_COLUMNS)
)

print(
    "Deployment encoded shape:",
    X_all_encoded.shape
)


# ============================================================
# SAVE DEPLOYMENT PREPROCESSOR
# ============================================================

preprocessor_file = (
    MODEL_DIR /
    "preprocessor.pkl"
)


joblib.dump(
    deployment_preprocessor,
    preprocessor_file
)


print()

print(
    "Saved deployment preprocessor:"
)

print(preprocessor_file)


# ============================================================
# TRAIN AND SAVE BEST MODEL FOR EACH TARGET
# ============================================================

for target in TARGETS:

    best_model_name = (

        best_models_data.loc[

            best_models_data["TARGET"] == target,

            "BEST_MODEL"

        ].iloc[0]

    )


    print()

    print(
        "Final model for:",
        target
    )

    print(
        "Selected:",
        best_model_name
    )


    # ========================================================
    # CREATE FRESH FINAL MODEL
    # ========================================================

    if best_model_name == "XGBoost":

        best_model = XGBRegressor(

            n_estimators=300,

            max_depth=6,

            learning_rate=0.05,

            subsample=0.8,

            colsample_bytree=0.8,

            objective="reg:squarederror",

            random_state=42,

            n_jobs=-1

        )


    elif best_model_name == "LightGBM":

        best_model = LGBMRegressor(

            n_estimators=300,

            learning_rate=0.05,

            num_leaves=31,

            subsample=0.8,

            colsample_bytree=0.8,

            random_state=42,

            verbosity=-1,

            n_jobs=-1

        )


    else:

        best_model = RandomForestRegressor(

            n_estimators=300,

            random_state=42,

            n_jobs=-1

        )


    # ========================================================
    # TRAIN FINAL MODEL
    # ========================================================

    best_model.fit(

        X_all_encoded,

        deployment_data[target].values

    )


    # ========================================================
    # SAVE FINAL MODEL
    # ========================================================

    if target == "NEXT_MONTH_TRAFFIC":

        model_file = (
            MODEL_DIR /
            "best_traffic_model.pkl"
        )

    else:

        model_file = (
            MODEL_DIR /
            "best_revenue_model.pkl"
        )


    joblib.dump(
        best_model,
        model_file
    )


    print(
        "Saved:",
        model_file
    )


# ============================================================
# FINAL MODEL COMPARISON
# ============================================================

print()

print("=" * 70)
print("FINAL MODEL COMPARISON")
print("=" * 70)

print()

print(
    results.to_string(
        index=False
    )
)


# ============================================================
# BEST MODELS
# ============================================================

print()

print("=" * 70)
print("BEST MODELS")
print("=" * 70)

print()

print(
    best_models_data.to_string(
        index=False
    )
)


# ============================================================
# OUTPUT FILES
# ============================================================

print()

print("=" * 70)
print("MODEL OUTPUT FILES")
print("=" * 70)

print()

print("Model comparison:")
print(results_file)

print()

print("All predictions:")
print(predictions_file)

print()

print("Best models:")
print(best_models_file)

print()

print("Model features:")
print(feature_information_file)

print()

print("Evaluation preprocessor:")
print(evaluation_preprocessor_file)

print()

print("Deployment preprocessor:")
print(preprocessor_file)

print()

print("Saved models:")
print(MODEL_DIR)

print()

print("=" * 70)
print("STEP 13 COMPLETED")
print("=" * 70)