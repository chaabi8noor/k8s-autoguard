import asyncio
from pathlib import Path

import httpx
import pandas as pd

from ml.api import main
from ml.api.main import create_app
from ml.model import FEATURE_COLUMNS, save_detector, train_detector


def detector_for_test():
    rows = [
        {
            "cpu_percent": 18 + index % 5,
            "memory_percent": 28 + index % 4,
            "network_connections": 2 + index % 3,
            "process_count": 5 + index % 2,
            "shell_exec": 0,
            "sensitive_file_access": 0,
            "denied_egress": 0,
        }
        for index in range(60)
    ]
    return train_detector(pd.DataFrame(rows, columns=FEATURE_COLUMNS))


def test_predict_returns_a_high_risk_anomaly_for_a_runtime_outlier() -> None:
    async def predict() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app(detector_for_test()))
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/predict",
                json={
                    "cpu_percent": 97,
                    "memory_percent": 94,
                    "network_connections": 160,
                    "process_count": 48,
                    "shell_exec": 1,
                    "sensitive_file_access": 1,
                    "denied_egress": 12,
                },
            )

    response = asyncio.run(predict())

    assert response.status_code == 200
    assert response.json()["is_anomaly"] is True
    assert response.json()["risk_score"] >= 0.80
    assert response.json()["model_version"] == "isolation-forest-v1"
    assert "shell-execution" in response.json()["evidence"]


def test_runtime_app_loads_a_saved_detector(tmp_path: Path) -> None:
    model_path = tmp_path / "detector.joblib"
    save_detector(detector_for_test(), model_path)

    async def exercise_runtime_app() -> tuple[httpx.Response, httpx.Response]:
        transport = httpx.ASGITransport(app=main.create_runtime_app(model_path))
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            health = await client.get("/healthz")
            prediction = await client.post(
                "/predict",
                json={
                    "cpu_percent": 97,
                    "memory_percent": 94,
                    "network_connections": 160,
                    "process_count": 48,
                    "shell_exec": 1,
                    "sensitive_file_access": 1,
                    "denied_egress": 12,
                },
            )
            return health, prediction

    health, prediction = asyncio.run(exercise_runtime_app())

    assert health.json() == {"status": "ok"}
    assert prediction.status_code == 200
    assert prediction.json()["is_anomaly"] is True
