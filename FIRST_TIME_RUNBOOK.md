# First-Time Setup and Runbook

Use this guide when someone receives this project for the first time and needs to run the full monitoring system on their own machine.

## What This Project Runs

This project has three parts:

- A Docker Compose stack for the Flask backend, Prometheus, Grafana, and Alertmanager.
- A separate React/Vite frontend that runs locally with `npm run dev`.
- A Locust load-testing script that runs locally with Python.

The frontend and Locust are not inside Docker in the current project structure.

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

Prometheus periodically scrapes the Flask application's `/metrics` endpoint and stores the collected metrics.

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

## Prerequisites

Install these once on the target machine:

- Docker Desktop
- Node.js and npm
- Python 3
- Git, if the project is cloned from a repository

Start Docker Desktop before running the project and wait until it says the engine is running.

Verify Node.js and npm:

```powershell
node -v
npm -v
```

Verify Python and pip:

```powershell
python --version
pip --version
```

## First-Time Setup

Open the project folder in VS Code.

If the project was copied to a different location, use that location instead of:

```text
D:\containerized-monitoring-system
```

Open three terminals in VS Code.

## Terminal 1 - Docker Services

From the project root:

```powershell
cd D:\containerized-monitoring-system
```

If containers from a previous session are still running, stop them first:

```powershell
docker compose down
```

Then start the services:

```powershell
docker compose up --build
```

On the first run, `--build` creates the Docker images before starting the containers.

This starts:

- Flask app
- Prometheus
- Grafana
- Alertmanager

Leave this terminal running.

For later runs, if Dockerfiles and container dependencies have not changed, this is enough:

```powershell
docker compose up
```

## Terminal 2 - Frontend

From the project root:

```powershell
cd D:\containerized-monitoring-system\frontend
npm install
npm run dev
```

Open the frontend:

```text
http://localhost:5173
```

Leave this terminal running.

For later runs, use:

```powershell
cd D:\containerized-monitoring-system\frontend
npm run dev
```

Run `npm install` again only if `package.json` or `package-lock.json` changes.

## Terminal 3 - Locust Load Testing

Use this terminal only when you want to generate traffic.

Install Locust once:

```powershell
pip install locust
```

Then run:

```powershell
cd D:\containerized-monitoring-system\load-testing\locust\scripts
locust -f locustfile.py
```

Open Locust:

```text
http://localhost:8089
```

Use this host value in the Locust UI:

```text
http://localhost:5000
```

Example Locust values:

```text
Number of users: 20
Spawn rate: 5
Host: http://localhost:5000
```

Click `Start swarming` to generate traffic.

## Browser URLs

Frontend:

```text
http://localhost:5173
```

Backend root endpoint:

```text
http://localhost:5000/
```

This page is optional. The primary backend verification endpoints are `/health`, `/metrics`, and `/process`.

Backend health check:

```text
http://localhost:5000/health
```

Backend metrics:

```text
http://localhost:5000/metrics
```

Backend process endpoint:

```text
http://localhost:5000/process
```

Backend slow endpoint:

```text
http://localhost:5000/slow
```

Backend intentional error endpoint:

```text
http://localhost:5000/error
```

Prometheus:

```text
http://localhost:9090
```

Prometheus targets:

```text
http://localhost:9090/targets
```

Expected target:

```text
flask_app -> UP
```

Grafana:

```text
http://localhost:3000
```

Default Grafana login:

```text
Username: admin
Password: admin
```

Alertmanager:

```text
http://localhost:9093
```

Locust:

```text
http://localhost:8089
```

## Grafana Setup

The current project has an empty Grafana datasource file:

```text
monitoring\grafana\datasources\datasource.yml
```

Because of that, Grafana may not automatically connect to Prometheus.

If Prometheus is not already listed as a data source, add it manually in Grafana:

```text
Connections -> Data sources -> Add data source -> Prometheus
```

Use this URL:

```text
http://prometheus:9090
```

Save and test the connection.

Import the included Grafana dashboard instead of recreating panels manually.

Dashboard file:

```text
monitoring\grafana\dashboards\FLASK_MONITORING_dashboard.json
```

To import it:

1. Open Grafana:

```text
http://localhost:3000
```

2. Log in with:

```text
Username: admin
Password: admin
```

3. Go to:

```text
Dashboards -> New -> Import
```

4. Click `Upload dashboard JSON file`.
5. Select:

```text
monitoring\grafana\dashboards\FLASK_MONITORING_dashboard.json
```

6. Select the Prometheus data source if Grafana asks for it.
7. If no Prometheus data source exists yet, create one first using `http://prometheus:9090`, then return and import the dashboard.
8. Click `Import`.

The dashboard should show traffic, errors, latency, and service availability once requests are sent to the Flask app.

The graphs will remain nearly flat until requests are sent to the Flask application.

Dashboard panels:

- Traffic shows how many requests the Flask app is receiving.
- Error Rate shows the rate of requests that resulted in errors.
- Latency shows slow responses, especially when `/slow` is called.
- Availability shows whether Prometheus can reach the Flask app.

## Demonstrating Monitoring

1. Start Docker services.
2. Start the frontend.
3. Start Locust.
4. In Locust, use host `http://localhost:5000`, users `20`, and spawn rate `5`.
5. Open Grafana and watch request traffic, errors, and latency update.
6. Open Prometheus targets and confirm `flask_app` is `UP`.

## Demonstration Flow

1. Open the React frontend and explain that it calls the Flask backend endpoints.
2. Open Prometheus targets and show that `flask_app` is `UP`.
3. Open Grafana and show the imported Flask monitoring dashboard.
4. Start Locust with host `http://localhost:5000`, users `20`, and spawn rate `5`.
5. Return to Grafana and show traffic, error rate, and latency changing.
6. Open Alertmanager and explain that it receives alerts from Prometheus.
7. Stop only the `flask_app` container in Docker Desktop.
8. Show the Prometheus target changing from `UP` to `DOWN`.
9. Show the alert appearing in Alertmanager.
10. Restart the `flask_app` container.
11. Show the target returning to `UP` and the alert resolving.

## Demonstrating Alerts

To trigger the `ServiceDown` alert:

1. Open Docker Desktop.
2. Stop only the `flask_app` container.
3. Wait for the duration configured in the Prometheus alert rule, typically around 30 to 60 seconds.
4. Open Prometheus targets:

```text
http://localhost:9090/targets
```

The Flask target should show as `DOWN`.

5. Open Alertmanager:

```text
http://localhost:9093
```

The alert should appear after Prometheus evaluates and sends it.

6. Restart the `flask_app` container.
7. Confirm Prometheus target changes back to `UP`.
8. Confirm the alert resolves.

To trigger the `HighLatency` alert, generate repeated traffic to `/slow` for more than one minute using Locust or the frontend.

## Python Dependencies

The Flask backend dependencies are installed inside the Docker image from:

```text
app\requirements\requirements.txt
```

You do not need to install Flask dependencies locally if you run the backend with Docker Compose.

For local Python tools, install Locust separately:

```powershell
pip install locust
```

## Proper Shutdown

Stop Locust:

```text
Ctrl + C
```

Stop the frontend:

```text
Ctrl + C
```

Stop Docker containers from the project root:

```powershell
cd D:\containerized-monitoring-system
docker compose down
```

You can leave Docker Desktop running, or quit it from the system tray if you are done.

## Quick Start Checklist

```text
1. Start Docker Desktop and wait for Engine running.

2. Terminal 1
   cd D:\containerized-monitoring-system
   docker compose up --build

3. Terminal 2
   cd D:\containerized-monitoring-system\frontend
   npm install
   npm run dev

4. Terminal 3, optional for load testing
   pip install locust
   cd D:\containerized-monitoring-system\load-testing\locust\scripts
   locust -f locustfile.py

5. Open:
   Frontend:     http://localhost:5173
   Health:       http://localhost:5000/health
   Metrics:      http://localhost:5000/metrics
   Process:      http://localhost:5000/process
   Prometheus:   http://localhost:9090
   Targets:      http://localhost:9090/targets
   Grafana:      http://localhost:3000
   Alertmanager: http://localhost:9093
   Locust:       http://localhost:8089

6. Locust host:
   http://localhost:5000

7. Shutdown:
   Ctrl + C for Locust
   Ctrl + C for Frontend
   docker compose down
```

## Common Issues

If a port is already in use, stop the program using that port or update the project port mapping.

Common ports used by this project:

```text
5000 - Flask backend
5173 - Vite frontend
9090 - Prometheus
9093 - Alertmanager
3000 - Grafana
8089 - Locust
```

If the frontend says the backend is offline, make sure Docker Compose is running and `http://localhost:5000/health` works.

If Prometheus target is down, check that the `flask_app` container is running.

If Grafana has no data, make sure the Prometheus data source uses:

```text
http://prometheus:9090
```

If dashboards are missing, import:

```text
monitoring\grafana\dashboards\FLASK_MONITORING_dashboard.json
```
