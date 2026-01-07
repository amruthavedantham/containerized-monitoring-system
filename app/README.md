# Flask Observability Service

## Purpose

This service is a **minimal Flask-based microservice built solely for observability testing**.  
It does not implement business logic, persistence, authentication, or a frontend.

Its only goal is to **emit predictable Prometheus metrics** so that monitoring concepts such as:
- request volume
- latency distribution
- error rates
- in-flight requests  

can be **observed, queried, and validated** using Prometheus and Grafana.

This makes the service suitable for:
- learning observability fundamentals
- validating PromQL queries
- testing dashboards and alert rules
- viva and lab demonstrations

---

## Service Characteristics

- Runs on port **5000**
- Stateless
- JSON responses only
- Synchronous request handling
- Exposes Prometheus metrics at `/metrics`

---

## Endpoints and Their Purpose

### `/health`
**Why it exists**
- To act as a fast liveness/readiness probe

**Behavior simulated**
- Healthy service with negligible latency

**Expected outcome**
- Very low request duration
- No errors

---

### `/process`
**Why it exists**
- To represent a normal, successful application request

**Behavior simulated**
- Typical request processing with small but non-zero latency

**Expected outcome**
- Consistent success responses
- Moderate latency values in histograms

---

### `/slow`
**Why it exists**
- To intentionally generate slow requests

**Behavior simulated**
- Downstream slowness
- Blocking operations
- Performance degradation without failure

**Expected outcome**
- High latency recorded in histograms
- No increase in error count

---

### `/error`
**Why it exists**
- To generate controlled failures

**Behavior simulated**
- Application-level HTTP 500 errors

**Expected outcome**
- Error counter increments
- Latency still recorded
- Useful for testing error-rate alerts

---

### `/metrics`
**Why it exists**
- Prometheus scrape endpoint

**Behavior simulated**
- None

**Expected outcome**
- Exposes current metric values in Prometheus format
- Must not introduce application behavior or side effects

---

## Prometheus Metrics Exposed

The service exposes **exactly four metrics**.  
These metrics describe the full lifecycle of HTTP requests.

| Metric Name                         | Meaning |
|------------------------------------|--------|
| `http_requests_total`              | Total number of HTTP requests received by the service |
| `http_request_duration_seconds`    | Histogram of end-to-end HTTP request latency |
| `http_errors_total`                | Total number of failed HTTP requests (5xx) |
| `http_requests_in_progress`        | Number of HTTP requests currently being processed |

---

## Metric Semantics (High-Level)

- Every request increments `http_requests_total`
- Request latency is always recorded, including failures
- Only failed requests increment `http_errors_total`
- `http_requests_in_progress` increases at request start and decreases at request end, even on errors

These guarantees ensure the metrics are:
- internally consistent
- suitable for alerting
- safe for SLO calculations

---

## Scope and Non-Goals

This service intentionally does **not** include:
- authentication
- databases
- external dependencies
- retries or background jobs
- advanced routing or middleware

Any additional complexity would dilute its purpose as an observability testbed.

---

## Summary

This service is not a production application.  
It is a **controlled environment for observing system behavior through metrics**.

If dashboards, alerts, or queries do not behave as expected when using this service, the issue lies in the monitoring setup—not the application logic.
