# ADR 002: Use Cilium and Hubble for Network Security

- Status: Accepted
- Date: 2026-07-20

## Context

The initial KIND baseline used the default CNI. K8s AutoGuard needs identity-aware network policy enforcement and visibility into allowed and denied flows before higher-level detection and remediation components are introduced.

## Decision

- Create KIND with `disableDefaultCNI: true`.
- Pin cluster nodes to Kubernetes v1.34.3.
- Install Cilium v1.19.5 through the OCI Helm chart.
- Use Kubernetes IPAM.
- Enable Hubble Relay and Hubble UI.
- Add a namespaced Cilium policy demo that permits only `trusted-client` to reach `api` on TCP/8080.

## Consequences

Positive:

- The lab has eBPF-based networking, identity-aware policy enforcement, and network observability.
- The policy demo provides a repeatable allowed-versus-denied security test.
- Hubble offers visual evidence for debugging and portfolio demonstrations.

Trade-offs:

- Nodes remain NotReady until Cilium is installed.
- First-time image pulls can extend cluster creation time.
- The current policy is intentionally namespaced; cluster-wide controls come later.
