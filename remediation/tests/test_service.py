from remediation.engine import Action, Classification, SecurityEvent
from remediation.service import RemediationService


class StaticClassifier:
    def classify(self, features: dict[str, float]) -> Classification:
        return Classification(
            is_anomaly=True,
            risk_score=0.94,
            evidence=("shell-execution",),
        )


class RecordingExecutor:
    def __init__(self) -> None:
        self.isolated_events: list[SecurityEvent] = []

    def isolate_workload(self, event: SecurityEvent) -> str:
        self.isolated_events.append(event)
        return "ciliumnetworkpolicy/autoguard-isolate-shell-test-abc123"


def test_executes_an_isolation_after_a_high_confidence_critical_event() -> None:
    executor = RecordingExecutor()
    service = RemediationService(classifier=StaticClassifier(), executor=executor)
    event = SecurityEvent(
        event_id="evt-001",
        rule="Terminal shell in container",
        namespace="autoguard-demo",
        pod="shell-test-abc123",
        container="shell-test",
        severity="Critical",
    )

    result = service.handle(event, {"shell_exec": 1.0})

    assert result.decision.action is Action.ISOLATE_WORKLOAD
    assert result.executed_resource == "ciliumnetworkpolicy/autoguard-isolate-shell-test-abc123"
    assert executor.isolated_events == [event]
