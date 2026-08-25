import json

import httpx

from remediation.runtime import HttpClassifier


def test_http_classifier_fills_missing_model_features_with_zero() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert json.loads(request.content) == {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "network_connections": 0.0,
            "process_count": 0.0,
            "shell_exec": 1.0,
            "sensitive_file_access": 0.0,
            "denied_egress": 0.0,
        }
        return httpx.Response(
            200,
            json={
                "is_anomaly": True,
                "risk_score": 1.0,
                "model_version": "isolation-forest-v1",
                "evidence": ["shell-execution"],
            },
        )

    classifier = HttpClassifier("http://ml-api:8000/predict", httpx.Client(transport=httpx.MockTransport(handler)))

    assert classifier.classify({"shell_exec": 1.0}).is_anomaly is True
