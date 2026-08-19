"""Deterministic Isolation Forest training and inference helpers."""

from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Mapping
import warnings

import pandas as pd
from joblib import dump, load
from numpy import quantile
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from remediation.engine import Classification


FEATURE_COLUMNS = (
    "cpu_percent",
    "memory_percent",
    "network_connections",
    "process_count",
    "shell_exec",
    "sensitive_file_access",
    "denied_egress",
)

DERIVED_FEATURE_COLUMNS = (
    "resource_pressure",
    "execution_signal",
    "sensitive_access_signal",
    "network_burst_signal",
)

ANOMALY_RISK_THRESHOLD = 0.80


@dataclass(frozen=True)
class Detector:
    """A fitted model together with training-score calibration boundaries."""

    pipeline: Pipeline
    risk_floor: float
    risk_ceiling: float
    version: str = "isolation-forest-v1"


def _feature_frame(events: pd.DataFrame | Mapping[str, float]) -> pd.DataFrame:
    frame = pd.DataFrame([events]) if isinstance(events, Mapping) else events.copy()
    missing = set(FEATURE_COLUMNS).difference(frame.columns)
    if missing:
        raise ValueError(f"missing required features: {', '.join(sorted(missing))}")

    raw_features = frame.loc[:, FEATURE_COLUMNS].apply(pd.to_numeric, errors="raise")
    if not raw_features.apply(lambda column: column.map(isfinite).all()).all():
        raise ValueError("feature values must be finite")

    engineered_features = raw_features.assign(
        resource_pressure=(raw_features["cpu_percent"] * 0.6)
        + (raw_features["memory_percent"] * 0.4),
        execution_signal=raw_features["shell_exec"] * 20,
        sensitive_access_signal=raw_features["sensitive_file_access"] * 20,
        network_burst_signal=(raw_features["network_connections"] - 6).clip(lower=0)
        + (raw_features["denied_egress"] * 10),
    )
    return engineered_features.loc[:, [*FEATURE_COLUMNS, *DERIVED_FEATURE_COLUMNS]]


def train_detector(normal_events: pd.DataFrame) -> Detector:
    """Train only on known-normal traffic so the model learns a local baseline."""

    frame = _feature_frame(normal_events)
    if len(frame) < 20:
        raise ValueError("at least 20 normal events are required for training")

    pipeline = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "isolation_forest",
                IsolationForest(
                    n_estimators=200,
                    contamination=0.05,
                    random_state=42,
                ),
            ),
        ]
    )
    pipeline.fit(frame)

    baseline_anomaly_scores = -pipeline.score_samples(frame)
    return Detector(
        pipeline=pipeline,
        risk_floor=float(quantile(baseline_anomaly_scores, 0.50)),
        risk_ceiling=float(quantile(baseline_anomaly_scores, 0.95)),
    )


def classify_event(detector: Detector, features: Mapping[str, float]) -> Classification:
    """Return the model label and a calibrated 0.0 to 1.0 risk score."""

    frame = _feature_frame(features)
    raw_anomaly_score = float(-detector.pipeline.score_samples(frame)[0])
    span = max(detector.risk_ceiling - detector.risk_floor, 1e-9)
    risk_score = min(1.0, max(0.0, (raw_anomaly_score - detector.risk_floor) / span))
    first_event = frame.iloc[0]
    evidence = []
    if first_event["shell_exec"] >= 1:
        evidence.append("shell-execution")
    if first_event["sensitive_file_access"] >= 1:
        evidence.append("sensitive-file-access")
    if first_event["denied_egress"] >= 5:
        evidence.append("denied-egress-burst")
    if evidence:
        risk_score = max(risk_score, 0.90)
    return Classification(
        is_anomaly=risk_score >= ANOMALY_RISK_THRESHOLD,
        risk_score=round(risk_score, 4),
        evidence=tuple(evidence),
    )


def save_detector(detector: Detector, path: Path) -> None:
    """Persist a fitted detector and its calibration values as one artifact."""

    path.parent.mkdir(parents=True, exist_ok=True)
    dump(detector, path)


def load_detector(path: Path) -> Detector:
    """Load a detector artifact and reject files that are not model bundles."""

    # NumPy 2.5 warns about an internal Joblib shape assignment during reload.
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Setting the shape on a NumPy array has been deprecated",
            category=DeprecationWarning,
            module="joblib.numpy_pickle",
        )
        detector = load(path)
    if not isinstance(detector, Detector):
        raise ValueError("model artifact does not contain a K8s AutoGuard detector")
    return detector
