"""Small Prometheus text exporter for K8s AutoGuard service signals."""

from collections import Counter
from collections.abc import Callable
from threading import Lock
from time import time


PROMETHEUS_CONTENT_TYPE = "text/plain; version=0.0.4; charset=utf-8"


class AutoGuardMetrics:
    """Keep per-process service counters without a metrics backend dependency."""

    def __init__(self, *, clock: Callable[[], float] = time) -> None:
        self._lock = Lock()
        self._clock = clock
        self._prediction_totals: Counter[str] = Counter()
        self._remediation_totals: Counter[tuple[str, str]] = Counter()
        self._latest_risk_score: float | None = None
        self._latest_prediction_timestamp_seconds: float | None = None

    def record_prediction(self, *, is_anomaly: bool, risk_score: float) -> None:
        outcome = "anomaly" if is_anomaly else "normal"
        with self._lock:
            self._prediction_totals[outcome] += 1
            self._latest_risk_score = risk_score
            self._latest_prediction_timestamp_seconds = self._clock()

    def record_remediation(self, *, action: str, mode: str) -> None:
        with self._lock:
            self._remediation_totals[(action, mode)] += 1

    def render(self) -> str:
        with self._lock:
            prediction_totals = dict(self._prediction_totals)
            remediation_totals = dict(self._remediation_totals)
            latest_risk_score = self._latest_risk_score
            latest_prediction_timestamp_seconds = self._latest_prediction_timestamp_seconds

        lines = [
            "# HELP autoguard_predictions_total Total model predictions by outcome.",
            "# TYPE autoguard_predictions_total counter",
        ]
        for outcome in ("normal", "anomaly"):
            lines.append(
                f'autoguard_predictions_total{{outcome="{outcome}"}} '
                f"{prediction_totals.get(outcome, 0)}"
            )

        lines.extend(
            [
                "# HELP autoguard_prediction_risk_score Baseline-relative anomaly score of the most recent prediction.",
                "# TYPE autoguard_prediction_risk_score gauge",
                "# HELP autoguard_prediction_last_seen_timestamp_seconds Unix timestamp of the most recent prediction.",
                "# TYPE autoguard_prediction_last_seen_timestamp_seconds gauge",
            ]
        )
        if latest_risk_score is not None:
            lines.append(f"autoguard_prediction_risk_score {latest_risk_score:g}")
            lines.append(
                "autoguard_prediction_last_seen_timestamp_seconds "
                f"{latest_prediction_timestamp_seconds:g}"
            )

        lines.extend(
            [
                "# HELP autoguard_remediation_decisions_total Total remediation decisions by action and mode.",
                "# TYPE autoguard_remediation_decisions_total counter",
            ]
        )
        for (action, mode), count in sorted(remediation_totals.items()):
            lines.append(
                "autoguard_remediation_decisions_total"
                f'{{action="{action}",mode="{mode}"}} {count}'
            )

        return "\n".join(lines) + "\n"
