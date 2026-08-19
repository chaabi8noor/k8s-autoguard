from remediation.engine import Action, Classification, RemediationPolicy, SecurityEvent


def security_event(*, namespace: str = "autoguard-demo", severity: str = "Critical") -> SecurityEvent:
    return SecurityEvent(
        event_id="evt-001",
        rule="Terminal shell in container",
        namespace=namespace,
        pod="shell-test-abc123",
        container="shell-test",
        severity=severity,
    )


def test_isolates_an_anomalous_critical_event_in_the_demo_namespace() -> None:
    decision = RemediationPolicy().decide(
        security_event(),
        Classification(is_anomaly=True, risk_score=0.94),
    )

    assert decision.action is Action.ISOLATE_WORKLOAD
    assert decision.execute is True


def test_does_not_remediate_an_event_outside_the_allowed_namespace() -> None:
    decision = RemediationPolicy().decide(
        security_event(namespace="kube-system"),
        Classification(is_anomaly=True, risk_score=0.94),
    )

    assert decision.action is Action.ALERT_ONLY
    assert decision.execute is False


def test_does_not_remediate_a_normal_classification() -> None:
    decision = RemediationPolicy().decide(
        security_event(),
        Classification(is_anomaly=False, risk_score=0.08),
    )

    assert decision.action is Action.ALERT_ONLY
    assert decision.execute is False


def test_does_not_remediate_an_insufficiently_confident_anomaly() -> None:
    decision = RemediationPolicy().decide(
        security_event(),
        Classification(is_anomaly=True, risk_score=0.42),
    )

    assert decision.action is Action.ALERT_ONLY
    assert decision.execute is False
