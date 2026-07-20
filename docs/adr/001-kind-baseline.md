# ADR 001: Start with a default-CNI KIND baseline

- Status: Accepted
- Date: 2026-07-14

## Context

K8s AutoGuard needs a reproducible local Kubernetes platform before security, observability, and AI components are introduced.

## Decision

Use a two-node KIND cluster with KIND's default CNI for the initial infrastructure baseline. Add Cilium in a separate iteration after the base cluster lifecycle is verified.

## Consequences

The project has a fast, reproducible local lab and a clear baseline for future measurements. Introducing Cilium will require recreating the cluster with CNI-specific configuration.
