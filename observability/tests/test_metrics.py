from observability.metrics import AutoGuardMetrics


def test_metrics_render_prediction_and_remediation_signals() -> None:
    metrics = AutoGuardMetrics()

    metrics.record_prediction(is_anomaly=True, risk_score=0.93)
    metrics.record_remediation(action="isolate_workload", mode="dry_run")

    rendered = metrics.render()

    assert 'autoguard_predictions_total{outcome="anomaly"} 1' in rendered
    assert "autoguard_prediction_risk_score 0.93" in rendered
    assert (
        'autoguard_remediation_decisions_total{action="isolate_workload",mode="dry_run"} 1'
        in rendered
    )
