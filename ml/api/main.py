"""FastAPI contract for K8s AutoGuard anomaly classification."""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from ml.model import Detector, classify_event, load_detector


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


def create_runtime_app(model_path: Path | str | None = None) -> FastAPI:
    resolved_path = Path(
        model_path or os.getenv("AUTOGUARD_MODEL_PATH", "ml/models/isolation_forest_v1.joblib")
    )
    detector = load_detector(resolved_path) if resolved_path.is_file() else None
    return create_app(detector)


app = create_runtime_app()
