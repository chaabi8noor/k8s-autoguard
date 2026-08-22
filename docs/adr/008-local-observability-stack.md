# ADR 008: Use Prometheus, Loki, and Grafana for Local Security Observability

- Status: Accepted
- Date: 2026-08-22

## Context

K8s AutoGuard needs visible, reproducible evidence of anomaly classification, guarded remediation decisions, and application logs. The local KIND lab has limited compute and is intended for learning and demonstration rather than high availability.

## Decision

- Expose Prometheus text metrics from the ML and remediation APIs at `/metrics`.
- Deploy `kube-prometheus-stack` chart `88.5.3` with a 24-hour local retention period.
- Deploy Loki chart `7.3.0` in single-binary, filesystem-backed test-schema mode.
- Deploy Promtail chart `6.17.1` because the project brief requires Loki and Promtail. Treat it as a lab-only component because the chart is deprecated.
- Provision a Grafana dashboard with Prometheus and Loki data sources.
- Alert on detected anomalies and on actually applied, scoped remediation. Dry-run recommendations remain visible but do not claim that Kubernetes was mutated.

## Consequences

Positive:

- Prometheus can discover the two application services through versioned `ServiceMonitor` resources.
- Grafana provides one dashboard for detection, risk, remediation mode, and platform logs.
- Alert names and metric labels make it possible to distinguish detection from actual remediation.

Trade-offs:

- Loki uses a disposable local test schema and no persistent volume.
- Promtail is retained only to meet the brief; a future production iteration should migrate log collection to Grafana Alloy.
- The dashboard and alerts require a live cluster before they can provide runtime evidence.
