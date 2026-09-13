# K8s AutoGuard Final Project Report

## Executive Summary

K8s AutoGuard is a local Kubernetes DevSecOps lab that combines preventive admission policy, runtime detection, network security, anomaly analysis, guarded remediation, and observable evidence. It is designed as a learning and portfolio project: each control is versioned, reproducible, and linked to a validation command.

## Architecture

```text
GitHub pull request
  -> Kyverno test and Trivy gates
  -> KIND with Cilium and Hubble
  -> Falco runtime event
  -> Falco Sidekick -> AutoGuard event-ingestion API
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
| Runtime detection | Falco modern eBPF and Falco Sidekick | Controlled runtime event, terminal-shell detection, and structured event delivery |
| Admission control | Kyverno Restricted Pod Security policy | Secure fixture admitted, insecure fixture denied |
| Supply chain | Trivy manifest and pinned-image scans | Versioned local and GitHub Actions security gates |
| Detection | Isolation Forest on deterministic scenario data with a real Falco event adapter | 1.00 recall and 0.08 false-positive rate on 520 labelled events; controlled runtime event classified live |
| Response | Guarded dry-run remediation with narrow Cilium RBAC | Tested scoped isolation-policy construction |
| Delivery | Protected `main`, Terraform, Ansible, Argo CD application manifest | Reviewed and merged pull requests; historical local Argo Application verification on 2026-09-11 |
| Observability | Prometheus metrics, Loki, Promtail, Grafana, alerts | Versioned Helm values, dashboard, and live-validation runbook; current-cluster evidence requires a successful rollout |

## Safety Model

Remediation defaults to dry run. A Cilium policy can be created only when the event is anomalous, its baseline-relative anomaly score meets the configured threshold, Falco severity is high or critical, and the namespace is `autoguard-demo`. The score is not a compromise probability. The Kubernetes Role allows only create, get, and list access to CiliumNetworkPolicies in that namespace.

## Verified Results

- Cilium connectivity validation: 77 applicable tests and 320 actions passed.
- Falco detected both a controlled file operation and an interactive container shell.
- A timestamped real Falco event was delivered through Falco Sidekick to the AutoGuard ingestor, classified as an anomaly with a 0.9 baseline-relative score, and produced a scoped dry-run Cilium isolation decision.
- Kyverno admitted a Restricted-profile fixture and denied an insecure fixture.
- Local Python, manifest, and policy validations are repeatable; GitHub Actions results must be checked from the current workflow runs before recording final CI evidence.
- The development benchmark measured 1.00 recall, 0.08 false-positive rate, and 38.69 ms P95 in-process classification latency on synthetic scenario data.
- The observability metric tests, embedded Grafana dashboard JSON, custom resource YAML, and all pinned Helm templates validated locally.

## Limitations and Final Runtime Acceptance

Synthetic benchmark measurements are not production MTTD or MTTR claims. No production data was collected, used for training, or claimed by this project. The real event adapter is deliberately narrow: it uses the observed rule, command, and workload identity to derive shell-execution and process-count features, while unavailable CPU, memory, and network telemetry remains zero. It demonstrates an honest runtime-event contract, not a complete production risk model. The Loki deployment is intentionally disposable and uses the chart test schema for the local lab. Promtail is included because the brief requests it, but should be replaced with Grafana Alloy in a future production-oriented iteration.

The local Argo CD Application was verified `Synced` and `Healthy` on 2026-09-11. This is historical local-lab evidence, not a claim about a newly created cluster or a production delivery environment.

The live KIND acceptance path has passed for Cilium and the Falco-to-remediation workflow. A native Docker Engine reachable from Ubuntu WSL is required to recreate the deployment, run the final demo, record the video, and capture fresh Grafana evidence. Observability should be called demonstrated only after its current-cluster rollout and validator pass. The exact commands are documented in [the observability validation plan](evidence/006-observability-validation.md) and [video runbook](demo/final-project-demo.md).

## Future Work

- Replace Promtail with Grafana Alloy.
- Add authenticated, durable Falco event transport and event storage.
- Enrich runtime events with representative CPU, memory, network, and historical baseline telemetry.
- Train and evaluate against representative non-synthetic events.
- Add approval workflows before activating remediation mode.
- Publish the MkDocs site and attach final live evidence to the repository.
