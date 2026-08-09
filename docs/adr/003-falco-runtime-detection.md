# ADR 003: Use Falco with Modern eBPF for Runtime Detection

- Status: Accepted
- Date: 2026-08-09

## Context

Cilium provides network-level enforcement and flow visibility, but it cannot explain suspicious process activity after a workload starts. K8s AutoGuard needs a node-level runtime sensor that can observe container process execution and produce machine-readable security events.

## Decision

- Install Falco with Helm chart v9.1.0 and pin the Falco image to v0.44.1.
- Run Falco as a DaemonSet so every KIND node has a runtime sensor.
- Use Falco's modern eBPF driver with `leastPrivileged: true`.
- Emit ISO 8601 JSON events with output fields and tags for later routing and analysis.
- Keep the container plugin managed by the chart and set `falco.config_files: []` to avoid loading the image's duplicate container-plugin fragment.
- Store the AutoGuard controlled-runtime-test rule in Helm `customRules` so the release owns rule deployment.
- Disable Falcosidekick and Falco Talon in this milestone; external alert delivery and automated response are later work.

## Consequences

Positive:

- The lab detects runtime process execution on both nodes without kernel-module compilation.
- The custom rule has a repeatable, non-interactive validation path that produces structured evidence.
- Pinning the chart and image keeps a local lab rebuild predictable.

Trade-offs:

- Falco alerts are currently written only to Pod logs; routing and retention need an observability milestone.
- The custom rule is intentionally narrow and demonstrates the rule lifecycle, not production threat coverage.
- Modern eBPF availability still depends on the host kernel and container runtime environment.
