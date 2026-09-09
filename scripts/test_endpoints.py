import sys
import os
import importlib.util

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load ml_service
ml_path = os.path.join(root_dir, "ml_service", "app.py")
spec_ml = importlib.util.spec_from_file_location("ml_service_mod", ml_path)
ml_mod = importlib.util.module_from_spec(spec_ml)
spec_ml.loader.exec_module(ml_mod)

print("=== 1. Testing ML Service Prediction Status Logic ===")
# Test Normal
pred_norm = ml_mod.compute_prediction({
    "request_rate_per_sec": 8.5,
    "error_rate_per_sec": 0.0,
    "p90_latency_seconds": 0.21,
    "requests_in_progress": 3.0
})
print("Normal Baseline -> Status:", pred_norm["risk_level"], "Score:", pred_norm["anomaly_score"], "Triggers:", pred_norm["affected_metrics"])
assert pred_norm["risk_level"] == "Normal", "Expected Normal"

# Test Heavy Error Storm
pred_err = ml_mod.compute_prediction({
    "request_rate_per_sec": 105.3,
    "error_rate_per_sec": 21.0,
    "p90_latency_seconds": 0.024,
    "requests_in_progress": 88.0
})
print("Heavy Error Storm -> Status:", pred_err["risk_level"], "Score:", pred_err["anomaly_score"], "Triggers:", pred_err["affected_metrics"])
assert pred_err["risk_level"] == "High Risk", "Expected High Risk"

# Test Latency Spike
pred_lat = ml_mod.compute_prediction({
    "request_rate_per_sec": 30.0,
    "error_rate_per_sec": 0.0,
    "p90_latency_seconds": 1.2,
    "requests_in_progress": 20.0
})
print("Latency Spike -> Status:", pred_lat["risk_level"], "Score:", pred_lat["anomaly_score"], "Triggers:", pred_lat["affected_metrics"])
assert pred_lat["risk_level"] == "High Risk", "Expected High Risk"

print("\n=== 2. Testing Flask Backend Endpoints ===")
backend_path = os.path.join(root_dir, "app", "src", "app.py")
spec_be = importlib.util.spec_from_file_location("backend_app_mod", backend_path)
be_mod = importlib.util.module_from_spec(spec_be)
spec_be.loader.exec_module(be_mod)

backend_client = be_mod.app.test_client()

# Test /health
res = backend_client.get("/health")
print("/health response:", res.status_code, res.get_json())
assert res.status_code == 200

# Test /api/metrics/realtime
res = backend_client.get("/api/metrics/realtime")
print("/api/metrics/realtime response:", res.status_code, res.get_json())
assert res.status_code == 200
assert "request_rate_per_sec" in res.get_json()

# Test /api/demos/start with invalid scenario
res = backend_client.post("/api/demos/start", json={"scenario": "invalid_one"})
print("/api/demos/start (invalid) ->", res.status_code, res.get_json())
assert res.status_code == 400

# Test /api/demos/start with demo_latency
res = backend_client.post("/api/demos/start", json={"scenario": "demo_latency"})
print("/api/demos/start (demo_latency) ->", res.status_code, res.get_json())
assert res.status_code == 201
demo_id = res.get_json()["demo_id"]

# Test concurrency guard (starting second demo while first is active)
res_conflict = backend_client.post("/api/demos/start", json={"scenario": "demo_errors"})
print("/api/demos/start (concurrency conflict) ->", res_conflict.status_code, res_conflict.get_json())
assert res_conflict.status_code == 409, "Expected 409 Conflict when demo is already running"

# Test /api/demos/<demo_id>/status
res_status = backend_client.get(f"/api/demos/{demo_id}/status")
print(f"/api/demos/{demo_id}/status ->", res_status.status_code, res_status.get_json())
assert res_status.status_code == 200
assert res_status.get_json()["status"] in ["running", "completed"]

# Test /api/demos/active
res_active = backend_client.get("/api/demos/active")
print("/api/demos/active ->", res_active.status_code, res_active.get_json())
assert res_active.status_code == 200

# Stop demo
res_stop = backend_client.post("/api/demos/stop")
print("/api/demos/stop ->", res_stop.status_code, res_stop.get_json())
assert res_stop.status_code == 200

print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
