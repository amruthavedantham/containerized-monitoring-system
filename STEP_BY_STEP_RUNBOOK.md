# Step-by-Step Runbook: Containerized Monitoring & ML Anomaly Detection System

This guide provides complete, step-by-step instructions to set up, run, and demonstrate the **Containerized Monitoring & Predictive Anomaly Detection System** in **VS Code**.

---

## 📋 System Requirements & Prerequisites

Ensure the following tools are installed on your system before proceeding:

1. **Visual Studio Code (VS Code)**
2. **Python 3.10 or higher** (with `pip`)
3. **Node.js 18 or higher** (with `npm`)
4. **Docker Desktop** (running and WSL2/Hyper-V enabled)
5. **Git**

---

## 🚀 Step 1: Open the Project in VS Code

1. Launch **VS Code**.
2. Go to **File** > **Open Folder...**
3. Select the project directory:
   `c:\Users\aksha\Downloads\containerized-monitoring-system-main`
4. Open the integrated terminal in VS Code:
   - Shortcut: `Ctrl + ~` (or `Terminal` > `New Terminal`).

---

## 🐍 Step 2: Set Up Python & ML Service Environment

1. In the VS Code terminal, navigate to the `ml_service` directory:
   ```bash
   cd ml_service
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   *Required packages installed: `flask`, `prometheus-client`, `pandas`, `scikit-learn`, `numpy`, `joblib`, `requests`.*

3. Train the **Isolation Forest Model** on the Locust synthetic dataset:
   ```bash
   python train.py
   ```
   *Expected Output:*
   ```text
   Loading dataset from .../load-testing/locust/dataset_exports/monitoring_dataset.csv...
   Fitting Isolation Forest on 19 baseline training samples...
   Model saved successfully to .../ml_service/model/isolation_forest.joblib
   ```

4. Start the ML Prediction Service:
   ```bash
   python app.py
   ```
   *The service will start listening on `http://localhost:5001`.*

---

## ⚡ Step 3: Start the Flask Application Backend

Open a **new terminal tab** in VS Code (`Ctrl + Shift + ~` or click `+` in terminal):

1. Install backend requirements (if not already installed):
   ```bash
   pip install -r app/requirements/requirements.txt
   ```

2. Run the Flask application:
   ```bash
   python app/src/app.py
   ```
   *The Flask app will start listening on `http://localhost:5000`.*

---

## 💻 Step 4: Set Up and Run the React Frontend Dashboard

Open another **new terminal tab** in VS Code:

1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Launch the React Vite development server:
   ```bash
   npm run dev
   ```
   *Output:*
   ```text
   ➜  Local:   http://localhost:5173/
   ```

4. Open your browser and navigate to:
   `http://localhost:5173/`

---

## 🐳 Step 5: Launch the Full Monitoring Stack with Docker Compose

To run all services in production containerized mode (Flask App, Prometheus, Alertmanager, Grafana, ML Service):

1. Ensure **Docker Desktop** is running.
2. Open a terminal tab at the project root and run:
   ```bash
   docker-compose up --build
   ```
3. Docker will build and launch all 5 containers:
   - **Flask App**: `http://localhost:5000`
   - **ML Prediction Service**: `http://localhost:5001`
   - **Prometheus UI**: `http://localhost:9090`
   - **Alertmanager UI**: `http://localhost:9093`
   - **Grafana Dashboard**: `http://localhost:3000` (Default login: `admin` / `admin`)

---

## 🧪 Step 6: Generate Synthetic Traffic using Locust

To test real-time metric capture and anomaly detection:

1. Open a new terminal tab at project root:
   ```bash
   cd load-testing/locust/scripts
   ```

2. Install Locust (if needed):
   ```bash
   pip install locust
   ```

3. Launch Locust load test targeting the Flask app:
   ```bash
   locust -f locustfile.py --host=http://localhost:5000
   ```

4. Open `http://localhost:8089` in your web browser.
5. Set parameters:
   - **Number of users**: `50`
   - **Spawn rate**: `5`
6. Click **Start Swarm** and observe metrics streaming into Prometheus, ML Service, and the React UI!

---

## 📊 Step 7: How to Use and Demonstrate the React Dashboard

1. Navigate to `http://localhost:5173/`.
2. **ML Intelligence Tab**:
   - View the live **Prediction Status** (`NORMAL`, `MEDIUM RISK`, `HIGH RISK`).
   - View the **Anomaly Score Meter** ($0.00$ to $1.00$).
   - Inspect the 4 **Feature Health Matrix Cards** (`Request Rate`, `HTTP Error Rate`, `P90 Latency`, `In-Progress Reqs`).
3. **Interactive Scenario Simulator**:
   - Click preset buttons:
     - 🟢 **Normal Baseline** → Status: `Normal` (Score ~0.20)
     - 🟡 **Ramp Up Load** → Status: `Normal` / `Medium Risk`
     - 🔴 **Traffic Spike** → Status: `Medium Risk` (Score ~0.70)
     - ⚠️ **Heavy Error Storm** → Status: `High Risk` (Score ~0.75+)
   - Move sliders manually to test custom feature vectors in real time!
4. **API Tester Tab**:
   - Test endpoints: `/health`, `/process`, `/slow`, `/error`, `/metrics`.

---

## 🔍 Step 8: Verify Prometheus Metrics & Alerts

1. Open **Prometheus** at `http://localhost:9090`.
2. Search for predictive metrics:
   - `ml_anomaly_score`
   - `ml_anomaly_risk_level`
3. Click **Status** > **Rules** to view active predictive alert rules:
   - `PredictiveHighAnomalyRisk`
   - `PredictiveMediumAnomalyRisk`
4. Open **Alertmanager** at `http://localhost:9093` to view fired warnings when anomaly scores exceed thresholds.

---

## 🛠️ Port & Service Cheat Sheet

| Service | Host Port | Internal Port | Description |
| :--- | :--- | :--- | :--- |
| **Flask App** | `5000` | `5000` | Core Application API |
| **ML Service** | `5001` | `5001` | Isolation Forest Prediction Microservice |
| **React Dashboard** | `5173` | `5173` | Developer UI & Interactive Simulator |
| **Prometheus** | `9090` | `9090` | Time-series Metrics Database |
| **Alertmanager** | `9093` | `9093` | Predictive Alert Dispatcher |
| **Grafana** | `3000` | `3000` | Visual Monitoring Analytics |
| **Locust UI** | `8089` | `8089` | Synthetic Load Testing Tool |

---

## ⚙️ Troubleshooting

- **`vite` or `npm` command not found**:
  Run `npm install` inside the `frontend` folder first.
- **`port 5000` or `5001` already in use**:
  Kill existing python processes:
  *Windows PowerShell:* `Stop-Process -Name python -Force`
- **Missing dataset error during training**:
  Ensure `load-testing/locust/dataset_exports/monitoring_dataset.csv` exists.
