import asyncio

import httpx

from remediation.api import create_app
from remediation.engine import Classification
from remediation.executors import DryRunExecutor


class StaticClassifier:
    def classify(self, features: dict[str, float]) -> Classification:
        return Classification(
            is_anomaly=True,
            risk_score=0.94,
            evidence=("shell-execution",),
        )


def test_event_endpoint_returns_an_explainable_dry_run_isolation() -> None:
    async def submit_event() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app(StaticClassifier(), DryRunExecutor()))
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/events",
                json={
                    "event": {
                        "event_id": "evt-100",
                        "rule": "Terminal shell in container",
                        "namespace": "autoguard-demo",
                        "pod": "shell-test-abc123",
                        "container": "shell-test",
                        "severity": "Critical",
                    },
                    "features": {"shell_exec": 1.0},
                },
            )

    response = asyncio.run(submit_event())

    assert response.status_code == 200
    assert response.json()["action"] == "isolate_workload"
    assert response.json()["execute"] is True
    assert response.json()["executed_resource"].startswith("dry-run:ciliumnetworkpolicy/")
    assert response.json()["evidence"] == ["shell-execution"]


def test_metrics_reports_remediation_decision() -> None:
    async def exercise_metrics() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app(StaticClassifier(), DryRunExecutor()))
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            await client.post(
                "/events",
                json={
                    "event": {
                        "event_id": "evt-101",
                        "rule": "Terminal shell in container",
                        "namespace": "autoguard-demo",
                        "pod": "shell-test-abc123",
                        "container": "shell-test",
                        "severity": "Critical",
                    },
                    "features": {"shell_exec": 1.0},
                },
            )
            return await client.get("/metrics")

    response = asyncio.run(exercise_metrics())

    assert response.status_code == 200
    assert (
        'autoguard_remediation_decisions_total{action="isolate_workload",mode="dry_run"} 1'
        in response.text
    )
