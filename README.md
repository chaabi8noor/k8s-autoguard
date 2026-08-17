# K8s AutoGuard

K8s AutoGuard is an autonomous DevSecOps platform for detecting, analyzing, and remediating Kubernetes security events.

> Current milestone: preventive admission control and supply-chain scanning.

Project repository: [chaabi8noor/k8s-autoguard](https://github.com/chaabi8noor/k8s-autoguard)

## Current Capabilities

- Reproducible two-node KIND lab on Kubernetes v1.34.3
- Cilium v1.19.5 with Hubble for network policy enforcement and flow visibility
- Falco v0.44.1 with modern eBPF runtime detection and structured JSON alerts
- Kyverno v1.18.2 admission control using an enforce-mode Restricted Pod Security policy
- Trivy v0.69.3 local manifest and image scanning through Docker
- GitHub Actions Trivy manifest gate on pull requests and `main` pushes
- Repeatable Cilium, Falco, Kyverno, and Trivy validation scripts

## Architecture

```text
Git push or pull request
  -> Trivy manifest gate + pinned-image vulnerability report
  -> Kubernetes API server
  -> Kyverno admission policy enforcement
  -> Cilium network policy enforcement + Hubble flows
  -> Falco modern-eBPF runtime detection
```

## Repository Layout

```text
infra/kind/                 KIND cluster configuration
infra/helm/                 Helm values for Cilium, Falco, and Kyverno
security/cilium-policies/   Cilium demo workloads and network policies
security/falco-rules/       Safe Falco runtime test workload
security/kyverno-policies/  Admission policy and safe/insecure test fixtures
scripts/                    Cluster lifecycle, validation, and scanning scripts
.github/workflows/          Pull-request security automation
docs/adr/                   Architecture Decision Records
docs/evidence/              Validation evidence
```

## Prerequisites

- Docker Desktop with WSL 2 integration
- `kubectl`
- `kind`
- `helm`
- Cilium CLI

## Create the Lab

```bash
./scripts/create-cluster.sh
```

The lifecycle script creates KIND, installs Cilium and Hubble, installs Falco, then installs Kyverno and the scoped admission policy.

Remove the lab when finished:

```bash
./scripts/delete-cluster.sh
```

## Validate Network and Runtime Security

```bash
./scripts/validate-cilium-policy-demo.sh
./scripts/validate-falco-runtime-demo.sh
```

The Cilium demo proves trusted traffic is allowed while an untrusted client is denied. The Falco demo proves a controlled process execution creates a structured runtime alert.

## Validate Admission Control

```bash
./scripts/validate-kyverno-policy-demo.sh
```

The validator uses API-server dry runs, so it creates no demo Pods. It proves a Pod meeting the Restricted profile is admitted and a Pod without a security context is rejected before scheduling.

Clean up the validation namespace:

```bash
./scripts/validate-kyverno-policy-demo.sh --cleanup
```

## Run Trivy Scans

```bash
./scripts/scan-trivy.sh --config

./scripts/scan-trivy.sh --image \
  quay.io/cilium/alpine-curl:v1.10.0@sha256:913e8c9f3d960dde03882defa0edd3a919d529c2eb167caa7f54194528bde364
```

The manifest scan fails on high or critical misconfigurations. The image scan reports high and critical fixed vulnerabilities without failing the command because this lab does not yet own an application image to remediate.

## Inspect Flows in Hubble

```bash
kubectl -n kube-system port-forward service/hubble-ui 12000:80
```

Open [http://localhost:12000](http://localhost:12000) and select the `autoguard-demo` namespace to inspect allowed and denied traffic.

## Evidence

- Cilium connectivity validation: 77 tests and 320 actions passed
- Hubble visualized allowed and denied application traffic
- Falco detected both a custom controlled command and an interactive container shell
- Kyverno server-side validation admits the secure fixture and rejects the insecure fixture
- Trivy manifest gate passed locally with zero high or critical findings; the GitHub Actions manifest gate and pinned-image report both passed
- [Falco runtime validation evidence](docs/evidence/003-falco-runtime-validation.md)
- [Preventive security validation evidence](docs/evidence/004-preventive-security-validation.md)

## Decisions

- [ADR 001: KIND baseline](docs/adr/001-kind-baseline.md)
- [ADR 002: Cilium network security](docs/adr/002-cilium-network-security.md)
- [ADR 003: Falco runtime detection](docs/adr/003-falco-runtime-detection.md)
- [ADR 004: Kyverno admission control](docs/adr/004-kyverno-admission-control.md)
- [ADR 005: Trivy supply-chain scanning](docs/adr/005-trivy-supply-chain-scanning.md)

## Next Steps

- Add Prometheus, Loki, and Grafana observability
- Build automated remediation workflows
