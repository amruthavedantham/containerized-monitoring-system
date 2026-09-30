import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

FEATURE_NAMES = [
    "request_rate_per_sec",
    "error_rate_per_sec",
    "p90_latency_seconds",
    "requests_in_progress"
]

def train_model(dataset_path, output_model_path):
    print(f"Loading dataset from {dataset_path}...")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found at {dataset_path}")

    df = pd.read_csv(dataset_path)
    
    # Handle missing values by imputing column medians
    for col in FEATURE_NAMES:
        if col in df.columns:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
        else:
            df[col] = 0.0

    X_all = df[FEATURE_NAMES].values

    # Train Isolation Forest on normal baseline data or full dataset with contamination
    # Using scenario == 'normal' if present for baseline reference
    normal_mask = df['scenario'] == 'normal' if 'scenario' in df.columns else np.ones(len(df), dtype=bool)
    X_normal = X_all[normal_mask] if normal_mask.sum() > 10 else X_all

    print(f"Fitting Isolation Forest on {len(X_normal)} baseline training samples...")
    model = IsolationForest(
        n_estimators=100,
        contamination=0.1,
        random_state=42
    )
    model.fit(X_normal)

    # Compute decision function scores
    # Higher score = normal, Lower score = anomalous
    scores_normal = model.decision_function(X_normal)
    scores_all = model.decision_function(X_all)

    score_max = float(np.max(scores_normal))
    score_min = float(np.min(scores_all))

    print(f"Decision function range - Max (Normal): {score_max:.4f}, Min (Overall): {score_min:.4f}")

    # Package model and calibration metadata
    artifact = {
        "model": model,
        "feature_names": FEATURE_NAMES,
        "score_max": score_max,
        "score_min": score_min,
        "medians": df[FEATURE_NAMES].median().to_dict()
    }

    os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
    joblib.dump(artifact, output_model_path)
    print(f"Model saved successfully to {output_model_path}")

    # Validate predictions on dataset scenarios
    df['raw_score'] = scores_all
    # Calibrate anomaly score to [0.0, 1.0] (0 = normal, 1 = extreme anomaly)
    denom = max(score_max - score_min, 1e-5)
    df['anomaly_score'] = np.clip((score_max - df['raw_score']) / denom, 0.0, 1.0)
    
    def get_risk(score):
        if score >= 0.75:
            return "High Risk"
        elif score >= 0.50:
            return "Medium Risk"
        else:
            return "Normal"

    df['risk_level'] = df['anomaly_score'].apply(get_risk)

    if 'scenario' in df.columns:
        print("\nScenario Risk Level Breakdown:")
        print(pd.crosstab(df['scenario'], df['risk_level']))

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_file = os.path.join(base_dir, "load-testing", "locust", "dataset_exports", "monitoring_dataset.csv")
    model_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "isolation_forest.joblib")
    train_model(dataset_file, model_file)
