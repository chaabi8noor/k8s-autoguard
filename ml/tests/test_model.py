import pandas as pd

from ml.model import FEATURE_COLUMNS, classify_event, train_detector


def normal_training_events() -> pd.DataFrame:
    rows = []
    for offset in range(60):
        rows.append(
            {
                "cpu_percent": 18 + offset % 5,
                "memory_percent": 28 + offset % 4,
                "network_connections": 2 + offset % 3,
                "process_count": 5 + offset % 2,
                "shell_exec": 0,
                "sensitive_file_access": 0,
                "denied_egress": 0,
            }
        )
    return pd.DataFrame(rows, columns=FEATURE_COLUMNS)


def test_classifies_an_obvious_runtime_outlier_as_high_risk() -> None:
    detector = train_detector(normal_training_events())

    classification = classify_event(
        detector,
        {
            "cpu_percent": 97,
            "memory_percent": 94,
            "network_connections": 160,
            "process_count": 48,
            "shell_exec": 1,
            "sensitive_file_access": 1,
            "denied_egress": 12,
        },
    )

    assert classification.is_anomaly is True
    assert classification.risk_score >= 0.80
    assert "shell-execution" in classification.evidence
