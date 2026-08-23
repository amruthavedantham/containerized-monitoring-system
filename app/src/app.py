from flask import Flask, jsonify, Response, render_template, g
import time
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


@app.before_request
def before_request():
    http_requests_in_progress.inc()
    http_requests_total.inc()
    g.start_time = time.time()


@app.after_request
def after_request(response):
    start_time = getattr(g, 'start_time', None)
    if start_time is not None:
        duration = time.time() - start_time
        http_request_duration_seconds.observe(duration)

    if response.status_code >= 500:
        http_errors_total.inc()

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
