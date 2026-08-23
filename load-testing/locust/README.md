## Scenario-Based Load Testing

This Locust setup supports repeatable traffic scenarios for dataset collection.

### Scenarios

- `normal`: steady baseline traffic
- `ramp`: gradually increasing traffic
- `spike`: sudden jump to heavy traffic, then back down
- `heavy`: sustained high load

### How to Run

From `load-testing\locust\scripts` in PowerShell, use the wrapper script:

```powershell
.\collect_dataset.ps1 -Scenario normal -Reset
.\collect_dataset.ps1 -Scenario ramp
.\collect_dataset.ps1 -Scenario spike
.\collect_dataset.ps1 -Scenario heavy
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
