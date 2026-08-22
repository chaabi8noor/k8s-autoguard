# K8s AutoGuard Final Project Report

## Executive Summary

K8s AutoGuard is a local Kubernetes DevSecOps lab that combines preventive admission policy, runtime detection, network security, anomaly analysis, guarded remediation, and observable evidence. It is designed as a learning and portfolio project: each control is versioned, reproducible, and linked to a validation command.

## Architecture

```text
GitHub pull request
  -> Kyverno test and Trivy gates
  -> KIND with Cilium and Hubble
  -> Falco runtime event
  -> ML anomaly classification API
  -> guarded remediation API
  -> Prometheus metrics, Loki logs, Grafana dashboard
  -> optional scoped Cilium isolation policy
```

## Implemented Controls

| Layer | Implementation | Evidence |
| --- | --- | --- |
| Local infrastructure | Two-node KIND, Terraform declaration, Ansible bootstrap | Cilium-ready cluster workflow and ADR 001 |
| Network security | Cilium and Hubble, trusted-client policy demo | 77 applicable Cilium connectivity tests and allowed-versus-denied demo |
| Runtime detection | Falco modern eBPF | Controlled runtime event and terminal-shell detection |
| Admission control | Kyverno Restricted Pod Security policy | Secure fixture admitted, insecure fixture denied |
| Supply chain | Trivy manifest and pinned-image scans | Protected GitHub Actions security gates |
| Detection | Isolation Forest on deterministic scenario data | 1.00 recall and 0.08 false-positive rate on 520 labelled events |
| Response | Guarded dry-run remediation with narrow Cilium RBAC | Tested scoped isolation-policy construction |
| Delivery | Protected `main`, Terraform, Ansible, Argo CD application manifest | Reviewed and merged pull requests |
| Observability | Prometheus metrics, Loki, Promtail, Grafana, alerts | Versioned Helm values, dashboard, and live-validation runbook |

## Safety Model

Remediation defaults to dry run. A Cilium policy can be created only when the event is anomalous, risk meets the configured threshold, Falco severity is high or critical, and the namespace is `autoguard-demo`. The Kubernetes Role allows only create, get, and list access to CiliumNetworkPolicies in that namespace.

## Verified Results

- Cilium connectivity validation: 77 applicable tests and 320 actions passed.
- Falco detected both a controlled file operation and an interactive container shell.
- Kyverno admitted a Restricted-profile fixture and denied an insecure fixture.
- Trivy CI gates and Python quality tests passed on protected pull requests.
- The development benchmark measured 1.00 recall, 0.08 false-positive rate, and 38.69 ms P95 in-process classification latency on synthetic scenario data.
- The observability metric tests, embedded Grafana dashboard JSON, custom resource YAML, and all pinned Helm templates validated locally.

## Limitations and Final Runtime Acceptance

Synthetic benchmark measurements are not production MTTD or MTTR claims. The Loki deployment is intentionally disposable and uses the chart test schema for the local lab. Promtail is included because the brief requests it, but should be replaced with Grafana Alloy in a future production-oriented iteration.

The last acceptance step requires Docker Desktop WSL integration: deploy the platform, install observability, run the final demo, record the video, and capture Grafana evidence. The exact commands are documented in [the observability validation plan](evidence/006-observability-validation.md) and [video runbook](demo/final-project-demo.md).

## Future Work

- Replace Promtail with Grafana Alloy.
- Add a real Falco event transport with authentication and durable storage.
- Train and evaluate against representative non-synthetic events.
- Add approval workflows before activating remediation mode.
- Publish the MkDocs site and attach final live evidence to the repository.
