from pathlib import Path

import pandas as pd

from ml.model import FEATURE_COLUMNS, classify_event, load_detector
from ml.data.generate_dataset import build_dataset
from ml.train import train_and_export


def labelled_events() -> pd.DataFrame:
    normal_rows = [
        {
            "cpu_percent": 18 + index % 5,
            "memory_percent": 28 + index % 4,
            "network_connections": 2 + index % 3,
            "process_count": 5 + index % 2,
            "shell_exec": 0,
            "sensitive_file_access": 0,
            "denied_egress": 0,
            "label": "normal",
            "scenario": "baseline",
        }
        for index in range(60)
    ]
    anomaly_rows = [
        {
            "cpu_percent": 97,
            "memory_percent": 94,
            "network_connections": 160,
            "process_count": 48,
            "shell_exec": 1,
            "sensitive_file_access": 1,
            "denied_egress": 12,
            "label": "anomaly",
            "scenario": "interactive-shell",
        }
    ]
    return pd.DataFrame(normal_rows + anomaly_rows, columns=[*FEATURE_COLUMNS, "label", "scenario"])


def test_trains_exports_and_reloads_a_detector(tmp_path: Path) -> None:
    dataset_path = tmp_path / "events.csv"
    model_path = tmp_path / "model.joblib"
    report_path = tmp_path / "training-report.json"
    labelled_events().to_csv(dataset_path, index=False)

    result = train_and_export(dataset_path, model_path, report_path)
    detector = load_detector(model_path)
    classification = classify_event(
        detector,
        labelled_events().query("label == 'anomaly'").iloc[0].loc[list(FEATURE_COLUMNS)].to_dict(),
    )

    assert result.normal_training_events == 60
    assert model_path.is_file()
    assert report_path.is_file()
    assert classification.is_anomaly is True


def test_meets_the_minimum_synthetic_detection_recall_target(tmp_path: Path) -> None:
    dataset_path = tmp_path / "scenario-events.csv"
    dataset = build_dataset(normal_count=400, anomaly_count=120, seed=42)
    dataset.to_csv(dataset_path, index=False)

    result = train_and_export(
        dataset_path,
        tmp_path / "model.joblib",
        tmp_path / "training-report.json",
    )

    assert result.recall >= 0.85
    assert result.false_positive_rate < 0.10
