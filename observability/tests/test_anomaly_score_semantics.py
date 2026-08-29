import json
from pathlib import Path

import yaml

from ml.model import Detector, classify_event
from observability.metrics import AutoGuardMetrics


REPO_ROOT = Path(__file__).parents[2]
DASHBOARD_FILE = REPO_ROOT / "observability" / "dashboards" / "autoguard-security-overview.yaml"


def test_extreme_outlier_is_high_without_claiming_certain_risk() -> None:
    class FixedScorePipeline:
        def score_samples(self, frame):
            return [-3.0]

    detector = Detector(
        pipeline=FixedScorePipeline(),
        risk_floor=0.0,
        risk_ceiling=1.0,
    )

    classification = classify_event(
        detector,
        {
            "cpu_percent": 20,
            "memory_percent": 30,
            "network_connections": 3,
            "process_count": 5,
            "shell_exec": 0,
            "sensitive_file_access": 0,
            "denied_egress": 0,
        },
    )

    assert classification.is_anomaly is True
    assert 0.90 <= classification.risk_score < 1.0


def test_metrics_report_when_the_latest_prediction_was_recorded() -> None:
    metrics = AutoGuardMetrics(clock=lambda: 1_700_000_000.0)

    metrics.record_prediction(is_anomaly=True, risk_score=0.93)

    assert (
        "autoguard_prediction_last_seen_timestamp_seconds 1.7e+09" in metrics.render()
    )


def test_dashboard_labels_the_anomaly_score_and_hides_stale_values() -> None:
    manifest = yaml.safe_load(DASHBOARD_FILE.read_text())
    dashboard = json.loads(manifest["data"]["autoguard-security-overview.json"])
    panel = next(panel for panel in dashboard["panels"] if panel["title"] == "Latest Anomaly Score")

    assert "not a compromise probability" in panel["description"]
    assert panel["targets"] == [
        {
            "expr": (
                "autoguard_prediction_risk_score and on() "
                "(time() - autoguard_prediction_last_seen_timestamp_seconds < 300)"
            ),
            "instant": True,
            "refId": "A",
        }
    ]
