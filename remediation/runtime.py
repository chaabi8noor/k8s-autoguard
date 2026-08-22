"""Runtime adapters and environment wiring for the remediation service."""

import os
from typing import Mapping

import httpx

from remediation.engine import Classification
from remediation.api import create_app
from remediation.executors import DryRunExecutor, KubernetesCiliumExecutor


class HttpClassifier:
    """Call the separately deployed ML API for a classification."""

    def __init__(self, endpoint: str, client: httpx.Client | None = None) -> None:
        self.endpoint = endpoint
        self.client = client or httpx.Client(timeout=5.0)

    def classify(self, features: Mapping[str, float]) -> Classification:
        response = self.client.post(self.endpoint, json=dict(features))
        response.raise_for_status()
        payload = response.json()
        return Classification(
            is_anomaly=bool(payload["is_anomaly"]),
            risk_score=float(payload["risk_score"]),
            evidence=tuple(payload.get("evidence", [])),
        )


def _executor_for_mode(execution_mode: str):
    if execution_mode == "dry-run":
        return DryRunExecutor()
    if execution_mode == "active":
        from kubernetes import client, config

        config.load_incluster_config()
        return KubernetesCiliumExecutor(client.CustomObjectsApi())
    raise ValueError("AUTOGUARD_EXECUTION_MODE must be 'dry-run' or 'active'")


def create_runtime_app(
    ml_api_url: str | None = None,
    execution_mode: str | None = None,
):
    """Build the service from explicit settings or deployment environment values."""

    return create_app(
        HttpClassifier(ml_api_url or os.getenv("AUTOGUARD_ML_API_URL", "http://autoguard-ml-api:8000/predict")),
        _executor_for_mode(execution_mode or os.getenv("AUTOGUARD_EXECUTION_MODE", "dry-run")),
    )


app = create_runtime_app()
