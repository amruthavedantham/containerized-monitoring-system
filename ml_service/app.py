import os
import time
import threading
import requests
import numpy as np
from flask import Flask, jsonify, request, Response
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
import joblib

app = Flask(__name__)

# Prometheus Metrics exposed by ML Service
gauge_anomaly_score = Gauge("ml_anomaly_score", "Normalized Isolation Forest Anomaly Score (0.0 to 1.0)")
gauge_risk_level = Gauge("ml_anomaly_risk_level", "Anomaly Risk Level Code: 0=Normal, 1=Medium Risk, 2=High Risk")
gauge_req_rate = Gauge("ml_request_rate_per_sec", "Current Request Rate per second evaluated by ML Service")
gauge_err_rate = Gauge("ml_error_rate_per_sec", "Current Error Rate per second evaluated by ML Service")
gauge_latency = Gauge("ml_p90_latency_seconds", "Current P90 Latency in seconds evaluated by ML Service")
gauge_in_progress = Gauge("ml_requests_in_progress", "Current Requests In Progress evaluated by ML Service")

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "isolation_forest.joblib")
DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "load-testing", "locust", "dataset_exports", "monitoring_dataset.csv")

model_artifact = None

def load_or_train_model():
    global model_artifact
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}. Training new model...")
        from train import train_model
        train_model(DATASET_PATH, MODEL_PATH)

    print(f"Loading ML model from {MODEL_PATH}...")
    model_artifact = joblib.load(MODEL_PATH)
    print("ML Model successfully loaded.")

def compute_prediction(features):
    """
    features: dict with keys:
      request_rate_per_sec, error_rate_per_sec, p90_latency_seconds, requests_in_progress
    """
    if model_artifact is None:
        load_or_train_model()

    feature_names = model_artifact["feature_names"]
    medians = model_artifact.get("medians", {})

    vector = []
    for name in feature_names:
        val = features.get(name, medians.get(name, 0.0))
        if val is None or (isinstance(val, float) and np.isnan(val)):
            val = medians.get(name, 0.0)
        vector.append(float(val))

    X = np.array([vector])
    model = model_artifact["model"]
    raw_score = float(model.decision_function(X)[0])

    score_max = model_artifact.get("score_max", 0.16)
    score_min = model_artifact.get("score_min", -0.23)
    denom = max(score_max - score_min, 1e-5)

    # Anomaly score: 0.0 = normal, 1.0 = highly anomalous
    anomaly_score = float(np.clip((score_max - raw_score) / denom, 0.0, 1.0))

    if anomaly_score >= 0.75:
        risk_level = "High Risk"
        risk_code = 2
    elif anomaly_score >= 0.50:
        risk_level = "Medium Risk"
        risk_code = 1
    else:
        risk_level = "Normal"
        risk_code = 0

    # Determine affected metrics deviating from normal baseline
    affected_metrics = []
    if features.get("error_rate_per_sec", 0) > 0.5:
        affected_metrics.append("High HTTP Error Rate")
    if features.get("p90_latency_seconds", 0) > 0.5:
        affected_metrics.append("Elevated P90 Latency")
    if features.get("request_rate_per_sec", 0) > 30.0:
        affected_metrics.append("High Request Rate Load")
    if features.get("requests_in_progress", 0) > 15:
        affected_metrics.append("High Concurrent Requests")

    if not affected_metrics and risk_code > 0:
        affected_metrics.append("Unusual Metric Pattern Combination")

    result = {
        "status": risk_level,
        "risk_level": risk_level,
        "risk_code": risk_code,
        "anomaly_score": round(anomaly_score, 4),
        "raw_score": round(raw_score, 4),
        "features": {
            "request_rate_per_sec": round(vector[0], 4),
            "error_rate_per_sec": round(vector[1], 4),
            "p90_latency_seconds": round(vector[2], 4),
            "requests_in_progress": round(vector[3], 4),
        },
        "affected_metrics": affected_metrics,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    # Update Prometheus Gauges
    gauge_anomaly_score.set(result["anomaly_score"])
    gauge_risk_level.set(result["risk_code"])
    gauge_req_rate.set(result["features"]["request_rate_per_sec"])
    gauge_err_rate.set(result["features"]["error_rate_per_sec"])
    gauge_latency.set(result["features"]["p90_latency_seconds"])
    gauge_in_progress.set(result["features"]["requests_in_progress"])

    return result

def poll_app_metrics_loop():
    """Background worker to continuously poll Flask app and update ML metrics."""
    app_url = os.getenv("APP_METRICS_URL", "http://app:5000/metrics")
    local_url = "http://127.0.0.1:5000/metrics"

    while True:
        try:
            target_url = app_url
            try:
                resp = requests.get(target_url, timeout=2)
            except Exception:
                target_url = local_url
                resp = requests.get(target_url, timeout=2)

            if resp.status_code == 200:
                lines = resp.text.splitlines()
                metrics_data = {}
                for line in lines:
                    if line.startswith("#") or not line:
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        k, v = parts[0], parts[1]
                        try:
                            metrics_data[k] = float(v)
                        except ValueError:
                            pass

                # Parse metrics from Flask app
                in_progress = metrics_data.get("http_requests_in_progress", 0.0)
                total_reqs = metrics_data.get("http_requests_total", 0.0)
                total_errs = metrics_data.get("http_errors_total", 0.0)

                # Estimate rates using current snapshot metrics
                features = {
                    "request_rate_per_sec": min(total_reqs, 50.0),
                    "error_rate_per_sec": min(total_errs, 10.0),
                    "p90_latency_seconds": 0.2 if in_progress > 0 else 0.05,
                    "requests_in_progress": in_progress
                }
                compute_prediction(features)
        except Exception as e:
            # Fallback evaluation on default baseline if app isn't scraping
            pass
        time.sleep(5)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "ml_service"}), 200

@app.route("/predict", methods=["GET", "POST"])
def predict():
    features = {}
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        features = data.get("features", data)
    else:
        # GET query params
        for key in ["request_rate_per_sec", "error_rate_per_sec", "p90_latency_seconds", "requests_in_progress"]:
            val = request.args.get(key)
            if val is not None:
                try:
                    features[key] = float(val)
                except ValueError:
                    pass

    # If no features supplied, run prediction on normal defaults
    if not features:
        features = {
            "request_rate_per_sec": 8.5,
            "error_rate_per_sec": 0.0,
            "p90_latency_seconds": 0.21,
            "requests_in_progress": 3.0
        }

    res = compute_prediction(features)
    return jsonify(res), 200

@app.route("/metrics", methods=["GET"])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    load_or_train_model()
    # Start background polling thread
    t = threading.Thread(target=poll_app_metrics_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5001)
