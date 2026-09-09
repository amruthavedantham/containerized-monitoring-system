import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone


QUERY_MAP = {
    "request_rate_per_sec": "sum(rate(http_requests_total[1m]))",
    "error_rate_per_sec": "sum(rate(http_errors_total[1m]))",
    "p90_latency_seconds": (
        "histogram_quantile(0.9, "
        "sum(rate(http_request_duration_seconds_bucket[1m])) by (le))"
    ),
    "requests_in_progress": "max(http_requests_in_progress)",
}


PHASES = {
    "normal": [("normal", 180)],
    "ramp": [
        ("baseline", 60),
        ("ramp_25", 120),
        ("ramp_50", 180),
        ("ramp_75", 240),
        ("ramp_100", 300),
    ],
    "spike": [
        ("baseline", 90),
        ("spike", 150),
        ("recovery", 240),
    ],
    "heavy": [
        ("heavy_100", 90),
        ("heavy_200", 180),
        ("heavy_300", 270),
    ],
    "demo_latency": [
        ("baseline", 20),
        ("latency_spike", 40),
        ("recovery", 60),
    ],
    "demo_errors": [
        ("baseline", 20),
        ("error_spike", 40),
        ("recovery", 60),
    ],
}


def parse_iso8601(value: str) -> datetime:
    normalized = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def prom_query_range(base_url: str, query: str, start: datetime, end: datetime, step_seconds: int):
    params = urllib.parse.urlencode(
        {
            "query": query,
            "start": start.timestamp(),
            "end": end.timestamp(),
            "step": step_seconds,
        }
    )
    url = f"{base_url.rstrip('/')}/api/v1/query_range?{params}"
    last_error = None

    for attempt in range(1, 6):
        try:
            with urllib.request.urlopen(url, timeout=120) as response:
                payload = json.loads(response.read().decode("utf-8"))

            if payload.get("status") != "success":
                raise RuntimeError(f"Prometheus query failed for {query!r}: {payload}")

            result = payload["data"]["result"]
            if not result:
                return {}

            series = result[0].get("values", [])
            values = {}
            for ts, raw_value in series:
                values[int(round(float(ts)))] = raw_value
            return values
        except (urllib.error.URLError, TimeoutError, ConnectionAbortedError, ConnectionResetError, OSError) as exc:
            last_error = exc
            if attempt == 5:
                break
            time.sleep(2 * attempt)

    raise RuntimeError(f"Prometheus query failed for {query!r}: {last_error}") from last_error


def phase_for_elapsed(scenario: str, elapsed_seconds: float) -> str:
    phases = PHASES[scenario]
    for label, end_boundary in phases:
        if elapsed_seconds < end_boundary:
            return label
    return phases[-1][0]


def read_existing_rows(path: str):
    if not os.path.exists(path):
        return []
    with open(path, "r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main():
    parser = argparse.ArgumentParser(description="Export Prometheus metrics to CSV.")
    parser.add_argument("--prom-url", default="http://localhost:9090")
    parser.add_argument("--scenario", required=True, choices=sorted(PHASES.keys()))
    parser.add_argument("--start", required=True, help="ISO 8601 timestamp, e.g. 2026-08-23T14:00:00+05:30")
    parser.add_argument("--end", required=True, help="ISO 8601 timestamp, e.g. 2026-08-23T14:03:00+05:30")
    parser.add_argument("--step", type=int, default=10, help="Query step in seconds. Default: 10")
    parser.add_argument("--output", required=True, help="CSV file to write")
    parser.add_argument("--append", action="store_true", help="Append to an existing CSV file")
    args = parser.parse_args()

    start_dt = parse_iso8601(args.start)
    end_dt = parse_iso8601(args.end)
    if end_dt <= start_dt:
        raise SystemExit("End time must be after start time.")

    metric_series = {
        column: prom_query_range(args.prom_url, query, start_dt, end_dt, args.step)
        for column, query in QUERY_MAP.items()
    }

    timestamps = sorted({ts for series in metric_series.values() for ts in series.keys()})
    if not timestamps:
        raise SystemExit("No Prometheus samples found in the requested time window.")

    fieldnames = [
        "timestamp_utc",
        "scenario",
        "scenario_phase",
        "request_rate_per_sec",
        "error_rate_per_sec",
        "p90_latency_seconds",
        "requests_in_progress",
    ]

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    existing_rows = read_existing_rows(args.output) if args.append else []

    rows = []
    start_ts = start_dt.timestamp()
    for ts in timestamps:
        elapsed = ts - start_ts
        row = {
            "timestamp_utc": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(),
            "scenario": args.scenario,
            "scenario_phase": phase_for_elapsed(args.scenario, elapsed),
            "request_rate_per_sec": metric_series["request_rate_per_sec"].get(ts, ""),
            "error_rate_per_sec": metric_series["error_rate_per_sec"].get(ts, ""),
            "p90_latency_seconds": metric_series["p90_latency_seconds"].get(ts, ""),
            "requests_in_progress": metric_series["requests_in_progress"].get(ts, ""),
        }
        rows.append(row)

    if args.append and existing_rows:
        rows = existing_rows + rows

    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
