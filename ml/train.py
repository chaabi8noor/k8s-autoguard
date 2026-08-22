"""Train and evaluate the K8s AutoGuard Isolation Forest detector."""

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score

from ml.model import FEATURE_COLUMNS, classify_event, save_detector, train_detector


@dataclass(frozen=True)
class TrainingResult:
    normal_training_events: int
    total_evaluation_events: int
    accuracy: float
    precision: float
    recall: float
    false_positive_rate: float
    model_path: str
    report_path: str


def train_and_export(
    dataset_path: Path,
    model_path: Path,
    report_path: Path,
) -> TrainingResult:
    """Train on normal events and evaluate against the full labeled dataset."""

    events = pd.read_csv(dataset_path)
    required_columns = set(FEATURE_COLUMNS) | {"label"}
    missing = required_columns.difference(events.columns)
    if missing:
        raise ValueError(f"dataset is missing required columns: {', '.join(sorted(missing))}")

    normal_events = events.loc[events["label"] == "normal", list(FEATURE_COLUMNS)]
    detector = train_detector(normal_events)
    save_detector(detector, model_path)

    actual = (events["label"] == "anomaly").tolist()
    predicted = [
        classify_event(detector, row).is_anomaly
        for row in events.loc[:, FEATURE_COLUMNS].to_dict(orient="records")
    ]
    normal_event_count = sum(not label for label in actual)
    false_positive_count = sum(
        predicted_label and not actual_label
        for predicted_label, actual_label in zip(predicted, actual, strict=True)
    )
    result = TrainingResult(
        normal_training_events=len(normal_events),
        total_evaluation_events=len(events),
        accuracy=round(float(accuracy_score(actual, predicted)), 4),
        precision=round(float(precision_score(actual, predicted, zero_division=0)), 4),
        recall=round(float(recall_score(actual, predicted, zero_division=0)), 4),
        false_positive_rate=round(false_positive_count / normal_event_count, 4),
        model_path=str(model_path),
        report_path=str(report_path),
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("ml/data/security_events.csv"))
    parser.add_argument("--model", type=Path, default=Path("ml/models/isolation_forest_v1.joblib"))
    parser.add_argument("--report", type=Path, default=Path("ml/models/model_report.json"))
    args = parser.parse_args()

    result = train_and_export(args.dataset, args.model, args.report)
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
