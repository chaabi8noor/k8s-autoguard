# Preventive Security Validation Evidence

- Date: 2026-08-15
- Milestone: Kyverno admission control and Trivy scanning

## Kyverno Admission Test

The project installer deployed Kyverno chart `3.8.2` with app version `1.18.2`. All four controllers were ready, and the `autoguard-require-pod-security` `ClusterPolicy` reported `READY: True`.

`./scripts/validate-kyverno-policy-demo.sh` produced these results with API-server dry runs:

- `secure-demo` was admitted.
- `insecure-demo` was denied by the `validate.kyverno.svc-fail` webhook.
- The rejection named the missing Restricted-profile controls: `allowPrivilegeEscalation: false`, dropped Linux capabilities, `runAsNonRoot`, and `seccompProfile`.

## Trivy Configuration Gate

`./scripts/scan-trivy.sh --config` scanned the Kyverno policy and secure fixture with Trivy `0.69.3`:

| Target | High or critical misconfigurations |
| --- | ---: |
| `autoguard-require-pod-security.yaml` | 0 |
| `test-fixtures/secure-pod.yaml` | 0 |

The deliberately insecure fixture is excluded because it exists solely to prove the Kyverno denial path.

## Image Report Delivery

`./scripts/scan-trivy.sh --image <pinned-image>` is the local reporting command for the pinned Cilium curl image. Its initial vulnerability-database download from the external Trivy mirror was too slow to complete during this validation. The pull-request workflow runs the same image scan on a GitHub-hosted runner, where its result becomes part of the review record.

## Reproduce

```bash
./scripts/install-kyverno.sh
./scripts/validate-kyverno-policy-demo.sh
./scripts/scan-trivy.sh --config
./scripts/scan-trivy.sh --image \
  quay.io/cilium/alpine-curl:v1.10.0@sha256:913e8c9f3d960dde03882defa0edd3a919d529c2eb167caa7f54194528bde364
```
