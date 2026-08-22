# ADR 007: Use Guarded Remediation for High-Confidence Events

- Status: Accepted
- Date: 2026-08-22

## Context

The platform needs to move beyond alerting without granting broad cluster privileges to an automated component.

## Decision

- Train an Isolation Forest on baseline event features and enrich its score with high-confidence Falco evidence.
- Keep the remediation API in `dry-run` mode by default.
- Allow active mode to create only a namespaced `CiliumNetworkPolicy` in `autoguard-demo`.
- Require an in-scope namespace, a High or Critical severity, and a risk score of at least `0.80` before isolation is eligible.

## Consequences

The service can demonstrate an autonomous decision path while its Kubernetes permissions remain narrow and its default behavior remains non-destructive. Production rollout would require a human review of the allow-list, severity mapping, and active-mode policy.
