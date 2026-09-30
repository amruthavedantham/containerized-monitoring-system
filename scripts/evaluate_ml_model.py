"""Read-only evaluation of the checked-in Isolation Forest artifact.

This script does not import or modify the running Flask service. It evaluates
the same dataset, artifact, feature order, score normalization, and risk rules
used by ml_service/app.py.
"""

from pathlib import Path
import warnings

import joblib
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

warnings.filterwarnings("ignore", message="Pyarrow will become a required dependency")

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "load-testing" / "locust" / "dataset_exports" / "monitoring_dataset.csv"
MODEL_PATH = ROOT / "ml_service" / "model" / "isolation_forest.joblib"
FEATURES = [
    "request_rate_per_sec",
    "error_rate_per_sec",
    "p90_latency_seconds",
    "requests_in_progress",
]

def evaluate_risk(features, artifact):
    """Reproduce ml_service.app.compute_prediction for one feature vector."""
    model = artifact["model"]
    raw_score = float(model.decision_function(np.array([features], dtype=float))[0])
    score_max = artifact.get("score_max", 0.16)
    score_min = artifact.get("score_min", -0.23)
    model_score = float(np.clip((score_max - raw_score) / max(score_max - score_min, 1e-5), 0.0, 1.0))

    request_rate, error_rate, p90_latency, in_progress = map(float, features)
    affected_count = sum((
        error_rate > 0.5,
        p90_latency > 0.4,
        request_rate > 30.0,
        in_progress > 15.0,
    ))

    if (error_rate > 2.0 or (error_rate > 0.5 and p90_latency > 0.4)
            or affected_count >= 2 or model_score >= 0.75):
        return raw_score, model_score, max(model_score, 0.82), "High Risk"
    if affected_count >= 1 or model_score >= 0.50:
        return raw_score, model_score, max(model_score, 0.58), "Medium Risk"
    return raw_score, model_score, min(model_score, 0.22), "Normal"


def print_counts(title, series):
    print(title)
    for name, count in series.value_counts().sort_index().items():
        print(f"  {name}: {count}")


def main():
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Model artifact not found: {MODEL_PATH}")

    df = pd.read_csv(DATASET_PATH)
    artifact = joblib.load(MODEL_PATH)
    feature_names = artifact["feature_names"]
    if feature_names != FEATURES:
        raise ValueError(f"Unexpected artifact feature order: {feature_names}")

    # Match the service's artifact-median fallback for missing feature values.
    medians = artifact.get("medians", {})
    for feature in FEATURES:
        df[feature] = pd.to_numeric(df[feature], errors="coerce").fillna(medians.get(feature, 0.0))

    evaluations = [evaluate_risk(row, artifact) for row in df[FEATURES].to_numpy()]
    evaluation_frame = pd.DataFrame(
        evaluations,
        columns=["raw_score", "model_anomaly_score", "anomaly_score", "predicted_risk"],
        index=df.index,
    )
    df[["raw_score", "model_anomaly_score", "anomaly_score", "predicted_risk"]] = evaluation_frame

    print("ISOLATION FOREST EVALUATION (READ-ONLY)")
    print("=" * 40)
    print(f"Dataset: {DATASET_PATH.relative_to(ROOT)}")
    print(f"Model:   {MODEL_PATH.relative_to(ROOT)}")
    print(f"Samples: {len(df)}")
    print(f"Features: {', '.join(FEATURES)}")
    print(f"Model: IsolationForest(n_estimators={artifact['model'].n_estimators}, "
          f"contamination={artifact['model'].contamination}, random_state=42)")
    print(f"Score normalization: clip((score_max - raw_score) / (score_max - score_min), 0, 1)")
    print(f"score_min={artifact['score_min']:.6f}; score_max={artifact['score_max']:.6f}")
    print()

    has_scenario = "scenario" in df.columns
    print(f"Scenario column present: {has_scenario}")
    if has_scenario:
        print_counts("Scenario/class distribution:", df["scenario"])
        normal_samples = int((df["scenario"] == "normal").sum())
        proxy_abnormal_samples = int((df["scenario"] != "normal").sum())
        print(f"Normal-scenario samples: {normal_samples}")
        print(f"Non-normal-scenario samples (proxy abnormal): {proxy_abnormal_samples}")
    print()

    print("Anomaly-score statistics (deployed risk-adjusted score):")
    for name, value in df["anomaly_score"].describe()[["min", "mean", "std", "50%", "max"]].items():
        print(f"  {name}: {value:.6f}")
    print_counts("Predicted risk-level distribution:", df["predicted_risk"])
    print()

    if has_scenario:
        print("Scenario x predicted-risk distribution:")
        print(pd.crosstab(df["scenario"], df["predicted_risk"]).to_string())
        print()

        # Scenario is a workload label, so this is a transparent proxy analysis,
        # not an independent ground-truth benchmark.
        y_true = (df["scenario"] != "normal").astype(int)
        y_pred = (df["predicted_risk"] != "Normal").astype(int)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average="binary", zero_division=0
        )
        matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])

        print("PROXY BINARY EVALUATION")
        print("Definition: normal scenario = normal (0); ramp/spike/heavy = non-normal (1).")
        print("Prediction: Medium Risk or High Risk = anomaly (1); Normal = normal (0).")
        print(f"Accuracy:  {accuracy_score(y_true, y_pred):.6f}")
        print(f"Precision: {precision:.6f}")
        print(f"Recall:    {recall:.6f}")
        print(f"F1-score:  {f1:.6f}")
        print("Confusion matrix (rows=true [normal, non-normal]; columns=predicted [normal, anomaly]):")
        print(matrix)
        print()
        print("VALIDITY NOTE")
        print("These are proxy metrics, not unbiased ground-truth anomaly-detection metrics.")
        print("The scenario column records how load was generated, not independently labeled")
        print("per-sample anomalies. The artifact was also trained using the same dataset's")
        print("normal-scenario rows, so this evaluation includes training data. A paper should")
        print("describe this as an in-sample operational-regime comparison and use a held-out,")
        print("independently labeled test set for formal accuracy/precision/recall/F1 claims.")


if __name__ == "__main__":
    main()
