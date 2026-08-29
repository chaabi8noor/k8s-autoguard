"""Translate authenticated-in-cluster Falco alerts into guarded API requests."""

from hashlib import sha256
from threading import Lock
from typing import Any, Protocol

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field

from observability.metrics import AutoGuardMetrics, PROMETHEUS_CONTENT_TYPE


AUTOGUARD_CONTROLLED_RULE = "AutoGuard Controlled Runtime Test"


class RemediationClient(Protocol):
    """Submit one normalized security event to the guarded remediation API."""

    def handle(
        self, event: dict[str, object], features: dict[str, float]
    ) -> dict[str, object]: ...


class FalcoAlert(BaseModel):
    """The JSON alert contract emitted by Falco and forwarded by Falco Sidekick."""

    model_config = ConfigDict(extra="ignore")

    output: str = ""
    output_fields: dict[str, Any] = Field(default_factory=dict)
    priority: str
    rule: str
    source: str
    tags: list[str] = Field(default_factory=list)
    time: str


def _field(alert: FalcoAlert, name: str) -> str | None:
    value = alert.output_fields.get(name)
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _event_id(alert: FalcoAlert, namespace: str, pod: str, command: str) -> str:
    identity = "\x00".join((alert.time, alert.rule, namespace, pod, command))
    return f"falco-{sha256(identity.encode('utf-8')).hexdigest()[:16]}"


def _runtime_features(alert: FalcoAlert) -> dict[str, float]:
    """Derive only signals that are evidenced by this deterministic Falco rule."""

    return {
        "cpu_percent": 0.0,
        "memory_percent": 0.0,
        "network_connections": 0.0,
        "process_count": 1.0,
        "shell_exec": 1.0 if alert.rule == AUTOGUARD_CONTROLLED_RULE else 0.0,
        "sensitive_file_access": 0.0,
        "denied_egress": 0.0,
    }


class FalcoEventIngestor:
    """Validate runtime identity before requesting a policy-governed response."""

    def __init__(self, remediation_client: RemediationClient, metrics: AutoGuardMetrics) -> None:
        self._remediation_client = remediation_client
        self._metrics = metrics
        self._lock = Lock()
        self._latest_event: dict[str, object] | None = None
        self._processed_event_ids: set[str] = set()
        self._in_progress_event_ids: set[str] = set()

    def handle(self, alert: FalcoAlert) -> dict[str, object]:
        if alert.rule != AUTOGUARD_CONTROLLED_RULE or "autoguard" not in alert.tags:
            self._metrics.record_falco_event(outcome="ignored")
            return {"status": "ignored", "reason": "unsupported-autoguard-rule"}

        namespace = _field(alert, "k8s.ns.name")
        pod = _field(alert, "k8s.pod.name")
        container = _field(alert, "container.name")
        command = _field(alert, "proc.cmdline")
        if not all((namespace, pod, container, command)):
            self._metrics.record_falco_event(outcome="ignored")
            return {"status": "ignored", "reason": "missing-kubernetes-workload-identity"}

        event = {
            "event_id": _event_id(alert, namespace, pod, command),
            "rule": alert.rule,
            "namespace": namespace,
            "pod": pod,
            "container": container,
            "severity": alert.priority.title(),
        }
        with self._lock:
            if event["event_id"] in self._processed_event_ids:
                self._metrics.record_falco_event(outcome="duplicate")
                return {"status": "ignored", "reason": "duplicate-event"}
            if event["event_id"] in self._in_progress_event_ids:
                return {"status": "ignored", "reason": "event-processing"}
            self._in_progress_event_ids.add(event["event_id"])

        try:
            remediation = self._remediation_client.handle(event, _runtime_features(alert))
        except Exception:
            with self._lock:
                self._in_progress_event_ids.discard(event["event_id"])
            raise

        result = {
            "status": "forwarded",
            "event": event,
            "command": command,
            "remediation": remediation,
        }
        latest_event = {
            "event_id": event["event_id"],
            "source_rule": alert.rule,
            "namespace": namespace,
            "pod": pod,
            "command": command,
            "remediation": remediation,
        }
        with self._lock:
            self._in_progress_event_ids.discard(event["event_id"])
            self._processed_event_ids.add(event["event_id"])
            self._latest_event = latest_event
        self._metrics.record_falco_event(outcome="forwarded")
        return result

    def latest_event(self) -> dict[str, object] | None:
        with self._lock:
            return self._latest_event


def create_app(remediation_client: RemediationClient) -> FastAPI:
    """Create the in-cluster Falco webhook receiver."""

    app = FastAPI(title="K8s AutoGuard Falco Event Ingestor", version="1.0.0")
    app.state.metrics = AutoGuardMetrics()
    app.state.ingestor = FalcoEventIngestor(remediation_client, app.state.metrics)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return Response(
            content=app.state.metrics.render(),
            media_type=PROMETHEUS_CONTENT_TYPE,
        )

    @app.post("/falco-events", status_code=status.HTTP_202_ACCEPTED)
    def ingest(alert: FalcoAlert) -> dict[str, object]:
        return app.state.ingestor.handle(alert)

    @app.get("/events/latest")
    def latest_event() -> dict[str, object]:
        latest = app.state.ingestor.latest_event()
        if latest is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no forwarded events")
        return latest

    return app
