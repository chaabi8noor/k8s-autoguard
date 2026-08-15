# ADR 005: Use Trivy for Manifest and Image Scanning

- Status: Accepted
- Date: 2026-08-15

## Context

Admission control stops unsafe Kubernetes resources at deployment time, but security findings should be visible earlier in local development and pull requests. The project needs a portable scanner for Kubernetes configuration and container images.

## Decision

- Run Trivy v0.69.3 through a pinned Docker image for local scans.
- Make high and critical manifest misconfigurations a failing local and GitHub Actions gate.
- Exclude the intentionally insecure Kyverno test fixture from that manifest gate.
- Scan the pinned Cilium curl image for high and critical vulnerabilities in reporting mode.
- Run both scans on pull requests and pushes to `main` with `aquasecurity/trivy-action@v0.36.0`, pinned to Trivy v0.69.3.

## Consequences

Positive:

- Developers receive configuration feedback before admission and runtime.
- The scanner does not require a host-level Trivy installation.
- GitHub Actions makes scan results part of the repository review record.

Trade-offs:

- Image findings are reporting-only until the project owns an application image and remediation SLA.
- Scan freshness depends on the Trivy vulnerability database download.
- Test fixtures need explicit exclusion to avoid intentional failures masking real regressions.
