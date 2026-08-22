# ADR 006: Declare the Lab and Application Delivery

- Status: Accepted
- Date: 2026-08-22

## Context

The lab had reproducible shell scripts but no declarative infrastructure entry point or GitOps application definition.

## Decision

- Use Terraform with the `tehcyx/kind` provider to declare the two-node, Cilium-ready KIND cluster.
- Use Ansible as the local orchestration layer for environment checks and the established security component installers.
- Use an Argo CD Application that watches `main` and automatically reconciles `deployments/autoguard-platform`.

## Consequences

Cluster changes remain explicit because KIND configuration changes recreate the cluster. Application resources can be reconciled from Git after a reviewed pull request merges to `main`.
