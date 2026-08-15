# ADR 004: Use Kyverno for Namespace-Scoped Admission Control

- Status: Accepted
- Date: 2026-08-15

## Context

Cilium controls network communication and Falco detects behavior after a container starts. K8s AutoGuard also needs a preventive control that evaluates workload configuration before the Kubernetes API server admits it.

## Decision

- Install Kyverno with Helm chart v3.8.2 and Kyverno app v1.18.2 in its own `kyverno` namespace.
- Use one replica for each Kyverno controller to fit the two-node local lab.
- Apply an `Enforce` mode `ClusterPolicy` named `autoguard-require-pod-security`.
- Use Kyverno's Kubernetes Restricted Pod Security profile, scoped initially to `autoguard-policy-demo`.
- Disable the Helm CRD migration Job because a newly created KIND lab has no legacy Kyverno resources to migrate.
- Validate admission with a server-side dry run: a secure Pod is admitted and an insecure Pod is denied.

## Consequences

Positive:

- Noncompliant Pods are rejected before they can run.
- The policy uses an upstream Pod Security Standard instead of a brittle collection of local field checks.
- The namespace scope gives a low-risk path to test and tune enforcement.

Trade-offs:

- The policy does not protect existing project namespaces yet.
- Production rollout needs staged Audit-to-Enforce adoption and exception governance.
- Admission availability now depends on Kyverno's control-plane components.
