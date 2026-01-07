# Prometheus

## Purpose
Prometheus is used to **collect application metrics** and **evaluate alert rules**.

In this project, Prometheus answers:
“Is the system healthy, and when should an engineer be alerted?”

Prometheus uses a **pull-based model** and scrapes metrics from the application’s `/metrics` endpoint.

---

## What Prometheus Does in This Project
- Scrapes metrics from the Flask application
- Stores time-series data (requests, latency, errors, availability)
- Evaluates alert rules:
  - ServiceDown
  - HighLatency
- Forwards firing alerts to Alertmanager

Prometheus is responsible for **detection**, not notification.

---

## What Was Installed
- Prometheus (Windows binary)
- promtool (bundled with Prometheus)

---

## Directory Structure
monitoring/prometheus/ <br>
├── prometheus-<version>.windows-amd64/ <br>
│ ├── prometheus.exe <br>
│ ├── promtool.exe <br>
├── config/ <br>
│ └── prometheus.yml <br>
├── rules/ <br>
│ └── alert_rules.yml <br>
├── README.md


---

## Configuration Summary

### prometheus.yml
Defines:
- Scrape interval and evaluation interval
- Target application (`/metrics`)
- Alert rule file location
- Alertmanager connection

### alert_rules.yml
Defines alert conditions:
- ServiceDown — application cannot be scraped
- HighLatency — request latency exceeds threshold

Alerts include:
- PromQL condition
- Duration (`for`)
- Severity and description

---

## How to Run Prometheus
From the Prometheus binary directory:

```bat
prometheus.exe --config.file=..\config\prometheus.yml
```
Prometheus runs at:
http://localhost:9090


---

### Verification Steps
Open Prometheus UI:
http://localhost:9090

Check scrape target status:
Status → Targets
Application should be UP

Verify alert rules are loaded:
Status → Rules
ServiceDown and HighLatency should be visible

Verify alerts page:
http://localhost:9090/rules

Validate rules using promtool:
``` bat
promtool.exe check rules ..\rules\alert_rules.yml 
```
Expected output:   
SUCCESS: 2 rules found

--- 

### Notes
- Prometheus evaluates alert rules continuously
- Prometheus does not send notifications directly
- Alertmanager handles alert delivery

---