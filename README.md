# Containerized Monitoring and Alerting System

This project demonstrates how a containerized application can be monitored in real time using Prometheus, Grafana, Alertmanager, and Locust.

It includes a small Flask observability service, a React frontend for testing backend endpoints, a Prometheus-based monitoring stack, Grafana dashboard support, Alertmanager alerts, and Locust load testing.

## First-Time Setup

If you are running this project for the first time, start here:

[FIRST_TIME_RUNBOOK.md](FIRST_TIME_RUNBOOK.md)

The runbook contains the full setup, execution steps, Grafana dashboard import instructions, Locust configuration, alert demonstration flow, shutdown steps, and troubleshooting notes.

## What This Project Includes

- Flask backend service exposing health, test, slow, error, and metrics endpoints.
- Prometheus for scraping and storing application metrics.
- Grafana for visualizing traffic, errors, latency, and service availability.
- Alertmanager for receiving alerts from Prometheus.
- React/Vite frontend for interacting with the backend endpoints.
- Locust script for generating load against the Flask app.
- Docker Compose setup for running the backend and monitoring stack.

## Architecture

```text
                    User
                     |
                     v
            React Frontend (5173)
                     |
                     v
              Flask App (5000)
                     |
          exposes /metrics endpoint
                     |
                     v
             Prometheus (9090)
                     |
          stores time-series metrics
                     |
           +---------+---------+
           |                   |
           v                   v
     Grafana (3000)     Alertmanager (9093)
   Visualizes metrics     Handles alerts

Locust (8089) generates HTTP traffic to the Flask app.
```

Prometheus periodically scrapes the Flask application's `/metrics` endpoint and evaluates alert rules based on the collected metrics.

## Project Structure

```text
containerized-monitoring-system/
|
|-- app/
|-- frontend/
|-- load-testing/
|-- monitoring/
|   |-- grafana/
|   |   |-- dashboards/
|   |   `-- datasources/
|   |-- prometheus/
|   `-- alertmanager/
|-- docker/
|-- docker-compose.yml
|-- FIRST_TIME_RUNBOOK.md
`-- README.md
```

## Main URLs

After the project is running, use these URLs:

```text
Frontend:     http://localhost:5173
Backend:      http://localhost:5000
Health:       http://localhost:5000/health
Metrics:      http://localhost:5000/metrics
Prometheus:   http://localhost:9090
Grafana:      http://localhost:3000
Alertmanager: http://localhost:9093
Locust:       http://localhost:8089
```

## Quick Start

Start Docker Desktop first, then run the Docker services from the project root:

```powershell
docker compose down
docker compose up --build
```

Run the frontend in a separate terminal:

```powershell
cd frontend
npm install
npm run dev
```

Run Locust only when load testing is needed:

```powershell
cd load-testing\locust\scripts
locust -f locustfile.py
```

For complete first-time instructions, use [FIRST_TIME_RUNBOOK.md](FIRST_TIME_RUNBOOK.md).

## Backend Endpoints

The Flask service exposes:

```text
/health   - Health check endpoint
/process  - Normal successful request
/slow     - Delayed request for latency testing
/error    - Intentional 500 response for error testing
/metrics  - Prometheus metrics endpoint
```

## Grafana Dashboard

An exported Grafana dashboard is included at:

```text
monitoring\grafana\dashboards\FLASK_MONITORING_dashboard.json
```

Import this file in Grafana after creating the Prometheus data source with:

```text
http://prometheus:9090
```

Detailed dashboard import steps are available in [FIRST_TIME_RUNBOOK.md](FIRST_TIME_RUNBOOK.md).

## Demonstration Summary

A typical demonstration flow is:

1. Start Docker services.
2. Start the React frontend.
3. Confirm the Flask backend is healthy.
4. Confirm Prometheus target `flask_app` is `UP`.
5. Import/open the Grafana dashboard.
6. Start Locust and generate traffic.
7. Watch traffic, error rate, and latency update in Grafana.
8. Stop the `flask_app` container to trigger an alert.
9. Confirm the target goes `DOWN` in Prometheus.
10. Confirm the alert appears in Alertmanager.
11. Restart the Flask container and confirm recovery.

## Shutdown

Stop the frontend and Locust terminals with:

```text
Ctrl + C
```

Stop Docker services from the project root:

```powershell
docker compose down
```
