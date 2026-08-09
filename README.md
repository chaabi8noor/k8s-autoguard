# K8s AutoGuard

K8s AutoGuard is an autonomous DevSecOps platform for detecting, analyzing, and remediating Kubernetes security events.

> Current milestone: Falco runtime threat detection on a Cilium-protected local Kubernetes lab.

Project repository: [chaabi8noor/k8s-autoguard](https://github.com/chaabi8noor/k8s-autoguard)

## Current Capabilities

- Reproducible two-node KIND lab on Kubernetes v1.34.3
- Cilium v1.19.5 installed through Helm from an OCI registry
- Hubble Relay and Hubble UI enabled for network observability
- A trusted-only Cilium network policy demo with reproducible validation
- Cilium connectivity validation passed: 77 applicable tests and 320 actions
- Falco v0.44.1 deployed by Helm chart v9.1.0 as a DaemonSet on both KIND nodes
- Modern eBPF runtime monitoring running with the chart's least-privileged mode
- JSON runtime events and a Helm-managed AutoGuard custom detection rule

## Architecture

```text
KIND control-plane + worker
  -> Cilium CNI with Kubernetes IPAM
  -> Hubble Relay + Hubble UI
  -> CiliumNetworkPolicy enforcement
  -> Falco DaemonSet with modern eBPF
  -> JSON runtime alerts and AutoGuard custom rules
```

## Repository Layout

```text
infra/kind/                 KIND cluster configuration
infra/helm/                 Helm values for Cilium and Falco
security/cilium-policies/   Demo workloads and Cilium policies
security/falco-rules/       Safe Falco runtime test workload
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

The script creates the KIND cluster, installs Cilium and Hubble, waits for nodes to become ready, then installs Falco on every node.

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

## Run the Network Policy Demo

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

## Validate Falco Runtime Detection

```bash
./scripts/validate-falco-runtime-demo.sh
```

The script starts a safe test Pod, runs a uniquely marked `touch` command, then waits for Falco to emit the `AutoGuard Controlled Runtime Test` JSON alert. The marker makes each run independently verifiable.

To demonstrate Falco's built-in terminal-shell rule manually:

```bash
kubectl -n falco-demo exec -it shell-test -- sh
```

At the container prompt, run `exit`, then retrieve the alert:

```bash

kubectl -n falco logs \
  -l app.kubernetes.io/name=falco \
  -c falco \
  --since=2m \
  --prefix=true | \
  grep -F 'Terminal shell in container'
```

This detects an interactive shell in a container. It is a runtime signal to investigate, not proof that every `kubectl exec` action is malicious.

Clean up the Falco demo namespace:

```bash
./scripts/validate-falco-runtime-demo.sh --cleanup
```

## Inspect Flows in Hubble

```bash
kubectl -n kube-system port-forward service/hubble-ui 12000:80
```

Open [http://localhost:12000](http://localhost:12000) and select the `autoguard-demo` namespace to inspect allowed and denied traffic.

## Evidence

This milestone includes:

- Cilium connectivity validation: 77 tests and 320 actions passed
- Trusted client successfully reached the API while an untrusted client timed out after policy enforcement
- Hubble visualized application traffic in `autoguard-demo`
- Falco v0.44.1 loaded its modern BPF probe on both KIND nodes
- A controlled terminal shell generated Falco's built-in `Terminal shell in container` event
- The validation script generated and found the `AutoGuard Controlled Runtime Test` JSON alert
- [Falco runtime validation evidence](docs/evidence/003-falco-runtime-validation.md)

## Decisions

- [ADR 001: KIND baseline](docs/adr/001-kind-baseline.md)
- [ADR 002: Cilium network security](docs/adr/002-cilium-network-security.md)
- [ADR 003: Falco runtime detection](docs/adr/003-falco-runtime-detection.md)

## Next Steps

- Add Kyverno admission policies
- Add Trivy image and manifest scanning
- Add Prometheus, Loki, and Grafana observability
- Build automated remediation workflows
