import asyncio

import httpx
import pytest

from ingestion.api import AUTOGUARD_CONTROLLED_RULE, FalcoAlert, FalcoEventIngestor, create_app
from observability.metrics import AutoGuardMetrics


REAL_FALCO_ALERT = {
    "hostname": "k8s-autoguard-worker",
    "output": (
        "AutoGuard controlled runtime test command executed "
        "(user=root command=touch /tmp/autoguard-runtime-test-20260829T175218Z "
        "container=shell-test image=quay.io/cilium/alpine-curl)"
    ),
    "output_fields": {
        "container.id": "9d44e57c6816",
        "container.image.repository": "quay.io/cilium/alpine-curl",
        "container.name": "shell-test",
        "evt.time.iso8601": 1788025877659581048,
        "k8s.ns.name": "autoguard-demo",
        "k8s.pod.name": "shell-test",
        "proc.cmdline": "touch /tmp/autoguard-runtime-test-20260829T175218Z",
        "user.name": "root",
    },
    "priority": "Critical",
    "rule": AUTOGUARD_CONTROLLED_RULE,
    "source": "syscall",
    "tags": ["autoguard", "container", "process"],
    "time": "2026-08-29T17:51:17.659581048Z",
}


class RecordingRemediationClient:
    def __init__(self) -> None:
        self.calls: list[tuple[dict[str, object], dict[str, float]]] = []

    def handle(self, event: dict[str, object], features: dict[str, float]) -> dict[str, object]:
        self.calls.append((event, features))
        return {
            "action": "isolate_workload",
            "execute": True,
            "executed_resource": "dry-run:ciliumnetworkpolicy/autoguard-isolate-shell-test",
            "reason": "high-confidence high-severity anomaly in the allowed demo namespace",
            "is_anomaly": True,
            "risk_score": 0.9,
            "evidence": ["shell-execution"],
        }


def test_forwards_a_real_falco_alert_using_derived_runtime_features() -> None:
    client = RecordingRemediationClient()

    async def submit() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app(client))
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            return await http_client.post("/falco-events", json=REAL_FALCO_ALERT)

    response = asyncio.run(submit())

    assert response.status_code == 202
    assert response.json()["status"] == "forwarded"
    assert response.json()["event"]["namespace"] == "autoguard-demo"
    assert response.json()["event"]["severity"] == "Critical"
    assert response.json()["remediation"]["action"] == "isolate_workload"
    assert response.json()["remediation"]["executed_resource"].startswith("dry-run:")

    event, features = client.calls[0]
    assert event["rule"] == AUTOGUARD_CONTROLLED_RULE
    assert event["pod"] == "shell-test"
    assert event["container"] == "shell-test"
    assert event["severity"] == "Critical"
    assert str(event["event_id"]).startswith("falco-")
    assert features == {
        "cpu_percent": 0.0,
        "memory_percent": 0.0,
        "network_connections": 0.0,
        "process_count": 1.0,
        "shell_exec": 1.0,
        "sensitive_file_access": 0.0,
        "denied_egress": 0.0,
    }


def test_ignores_an_incomplete_cross_node_falco_alert_without_forwarding() -> None:
    client = RecordingRemediationClient()
    incomplete_alert = {
        **REAL_FALCO_ALERT,
        "output_fields": {
            **REAL_FALCO_ALERT["output_fields"],
            "container.name": None,
            "k8s.ns.name": None,
            "k8s.pod.name": None,
        },
    }

    async def submit() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app(client))
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            return await http_client.post("/falco-events", json=incomplete_alert)

    response = asyncio.run(submit())

    assert response.status_code == 202
    assert response.json() == {
        "status": "ignored",
        "reason": "missing-kubernetes-workload-identity",
    }
    assert client.calls == []


def test_latest_event_and_metrics_are_available_after_a_forwarded_alert() -> None:
    client = RecordingRemediationClient()

    async def exercise_api() -> tuple[httpx.Response, httpx.Response, httpx.Response]:
        transport = httpx.ASGITransport(app=create_app(client))
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            accepted = await http_client.post("/falco-events", json=REAL_FALCO_ALERT)
            latest = await http_client.get("/events/latest")
            metrics = await http_client.get("/metrics")
            return accepted, latest, metrics

    accepted, latest, metrics = asyncio.run(exercise_api())

    assert latest.status_code == 200
    assert latest.json()["event_id"] == accepted.json()["event"]["event_id"]
    assert latest.json()["source_rule"] == AUTOGUARD_CONTROLLED_RULE
    assert 'autoguard_falco_events_total{outcome="forwarded"} 1' in metrics.text


def test_a_failed_downstream_call_does_not_mark_the_falco_event_as_processed() -> None:
    class FlakyRemediationClient(RecordingRemediationClient):
        def __init__(self) -> None:
            super().__init__()
            self.attempts = 0

        def handle(self, event: dict[str, object], features: dict[str, float]) -> dict[str, object]:
            self.attempts += 1
            if self.attempts == 1:
                raise httpx.ReadTimeout("temporary downstream delay")
            return super().handle(event, features)

    client = FlakyRemediationClient()
    ingestor = FalcoEventIngestor(client, AutoGuardMetrics())
    alert = FalcoAlert.model_validate(REAL_FALCO_ALERT)

    with pytest.raises(httpx.ReadTimeout):
        ingestor.handle(alert)

    result = ingestor.handle(alert)

    assert client.attempts == 2
    assert result["status"] == "forwarded"
