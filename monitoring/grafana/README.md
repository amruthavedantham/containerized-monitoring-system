# Grafana

## Purpose
Grafana is used to **visualize metrics collected by Prometheus**.

In this project, Grafana answers:
“Is the system healthy, and how do we know?”

Grafana provides visibility into system behavior but does not collect metrics or evaluate alert rules.

---

## What Grafana Does in This Project
- Connects to Prometheus as a data source
- Displays real-time dashboards for:
  - Request rate
  - Error rate
  - Latency percentiles
  - Service availability
- Helps correlate traffic, performance, and failures visually

---

## What Was Installed
- Grafana (Windows installer)

---

## Directory Structure


monitoring/grafana/ <br>
├── dashboards/ <br>
│   └── <exported-dashboard>.json <br>
├── datasources/ <br>
│   └── datasource.yml <br>
├── README.md 


---

## Configuration Summary

### datasource.yml
Defines:
- Prometheus as the Grafana data source
- Automatic data source provisioning
- Avoids manual UI configuration

### dashboards/
Contains exported Grafana dashboards created via the UI.

Dashboards are designed to be minimal and action-oriented.

---

## How to Run Grafana
Start Grafana using the Windows service or executable.

Grafana runs at: [http://localhost:3000](http://localhost:3000)



Default credentials:
- Username: admin
- Password: admin (prompted to change on first login)

---

## Verification Steps

1. Open Grafana UI: [http://localhost:3000](http://localhost:3000)

2. Verify Prometheus data source:

```
Connections → Data sources
```

Prometheus should show status **Connected**.

3. Verify dashboards:
```
Dashboards → Browse
```

Open the application monitoring dashboard.

Graphs should display data when application endpoints are accessed.

---

## Notes
- Grafana does not generate alerts in this setup
- Grafana reads data from Prometheus only
- Dashboards focus on clarity and operational usefulness

---

