# K8s AutoGuard

K8s AutoGuard is an autonomous DevSecOps platform for detecting, analyzing, and remediating Kubernetes security events.

> Current milestone: Cilium network security and Hubble observability foundation.

## Current Capabilities

- Reproducible two-node KIND lab on Kubernetes v1.34.3
- Cilium v1.19.5 installed through Helm from an OCI registry
- Hubble Relay and Hubble UI enabled for network observability
- A trusted-only Cilium network policy demo with reproducible validation
- Cilium connectivity validation passed: 77 applicable tests and 320 actions

## Architecture

```text
KIND control-plane + worker
  -> Cilium CNI with Kubernetes IPAM
  -> Hubble Relay + Hubble UI
  -> CiliumNetworkPolicy enforcement
  -> trusted-client allowed to call api
  -> untrusted-client denied
```

## Repository Layout

```text
infra/kind/                 KIND cluster configuration
infra/helm/                 Helm values for Cilium
security/cilium-policies/   Demo workloads and Cilium policies
scripts/                    Cluster lifecycle and validation scripts
docs/adr/                   Architecture Decision Records
docs/evidence/              Screenshots and validation evidence
observability/              Future dashboards and alerts
remediation/                Future automated response actions
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

The script creates the KIND cluster, installs Cilium, waits for Cilium and Hubble components, then verifies that all nodes are ready.

Remove the lab when finished:

```bash
./scripts/delete-cluster.sh
```

## Validate Cilium

```bash
cilium status --wait

cilium connectivity test \
  --timeout 20m \
  --hubble=false \
  --log-check-only-test-time
```

Validated result: **77 applicable connectivity tests and 320 actions passed**.

Some checks are skipped because this is a compact local lab with one schedulable worker and intentionally disabled features.

## Run the Policy Demo

```bash
./scripts/validate-cilium-policy-demo.sh
```

The demo verifies access before and after applying the Cilium policy:

| Stage | trusted-client -> api | untrusted-client -> api |
| --- | --- | --- |
| Before policy | Allowed | Allowed |
| After policy | Allowed | Denied |

The `CiliumNetworkPolicy` selects the `api` workload. Once selected, ingress becomes default-deny and only `trusted-client` can reach the API on TCP port `8080`.

Clean up the demo namespace:

```bash
./scripts/validate-cilium-policy-demo.sh --cleanup
```

## Inspect Flows in Hubble

```bash
kubectl -n kube-system port-forward service/hubble-ui 12000:80
```

Open [http://localhost:12000](http://localhost:12000) and select the `autoguard-demo` namespace to inspect allowed and denied traffic.

## Evidence

This milestone includes:

- Cilium connectivity validation: 77 tests and 320 actions passed
- Trusted client successfully reached the API
- Untrusted client timed out after Cilium denied its request
- Hubble visualized the application topology and network decisions

## Decisions

- [ADR 001: KIND baseline](docs/adr/001-kind-baseline.md)
- [ADR 002: Cilium network security](docs/adr/002-cilium-network-security.md)

## Next Steps

- Add Falco runtime threat detection
- Add Kyverno admission policies
- Add Trivy image and manifest scanning
- Add Prometheus, Loki, and Grafana observability
- Build automated remediation workflows
