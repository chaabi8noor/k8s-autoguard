"""FastAPI contract for K8s AutoGuard anomaly classification."""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from ml.model import Detector, classify_event


class PredictionRequest(BaseModel):
    cpu_percent: float = Field(ge=0)
    memory_percent: float = Field(ge=0)
    network_connections: float = Field(ge=0)
    process_count: float = Field(ge=0)
    shell_exec: int = Field(ge=0, le=1)
    sensitive_file_access: int = Field(ge=0, le=1)
    denied_egress: float = Field(ge=0)


class PredictionResponse(BaseModel):
    is_anomaly: bool
    risk_score: float
    model_version: str
    evidence: list[str]


def create_app(detector: Detector | None = None) -> FastAPI:
    app = FastAPI(title="K8s AutoGuard ML API", version="1.0.0")
    app.state.detector = detector

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok" if app.state.detector is not None else "model-unavailable"}

    @app.post("/predict", response_model=PredictionResponse)
    def predict(request: PredictionRequest) -> PredictionResponse:
        active_detector = app.state.detector
        if active_detector is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="model is not loaded",
            )

        classification = classify_event(active_detector, request.model_dump())
        return PredictionResponse(
            is_anomaly=classification.is_anomaly,
            risk_score=classification.risk_score,
            model_version=active_detector.version,
            evidence=list(classification.evidence),
        )

    return app


app = create_app()
