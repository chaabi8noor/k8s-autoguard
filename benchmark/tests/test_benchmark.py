from pathlib import Path

import benchmark
from benchmark.run_benchmark import run


def test_summarize_predictions_calculates_security_metrics() -> None:
    summary = benchmark.summarize_predictions(
        labels=[0, 0, 1, 1, 1],
        predictions=[0, 1, 1, 1, 0],
        latencies_ms=[5.0, 7.0, 11.0, 13.0, 17.0],
    )

    assert summary["events"] == 5
    assert summary["recall"] == 2 / 3
    assert summary["false_positive_rate"] == 0.5
    assert summary["p95_detection_ms"] == 17.0


def test_run_evaluates_the_saved_scenario_model() -> None:
    summary = run(
        Path("ml/data/security_events.csv"),
        Path("ml/models/isolation_forest_v1.joblib"),
    )

    assert summary["events"] == 520
    assert summary["recall"] >= 0.85
