# ADR 009: Ingest Real Falco Runtime Events

- Status: Accepted
- Date: 2026-08-29

## Context

The initial platform demonstration invoked the ML and remediation APIs with shaped test payloads. Those requests verified each API but did not prove that a Falco runtime alert automatically reached the decision path. K8s AutoGuard needs an explicit, observable integration boundary for the portfolio demo.

## Decision

- Enable Falco Sidekick and configure its in-cluster webhook to send critical alerts to `autoguard-event-ingestor`.
- Accept only alerts tagged `autoguard` and require namespace, pod, container, and command identity before processing them.
- Map observed controlled-rule behavior to `shell_exec=1` and `process_count=1`; set telemetry not present in the Falco alert to zero.
- Forward the derived event to the existing ML API and the guarded remediation API.
- Keep remediation in dry-run mode and verify the flow with a timestamped `kubectl exec ... touch` command.

## Consequences

Positive:

- A real kernel-observed runtime action drives the detection, scoring, remediation, metrics, and Grafana evidence path.
- The unique generated command path joins the Falco output to the resulting dry-run remediation decision.
- The ingestor safely ignores unrelated Falco alerts and retries downstream failures without permanently discarding an event.

Trade-offs:

- The first mapper is intentionally narrow. Falco's alert does not provide representative CPU, memory, or network telemetry, so those features are zero.
- The score remains a baseline-relative model output, not a compromise probability or a production risk score.
- The local webhook uses in-cluster HTTP and has no durable event queue or authentication; those belong in a production-oriented follow-up.
