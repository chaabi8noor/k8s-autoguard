"""Run a repeatable local benchmark of the AutoGuard anomaly detector."""

import argparse
import json
from pathlib import Path
from time import perf_counter

import pandas as pd

from ml.model import FEATURE_COLUMNS, classify_event, load_detector
from benchmark.metrics import summarize_predictions


def run(dataset_path: Path, model_path: Path) -> dict[str, float | int]:
    dataset = pd.read_csv(dataset_path)
    detector = load_detector(model_path)
    labels: list[int] = []
    predictions: list[int] = []
    latencies_ms: list[float] = []

    for _, row in dataset.iterrows():
        started = perf_counter()
        classification = classify_event(detector, row[list(FEATURE_COLUMNS)].to_dict())
        latencies_ms.append((perf_counter() - started) * 1000)
        labels.append(int(row["label"] != "normal"))
        predictions.append(int(classification.is_anomaly))

    return summarize_predictions(labels, predictions, latencies_ms)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("ml/data/security_events.csv"))
    parser.add_argument("--model", type=Path, default=Path("ml/models/isolation_forest_v1.joblib"))
    parser.add_argument("--output", type=Path, default=Path("benchmark/results/model-benchmark.json"))
    args = parser.parse_args()

    summary = run(args.dataset, args.model)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
