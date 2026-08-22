import asyncio

import httpx

from remediation.runtime import HttpClassifier, create_runtime_app


def test_http_classifier_maps_the_ml_api_response_to_a_classification() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == httpx.URL("http://ml-api:8000/predict")
        return httpx.Response(
            200,
            json={
                "is_anomaly": True,
                "risk_score": 0.94,
                "model_version": "isolation-forest-v1",
                "evidence": ["shell-execution"],
            },
        )

    classifier = HttpClassifier(
        "http://ml-api:8000/predict",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    classification = classifier.classify({"shell_exec": 1.0})

    assert classification.is_anomaly is True
    assert classification.risk_score == 0.94
    assert classification.evidence == ("shell-execution",)


def test_runtime_app_defaults_to_a_healthy_dry_run_service() -> None:
    async def health() -> httpx.Response:
        transport = httpx.ASGITransport(
            app=create_runtime_app("http://ml-api:8000/predict", execution_mode="dry-run")
        )
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/healthz")

    response = asyncio.run(health())

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
