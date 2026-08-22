# K8s AutoGuard

K8s AutoGuard is a local Kubernetes DevSecOps lab that combines preventive policy enforcement, runtime event detection, anomaly classification, and scoped remediation decisions.

Its design intentionally makes destructive response opt-in: the remediation API reports a dry run unless active mode is explicitly enabled, and it can create policies only in the demo namespace.

Prometheus captures application security metrics, Loki captures logs, and Grafana provisions one security overview dashboard. The project records static validation separately from live cluster evidence so portfolio claims stay precise.

See the evidence pages for reproducible validation results and the ADRs for the technical decisions behind the lab.
