import os
import sys
import time
import shutil
import threading
import subprocess
from collections import deque
from flask import Flask, jsonify, Response, render_template, request, g
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Metrics (DO NOT CHANGE NAMES OR TYPES)
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests"
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency"
)

http_errors_total = Counter(
    "http_errors_total",
    "Total number of HTTP error responses"
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed"
)

# Rolling window for real-time metric calculation (recent requests buffer)
# Stores tuples: (timestamp, duration, is_error)
RECENT_REQUESTS = deque(maxlen=500)
METRICS_LOCK = threading.Lock()

# Demo Execution Manager state
DEMOS = {}
ACTIVE_DEMO_LOCK = threading.Lock()
ACTIVE_DEMO_ID = None


def get_realtime_metrics():
    now = time.time()
    cutoff = now - 5.0  # Lookback window of 5 seconds

    with METRICS_LOCK:
        recent = [r for r in RECENT_REQUESTS if r[0] >= cutoff]

    req_count = len(recent)
    window_duration = max(now - (recent[0][0] if recent else now - 5.0), 1.0)
    req_rate = round(req_count / window_duration, 2) if req_count > 0 else 0.0

    err_count = sum(1 for r in recent if r[2])
    err_percentage = round((err_count / req_count) * 100.0, 2) if req_count > 0 else 0.0
    err_rate = round(err_count / window_duration, 2) if err_count > 0 else 0.0

    durations = sorted([r[1] for r in recent]) if recent else []
    if durations:
        avg_latency = round(sum(durations) / len(durations), 4)
        p90_idx = min(int(len(durations) * 0.9), len(durations) - 1)
        p90_latency = round(durations[p90_idx], 4)
    else:
        avg_latency = 0.0
        p90_latency = 0.0

    in_progress = float(http_requests_in_progress._value.get())

    return {
        "request_rate_per_sec": req_rate,
        "latency_seconds": avg_latency,
        "p90_latency_seconds": p90_latency,
        "error_percentage": err_percentage,
        "error_rate_per_sec": err_rate,
        "requests_in_progress": in_progress,
        "sample_count": req_count,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }


@app.before_request
def before_request():
    http_requests_in_progress.inc()
    http_requests_total.inc()
    g.start_time = time.time()


@app.after_request
def after_request(response):
    start_time = getattr(g, 'start_time', None)
    duration = 0.0
    is_error = False

    if start_time is not None:
        duration = time.time() - start_time
        http_request_duration_seconds.observe(duration)

    if response.status_code >= 500:
        http_errors_total.inc()
        is_error = True

    # Record in rolling window for real-time monitoring graphs
    if request.path not in ["/metrics", "/health", "/api/metrics/realtime"] and not request.path.startswith("/api/demos"):
        with METRICS_LOCK:
            RECENT_REQUESTS.append((time.time(), duration, is_error))

    http_requests_in_progress.dec()
    return response


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": "internal server error"}), 500


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/process", methods=["GET"])
def process():
    time.sleep(0.1)
    return jsonify({"result": "processed"}), 200


@app.route("/slow", methods=["GET"])
def slow():
    time.sleep(2)
    return jsonify({"result": "slow response"}), 200


@app.route("/error", methods=["GET"])
def error():
    return jsonify({"error": "intentional failure"}), 500


@app.route("/metrics", methods=["GET"])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


# Real-time metrics endpoint for live monitoring graphs
@app.route("/api/metrics/realtime", methods=["GET"])
def api_realtime_metrics():
    return jsonify(get_realtime_metrics()), 200


# Demo execution helper
def run_demo_worker(demo_id, scenario, cmd, env, working_dir):
    global ACTIVE_DEMO_ID
    demo = DEMOS[demo_id]
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=working_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        demo["process"] = proc

        # Capture logs
        output_lines = []
        for line in iter(proc.stdout.readline, ''):
            output_lines.append(line)
            if len(output_lines) > 200:
                output_lines.pop(0)
        proc.wait()

        demo["exit_code"] = proc.returncode
        demo["logs"] = "".join(output_lines)
        if proc.returncode == 0:
            demo["status"] = "completed"
        else:
            demo["status"] = "failed"
            demo["error"] = f"Locust process exited with code {proc.returncode}"
    except Exception as exc:
        demo["status"] = "failed"
        demo["error"] = str(exc)
    finally:
        demo["completed_at"] = time.time()
        with ACTIVE_DEMO_LOCK:
            if ACTIVE_DEMO_ID == demo_id:
                ACTIVE_DEMO_ID = None


@app.route("/api/demos/start", methods=["POST"])
def start_demo():
    global ACTIVE_DEMO_ID
    data = request.get_json(silent=True) or {}
    scenario = data.get("scenario", "").strip().lower()

    if scenario not in ["demo_latency", "demo_errors"]:
        return jsonify({
            "error": "Invalid scenario. Must be 'demo_latency' or 'demo_errors'."
        }), 400

    with ACTIVE_DEMO_LOCK:
        if ACTIVE_DEMO_ID and ACTIVE_DEMO_ID in DEMOS:
            current_demo = DEMOS[ACTIVE_DEMO_ID]
            if current_demo["status"] == "running":
                return jsonify({
                    "error": f"A demo ('{current_demo['scenario']}') is currently in progress. Please wait for it to complete.",
                    "active_demo_id": ACTIVE_DEMO_ID,
                    "active_scenario": current_demo["scenario"],
                    "remaining_seconds": max(0, int(60 - (time.time() - current_demo["start_time"])))
                }), 409

        demo_id = f"{scenario}_{int(time.time())}"
        demo_record = {
            "demo_id": demo_id,
            "scenario": scenario,
            "status": "running",
            "start_time": time.time(),
            "duration": 60,
            "process": None,
            "exit_code": None,
            "error": None,
            "logs": ""
        }
        DEMOS[demo_id] = demo_record
        ACTIVE_DEMO_ID = demo_id

    # Resolve Locust script location
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    locust_dir = os.path.join(project_root, "load-testing", "locust", "scripts")
    ps_script = os.path.join(locust_dir, "collect_dataset.ps1")
    locust_file = os.path.join(locust_dir, "locustfile.py")

    host_url = os.getenv("FLASK_HOST_URL", "http://localhost:5000")
    env = os.environ.copy()
    env["LOCUST_SCENARIO"] = scenario

    # Determine command to run: PowerShell script on Windows if available, otherwise direct Locust runner
    has_powershell = bool(shutil.which("powershell.exe") or shutil.which("powershell"))
    if sys.platform == "win32" and os.path.exists(ps_script) and has_powershell:
        cmd = [
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-File", ps_script,
            "-Scenario", scenario,
            "-HostUrl", host_url
        ]
        working_dir = locust_dir
    else:
        cmd = [
            sys.executable,
            "-m", "locust",
            "-f", locust_file,
            "--host", host_url,
            "--headless",
            "--run-time", "60s"
        ]
        working_dir = locust_dir

    t = threading.Thread(
        target=run_demo_worker,
        args=(demo_id, scenario, cmd, env, working_dir),
        daemon=True
    )
    t.start()

    return jsonify({
        "message": f"Demo '{scenario}' started successfully.",
        "demo_id": demo_id,
        "scenario": scenario,
        "status": "running",
        "duration": 60,
        "start_time": demo_record["start_time"]
    }), 201


@app.route("/api/demos/<demo_id>/status", methods=["GET"])
def get_demo_status(demo_id):
    demo = DEMOS.get(demo_id)
    if not demo:
        return jsonify({"error": f"Demo with id '{demo_id}' not found."}), 404

    elapsed = time.time() - demo["start_time"]
    if demo["status"] == "running" and elapsed >= demo["duration"] + 5:
        # Failsafe timeout after 65 seconds
        demo["status"] = "completed"

    remaining = max(0, int(demo["duration"] - elapsed))
    progress = min(100.0, round((elapsed / demo["duration"]) * 100.0, 1))

    return jsonify({
        "demo_id": demo_id,
        "scenario": demo["scenario"],
        "status": demo["status"],
        "elapsed_seconds": round(elapsed, 1),
        "remaining_seconds": remaining,
        "total_seconds": demo["duration"],
        "progress_percent": progress,
        "current_metrics": get_realtime_metrics(),
        "error": demo.get("error")
    }), 200


@app.route("/api/demos/active", methods=["GET"])
def get_active_demo():
    with ACTIVE_DEMO_LOCK:
        current_id = ACTIVE_DEMO_ID

    if not current_id or current_id not in DEMOS:
        return jsonify({"active": False, "demo": None}), 200

    demo = DEMOS[current_id]
    elapsed = time.time() - demo["start_time"]
    remaining = max(0, int(demo["duration"] - elapsed))
    progress = min(100.0, round((elapsed / demo["duration"]) * 100.0, 1))

    return jsonify({
        "active": demo["status"] == "running",
        "demo": {
            "demo_id": demo["demo_id"],
            "scenario": demo["scenario"],
            "status": demo["status"],
            "elapsed_seconds": round(elapsed, 1),
            "remaining_seconds": remaining,
            "total_seconds": demo["duration"],
            "progress_percent": progress,
            "current_metrics": get_realtime_metrics()
        }
    }), 200


@app.route("/api/demos/stop", methods=["POST"])
def stop_active_demo():
    global ACTIVE_DEMO_ID
    with ACTIVE_DEMO_LOCK:
        if not ACTIVE_DEMO_ID or ACTIVE_DEMO_ID not in DEMOS:
            return jsonify({"message": "No active demo to stop."}), 200
        demo = DEMOS[ACTIVE_DEMO_ID]
        proc = demo.get("process")
        if proc and proc.poll() is None:
            try:
                proc.terminate()
            except Exception:
                pass
        demo["status"] = "completed"
        ACTIVE_DEMO_ID = None

    return jsonify({"message": f"Demo '{demo['scenario']}' stopped."}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
