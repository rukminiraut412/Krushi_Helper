"""
Training script for KrushiRakshak Climate Risk Prediction Models.
Trains separate RandomForestClassifiers for:
- Drought Risk
- Flood Risk
- Heat Stress Risk
- Extreme Rainfall Risk
Saves the preprocessor and trained models to ml/models/climate_risk_models.joblib.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score

NUMERIC_FEATURES = [
    "temperature",
    "rainfall",
    "humidity",
    "soil_moisture",
    "forecast_rainfall",
    "historical_rainfall",
    "historical_temperature",
]

CATEGORICAL_FEATURES = [
    "crop_type",
    "soil_type",
    "water_availability",
]

TARGETS = {
    "drought": "drought_risk",
    "flood": "flood_risk",
    "heat": "heat_risk",
    "extreme_rainfall": "extreme_rainfall_risk",
}

def train_and_save_models():
    # 1. Resolve paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.dirname(current_dir)
    dataset_path = os.path.join(ml_dir, "dataset", "climate_risk_dataset.csv")
    models_dir = os.path.join(ml_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    out_model_path = os.path.join(models_dir, "climate_risk_models.joblib")

    print(f"[Training] Loading dataset from: {dataset_path}")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}. Please run generate_dataset.py first.")

    df = pd.read_csv(dataset_path)
    print(f"[Training] Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns.")

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    Y_dict = {key: df[col] for key, col in TARGETS.items()}

    # 2. Build Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
        ],
        remainder="drop"
    )

    # 3. Train/Test Split
    X_train, X_test, indices_train, indices_test = train_test_split(
        X, df.index, test_size=0.2, random_state=42
    )

    print("[Training] Fitting feature preprocessor...")
    X_train_trans = preprocessor.fit_transform(X_train)
    X_test_trans = preprocessor.transform(X_test)

    trained_models = {}
    metrics = {}

    print("\n" + "=" * 60)
    print("TRAINING INDIVIDUAL RANDOM FOREST CLASSIFIERS")
    print("=" * 60)

    for risk_name, col_name in TARGETS.items():
        y_train = df.loc[indices_train, col_name]
        y_test = df.loc[indices_test, col_name]

        print(f"\n--> Training RandomForest for [{risk_name.upper()}] risk...")
        clf = RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_split=4,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1
        )
        clf.fit(X_train_trans, y_train)

        # Evaluation
        y_pred = clf.predict(X_test_trans)
        y_proba = clf.predict_proba(X_test_trans)[:, 1]
        acc = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)

        trained_models[risk_name] = clf
        metrics[risk_name] = {"accuracy": acc, "roc_auc": auc}

        print(f"    Accuracy: {acc * 100:.2f}% | ROC-AUC: {auc:.4f}")
        print(f"    Test distribution: {np.bincount(y_test)} (Neg, Pos)")

    # 4. Serialize to ml/models/climate_risk_models.joblib
    bundle = {
        "version": "1.0.0",
        "preprocessor": preprocessor,
        "models": trained_models,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "targets": list(TARGETS.keys()),
        "metrics": metrics,
    }

    joblib.dump(bundle, out_model_path)
    print("\n" + "=" * 60)
    print(f"Successfully trained and saved model bundle to:\n{out_model_path}")
    print("=" * 60)

    return out_model_path

if __name__ == "__main__":
    train_and_save_models()
