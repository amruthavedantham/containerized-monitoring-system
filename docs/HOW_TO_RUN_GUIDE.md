# How to Run: Containerized Monitoring & Alerting System

**Complete Quick-Reference Runbook • Docker Compose, Local Dev, Demos & ML Intelligence**

---

## 1. System Services & Access URLs

| Service Name | Container | Port | Access URL | Description |
| :--- | :--- | :--- | :--- | :--- |
| **React Frontend** | `react_frontend` | `5173` | [http://localhost:5173](http://localhost:5173) | ML Intelligence, Live Input Graph & Locust Demo Runner |
| **Flask App** | `flask_app` | `5000` | [http://localhost:5000](http://localhost:5000) | Instrumented REST API, Prometheus `/metrics` & Demo API |
| **ML Service** | `ml_service` | `5001` | [http://localhost:5001](http://localhost:5001) | Isolation Forest Anomaly Engine (`/predict` & metrics) |
| **Locust UI** | `locust` | `8089` | [http://localhost:8089](http://localhost:8089) | Interactive load generation & scenario launcher |
| **Prometheus** | `prometheus` | `9090` | [http://localhost:9090](http://localhost:9090) | TSDB scraping `flask_app` & `ml_service`, alert rules |
| **Grafana** | `grafana` | `3000` | [http://localhost:3000](http://localhost:3000) | Pre-provisioned dashboards (login: `admin / admin`) |
| **Alertmanager** | `alertmanager` | `9093` | [http://localhost:9093](http://localhost:9093) | Receives, groups and manages Prometheus alert triggers |

---

## 2. Method 1: Running with Docker Compose (Recommended)

To build and start all 7 services in containers connected via `monitoring_net`:

```powershell
# From project root:
docker compose down
docker compose up --build

# Or in detached background mode:
docker compose up --build -d
```

### Verification
1. Open **React Frontend**: [http://localhost:5173](http://localhost:5173) &rarr; API shows **Online** and ML Engine shows **Active**.
2. Open **Prometheus Targets**: [http://localhost:9090/targets](http://localhost:9090/targets) &rarr; Verify `flask_app` and `ml_service` are **UP**.
3. Open **Grafana**: [http://localhost:3000](http://localhost:3000) &rarr; View Flask monitoring dashboard.

### To Stop
```powershell
docker compose down
```

---

## 3. Method 2: Running Locally (Development Mode)

If running without Docker Desktop, launch each service in its own terminal window:

### Terminal 1: Flask Backend (Port 5000)
```powershell
python app/src/app.py
```

### Terminal 2: ML Service (Port 5001)
```powershell
python ml_service/app.py
```

### Terminal 3: React Frontend (Port 5173)
```powershell
cd frontend
npm run dev
```

### Terminal 4: Locust (Optional Web UI on Port 8089)
```powershell
cd load-testing\locust\scripts
locust -f locustfile.py
```

---

## 4. Interactive Locust 1-Minute Demo Scenarios

Two automated 60-second scenarios test latency surges and error storms:

### Scenario 1: `demo_latency` (60 Seconds)
- **Profile:** 0–20s baseline normal traffic $\rightarrow$ 20–40s spike with heavy `/slow` requests $\rightarrow$ 40–60s recovery.
- **Observed Behavior:** P90 Latency elevates to ~2.0s during middle spike while error percentage stays at 0%.

### Scenario 2: `demo_errors` (60 Seconds)
- **Profile:** 0–20s baseline normal traffic $\rightarrow$ 20–40s spike with both `/slow` AND intentional 500 `/error` requests $\rightarrow$ 40–60s recovery.
- **Observed Behavior:** Latency surges to ~2.0s AND error percentage surges to ~35–45%, triggering High Risk ML state and critical alerts.

### How to Trigger Demos:
- **Option A (Frontend One-Click):** In [http://localhost:5173](http://localhost:5173), click **Run Latency Demo** or **Run Latency + Errors Demo**.
- **Option B (PowerShell CLI):**
  ```powershell
  cd load-testing\locust\scripts
  .\collect_dataset.ps1 -Scenario demo_latency
  # OR
  .\collect_dataset.ps1 -Scenario demo_errors
  ```
- **Option C (REST API):**
  ```bash
  curl -X POST http://localhost:5000/api/demos/start -H "Content-Type: application/json" -d "{\"scenario\": \"demo_latency\"}"
  curl http://localhost:5000/api/demos/active
  ```

> [!NOTE]
> **Concurrency Protection:** Only 1 demo can run at a time. Starting a second demo while one is running returns `HTTP 409 Conflict`.

---

## 5. Frontend Features & Verification

- **Live Input Metrics Graph:** Visualizes Traffic (req/s), Latency (s), and Errors (err/s or %) with interactive tooltips and series toggles.
- **Anomaly Simulator:** Adjust sliders and click **Evaluate Custom Inputs** to test Isolation Forest predictions live.
- **Offline Status Test:** Stop the Flask backend (`docker stop flask_app` or `Ctrl+C`). The Status Banner immediately turns **RED** with **`Status: App is Down`** and `[OFFLINE]` badge.
