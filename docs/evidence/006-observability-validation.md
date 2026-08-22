# Observability Validation Plan

- Date: 2026-08-22
- Scope: Prometheus metrics, Loki logs, Grafana dashboard, and Prometheus alert rules

## Repository Validation Completed

The following checks completed without a running Kubernetes cluster:

| Check | Result |
| --- | --- |
| Metrics unit and API tests | 22 tests passed across model, benchmark, API, observability, and remediation modules |
| `kube-prometheus-stack` Helm rendering | Passed with chart `88.5.3` |
| Loki Helm rendering | Passed with chart `7.3.0` in local single-binary test-schema mode |
| Promtail Helm rendering | Passed with chart `6.17.1`; the chart reports its deprecation warning |
| Dashboard YAML and embedded JSON parsing | Passed |
| ServiceMonitor and PrometheusRule YAML parsing | Passed for 3 Kubernetes resources |

## Live Validation Procedure

Docker Desktop WSL integration is required before these checks can be recorded as runtime evidence.

```bash
./scripts/deploy-autoguard-platform.sh
./scripts/install-observability.sh
./scripts/run-final-project-demo.sh --interactive
```

The final demo script submits a high-risk ML event and a guarded remediation event, then `validate-observability.sh` confirms that both services expose the expected metric families through Kubernetes service proxies.

Open Grafana locally:

```bash
kubectl -n monitoring port-forward service/autoguard-monitoring-grafana 3000:80
```

Use username `admin` and retrieve the generated password without committing it:

```bash
kubectl -n monitoring get secret autoguard-monitoring-grafana \
  -o jsonpath='{.data.admin-password}' | base64 --decode
```

Capture the dashboard and the Grafana alert page only after the live commands complete successfully. Do not replace this plan with fabricated screenshots.
