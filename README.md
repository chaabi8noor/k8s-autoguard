# K8s AutoGuard

K8s AutoGuard is a local DevSecOps platform for detecting, analyzing, and safely remediating Kubernetes security events.

Project repository: [chaabi8noor/k8s-autoguard](https://github.com/chaabi8noor/k8s-autoguard)

## What It Demonstrates

- A reproducible Cilium-ready two-node KIND lab on Kubernetes v1.34.3
- Cilium and Hubble for identity-aware policy enforcement and flow visibility
- Falco modern eBPF runtime detection with structured JSON events
- Kyverno Restricted Pod Security admission enforcement and Trivy supply-chain gates
- A deterministic security-event dataset, Isolation Forest anomaly detector, and FastAPI inference API
- A guarded remediation API that defaults to dry run and can create Cilium isolation policies only in `autoguard-demo`
- Prometheus service metrics, Loki log aggregation, Grafana dashboard provisioning, and scoped security alerts
- Terraform, Ansible, and Argo CD definitions for declarative infrastructure and post-review delivery

## Architecture

```text
Git push or pull request
  -> Trivy manifest and image security gates
  -> Kubernetes API + Kyverno admission enforcement
  -> Cilium policies + Hubble network evidence
  -> Falco runtime detection
  -> normalized event + ML anomaly classification
  -> guarded remediation decision
  -> Prometheus metrics + Loki logs + Grafana security overview
  -> optional, scoped Cilium workload isolation
```

## Repository Layout

```text
infra/kind/                 KIND cluster configuration
infra/terraform/            Terraform declaration for the Cilium-ready lab
infra/ansible/              Local bootstrap orchestration
infra/helm/                 Helm values for Cilium, Falco, and Kyverno
observability/              Prometheus rules, ServiceMonitors, and Grafana dashboard
deployments/                ML and remediation Kubernetes workloads
gitops/                     Argo CD Application definitions
security/                   Cilium, Falco, and Kyverno policies
ml/                         Dataset generator, model, training, and inference API
benchmark/                  Reproducible scenario-model benchmark
scripts/                    Lifecycle, installation, validation, and scanning scripts
docs/                       ADRs, evidence, and demo material
```

## Prerequisites

- Docker Desktop with Ubuntu WSL 2 integration
- `kubectl`, `kind`, `helm`, Terraform, Ansible, and the Cilium CLI
- Python 3.12 for model training and benchmarking

## Quick Start

```bash
./scripts/create-cluster.sh
./scripts/validate-cilium-policy-demo.sh
./scripts/validate-falco-runtime-demo.sh
./scripts/validate-kyverno-policy-demo.sh
./scripts/scan-trivy.sh --config
```

`create-cluster.sh` creates KIND, then installs Cilium/Hubble, Falco, Kyverno, and the scoped admission policy. Each validation script exercises one control with an expected security outcome.

## Application Platform

```bash
./scripts/deploy-autoguard-platform.sh
./scripts/install-observability.sh
```

This builds the pinned-base Python image, loads it directly into KIND, and deploys the ML inference and remediation APIs. Remediation starts in `dry-run` mode. Its active mode is guarded by namespace, severity, risk threshold, and narrow Kubernetes RBAC.

## Observability

```bash
./scripts/install-observability.sh
./scripts/run-final-project-demo.sh --interactive
```

The local stack uses Prometheus, Alertmanager, Loki, Promtail, and Grafana. The dashboard tracks predictions, latest risk, remediation mode, and platform logs. It is intentionally a local-lab deployment with 24-hour metric retention and disposable Loki storage.

## Model Benchmark

```bash
.venv/bin/python -m benchmark.run_benchmark
```

The latest deterministic development benchmark processed **520 labelled scenario events** with **1.00 recall**, **0.08 false-positive rate**, and **38.69 ms P95 in-process classification latency**. These are synthetic-scenario, in-process metrics; they are not production MTTD or MTTR claims.

## Infrastructure and GitOps

```bash
terraform -chdir=infra/terraform init
terraform -chdir=infra/terraform apply

ansible-playbook -i infra/ansible/inventory.ini infra/ansible/site.yaml

./scripts/install-argocd.sh
```

Terraform declares the Cilium-ready KIND topology. Ansible orchestrates the established local installers. Argo CD reconciles `deployments/autoguard-platform` from `main` only after reviewed changes merge.

## Evidence

- Cilium connectivity validation: 77 tests and 320 actions passed
- Cilium policy demo: trusted client allowed, untrusted client denied
- Falco detected a controlled command and an interactive container shell
- Kyverno admits the secure fixture and rejects the insecure fixture before scheduling
- Trivy manifest gate passed with zero high or critical findings
- [Falco runtime validation](docs/evidence/003-falco-runtime-validation.md)
- [Preventive security validation](docs/evidence/004-preventive-security-validation.md)
- [Model benchmark](docs/evidence/005-model-benchmark.md)
- [Observability validation plan](docs/evidence/006-observability-validation.md)
- [Final video demo runbook](docs/demo/final-project-demo.md)
- [Final project report](docs/final-report.md)
- [Final project report PDF](output/pdf/k8s-autoguard-final-report.pdf)

## Decisions

- [ADR 001: KIND baseline](docs/adr/001-kind-baseline.md)
- [ADR 002: Cilium network security](docs/adr/002-cilium-network-security.md)
- [ADR 003: Falco runtime detection](docs/adr/003-falco-runtime-detection.md)
- [ADR 004: Kyverno admission control](docs/adr/004-kyverno-admission-control.md)
- [ADR 005: Trivy supply-chain scanning](docs/adr/005-trivy-supply-chain-scanning.md)
- [ADR 006: GitOps and IaC](docs/adr/006-gitops-and-iac.md)
- [ADR 007: Guarded anomaly remediation](docs/adr/007-guarded-anomaly-remediation.md)
- [ADR 008: Local observability stack](docs/adr/008-local-observability-stack.md)

## Current Operational Status

The code, policies, IaC, and benchmark are versioned and locally validated. Docker Desktop WSL integration must be enabled before rerunning live deployment, Argo CD installation, and end-to-end cluster evidence collection.
