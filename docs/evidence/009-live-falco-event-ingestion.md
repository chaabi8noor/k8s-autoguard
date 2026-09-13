# Live Falco-to-Remediation Validation

- Date: 2026-08-29
- Environment: two-node KIND `k8s-autoguard` lab with Cilium, Falco, Falco Sidekick, the AutoGuard platform, and Prometheus instrumentation

## Trigger

The validator created the `shell-test` workload and ran a unique command through Kubernetes:

```text
touch /tmp/autoguard-runtime-test-20260829T191535Z
```

Falco emitted the `AutoGuard Controlled Runtime Test` alert with the same command, `autoguard-demo` namespace, and `shell-test` pod identity.

## Observed Result

Falco Sidekick forwarded the alert to `autoguard-event-ingestor`. The ingestor stored the resulting live event and returned this guarded response:

```text
source_rule: AutoGuard Controlled Runtime Test
namespace: autoguard-demo
pod: shell-test
command: touch /tmp/autoguard-runtime-test-20260829T191535Z
action: isolate_workload
executed_resource: dry-run:ciliumnetworkpolicy/autoguard-isolate-shell-test-b2613164
risk_score: 0.9
evidence: [shell-execution]
```

The validator then confirmed the forwarded-Falco-event, ML anomaly, and dry-run remediation metrics and completed with:

```text
Real Falco-to-remediation pipeline passed.
```

## Interpretation

This proves an event from the real Falco sensor, rather than a handcrafted API request, reached the model and the guarded response path. The score is not a compromise probability. For this controlled rule, the ingestor derives shell execution and process count from the observed event and sets unavailable CPU, memory, and network telemetry to zero. It is an honest integration test and a useful local demonstration, but not a production-grade telemetry model.
