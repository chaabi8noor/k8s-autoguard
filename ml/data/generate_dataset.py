"""Create a labeled, scenario-derived dataset for the local demo model."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ml.model import FEATURE_COLUMNS


SCENARIOS = (
    "interactive-shell",
    "sensitive-file-read",
    "network-scan",
    "resource-abuse",
)


def _normal_row(rng: np.random.Generator) -> dict[str, float | int | str]:
    return {
        "cpu_percent": round(float(np.clip(rng.normal(20, 3), 5, 45)), 2),
        "memory_percent": round(float(np.clip(rng.normal(30, 4), 10, 55)), 2),
        "network_connections": int(rng.integers(1, 6)),
        "process_count": int(rng.integers(4, 8)),
        "shell_exec": 0,
        "sensitive_file_access": 0,
        "denied_egress": 0,
        "label": "normal",
        "scenario": "baseline",
    }


def _anomaly_row(rng: np.random.Generator, scenario: str) -> dict[str, float | int | str]:
    row = _normal_row(rng)
    row.update({"label": "anomaly", "scenario": scenario})
    if scenario == "interactive-shell":
        row.update({"cpu_percent": 78.0, "process_count": 22, "shell_exec": 1})
    elif scenario == "sensitive-file-read":
        row.update({"process_count": 16, "sensitive_file_access": 1})
    elif scenario == "network-scan":
        row.update({"network_connections": 120, "denied_egress": 10})
    elif scenario == "resource-abuse":
        row.update({"cpu_percent": 96.0, "memory_percent": 92.0, "process_count": 32})
    else:
        raise ValueError(f"unknown scenario: {scenario}")
    return row


def build_dataset(
    normal_count: int = 400,
    anomaly_count: int = 120,
    seed: int = 42,
) -> pd.DataFrame:
    """Return a deterministic labeled dataset for the local security lab."""

    if normal_count < 20 or anomaly_count < len(SCENARIOS):
        raise ValueError("use at least 20 normal and four anomaly events")

    rng = np.random.default_rng(seed)
    rows = [_normal_row(rng) for _ in range(normal_count)]
    rows.extend(_anomaly_row(rng, SCENARIOS[index % len(SCENARIOS)]) for index in range(anomaly_count))
    dataset = pd.DataFrame(rows, columns=[*FEATURE_COLUMNS, "label", "scenario"])
    return dataset.sample(frac=1, random_state=seed).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("ml/data/security_events.csv"))
    parser.add_argument("--normal-count", type=int, default=400)
    parser.add_argument("--anomaly-count", type=int, default=120)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    dataset = build_dataset(args.normal_count, args.anomaly_count, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(args.output, index=False)
    print(f"Wrote {len(dataset)} labeled events to {args.output}")


if __name__ == "__main__":
    main()
