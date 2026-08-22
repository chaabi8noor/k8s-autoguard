"""HTTP endpoint for normalized security events and guarded responses."""

from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel

from observability.metrics import AutoGuardMetrics, PROMETHEUS_CONTENT_TYPE
from remediation.engine import SecurityEvent
from remediation.service import Classifier, RemediationExecutor, RemediationService


class EventPayload(BaseModel):
    event_id: str
    rule: str
    namespace: str
    pod: str
    container: str
    severity: str


class RemediationRequest(BaseModel):
    event: EventPayload
    features: dict[str, float]


class RemediationResponse(BaseModel):
    action: str
    execute: bool
    executed_resource: str | None
    reason: str
    is_anomaly: bool
    risk_score: float
    evidence: list[str]


def create_app(classifier: Classifier, executor: RemediationExecutor) -> FastAPI:
    app = FastAPI(title="K8s AutoGuard Remediation API", version="1.0.0")
    service = RemediationService(classifier=classifier, executor=executor)
    app.state.metrics = AutoGuardMetrics()

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return Response(
            content=app.state.metrics.render(),
            media_type=PROMETHEUS_CONTENT_TYPE,
        )

    @app.post("/events", response_model=RemediationResponse)
    def handle_event(request: RemediationRequest) -> RemediationResponse:
        event = SecurityEvent(**request.event.model_dump())
        result = service.handle(event, request.features)
        mode = "not_applied"
        if result.executed_resource is not None:
            mode = "dry_run" if result.executed_resource.startswith("dry-run:") else "executed"
        app.state.metrics.record_remediation(
            action=result.decision.action.value,
            mode=mode,
        )
        return RemediationResponse(
            action=result.decision.action.value,
            execute=result.decision.execute,
            executed_resource=result.executed_resource,
            reason=result.decision.reason,
            is_anomaly=result.classification.is_anomaly,
            risk_score=result.classification.risk_score,
            evidence=list(result.classification.evidence),
        )

    return app
