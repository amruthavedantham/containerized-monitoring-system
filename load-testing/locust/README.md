## Scenario-Based Load Testing

This Locust setup supports repeatable traffic scenarios for dataset collection.

### Scenarios

- `normal`: steady baseline traffic
- `ramp`: gradually increasing traffic
- `spike`: sudden jump to heavy traffic, then back down
- `heavy`: sustained high load
- `demo_latency`: one-minute demo where latency rises during the middle spike
- `demo_errors`: one-minute demo where latency and the error percentage rise together

### How to Run

From `load-testing\locust\scripts` in PowerShell, use the wrapper script:

```powershell
.\collect_dataset.ps1 -Scenario normal -Reset
.\collect_dataset.ps1 -Scenario ramp
.\collect_dataset.ps1 -Scenario spike
.\collect_dataset.ps1 -Scenario heavy
.\collect_dataset.ps1 -Scenario demo_latency
.\collect_dataset.ps1 -Scenario demo_errors
```

If PowerShell blocks the script, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\collect_dataset.ps1 -Scenario normal -Reset
```

### Scenario Timing

The built-in load shape runs each scenario automatically:

- `normal`: 20 users for 3 minutes
- `ramp`: 10 -> 25 -> 50 -> 75 -> 100 users over 5 minutes
- `spike`: 20 users, then 200 users, then back to 20 users
- `heavy`: 100 users, then 200 users, then 300 users
- `demo_latency`: 20 seconds baseline, 25 seconds at 150 users, then 15 seconds recovery
- `demo_errors`: same one-minute shape as `demo_latency`

The demo scenarios are designed for presentations. `demo_latency` increases the
share of `/slow` requests during the spike without generating errors.
`demo_errors` adds `/error` requests during that same phase, making the error
percentage rise alongside latency.

### What You Should Do

1. Start Docker Compose and make sure the Flask app is UP in Prometheus.
2. Open PowerShell in `load-testing\locust\scripts`.
3. Run `.\collect_dataset.ps1 -Scenario normal -Reset`.
4. Run `.\collect_dataset.ps1 -Scenario ramp`.
5. Run `.\collect_dataset.ps1 -Scenario spike`.
6. Run `.\collect_dataset.ps1 -Scenario heavy`.
7. Share the resulting CSV at `load-testing\locust\dataset_exports\monitoring_dataset.csv`.

### Output Files

- `load-testing\locust\dataset_exports\monitoring_dataset.csv`
- `load-testing\locust\dataset_exports\<timestamp>_<scenario>_locust_*` files from Locust

The dataset CSV includes:

- `timestamp_utc`
- `scenario`
- `scenario_phase`
- `request_rate_per_sec`
- `error_rate_per_sec`
- `p90_latency_seconds`
- `requests_in_progress`
