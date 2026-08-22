"""Small Prometheus text exporter for K8s AutoGuard service signals."""

from collections import Counter
from threading import Lock


PROMETHEUS_CONTENT_TYPE = "text/plain; version=0.0.4; charset=utf-8"


class AutoGuardMetrics:
    """Keep per-process service counters without a metrics backend dependency."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._prediction_totals: Counter[str] = Counter()
        self._remediation_totals: Counter[tuple[str, str]] = Counter()
        self._latest_risk_score: float | None = None

    def record_prediction(self, *, is_anomaly: bool, risk_score: float) -> None:
        outcome = "anomaly" if is_anomaly else "normal"
        with self._lock:
            self._prediction_totals[outcome] += 1
            self._latest_risk_score = risk_score

    def record_remediation(self, *, action: str, mode: str) -> None:
        with self._lock:
            self._remediation_totals[(action, mode)] += 1

    def render(self) -> str:
        with self._lock:
            prediction_totals = dict(self._prediction_totals)
            remediation_totals = dict(self._remediation_totals)
            latest_risk_score = self._latest_risk_score

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
                "# HELP autoguard_prediction_risk_score Risk score of the most recent prediction.",
                "# TYPE autoguard_prediction_risk_score gauge",
            ]
        )
        if latest_risk_score is not None:
            lines.append(f"autoguard_prediction_risk_score {latest_risk_score:g}")

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
