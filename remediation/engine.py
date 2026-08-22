"""Pure decision logic for the K8s AutoGuard remediation service."""

from dataclasses import dataclass
from enum import Enum


class Action(str, Enum):
    """Actions the service is allowed to request."""

    ALERT_ONLY = "alert_only"
    ISOLATE_WORKLOAD = "isolate_workload"


@dataclass(frozen=True)
class SecurityEvent:
    """Normalized fields from a Falco event."""

    event_id: str
    rule: str
    namespace: str
    pod: str
    container: str
    severity: str


@dataclass(frozen=True)
class Classification:
    """Model result using a normalized 0.0 to 1.0 risk score."""

    is_anomaly: bool
    risk_score: float
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class Decision:
    """An auditable policy decision, before any Kubernetes API call."""

    action: Action
    execute: bool
    reason: str


class RemediationPolicy:
    """Only isolate high-confidence, high-severity demo events by default."""

    def __init__(
        self,
        allowed_namespaces: frozenset[str] = frozenset({"autoguard-demo"}),
        minimum_risk_score: float = 0.80,
    ) -> None:
        self.allowed_namespaces = allowed_namespaces
        self.minimum_risk_score = minimum_risk_score

    def decide(self, event: SecurityEvent, classification: Classification) -> Decision:
        if not classification.is_anomaly:
            return Decision(Action.ALERT_ONLY, False, "model classified the event as normal")

        if event.namespace not in self.allowed_namespaces:
            return Decision(Action.ALERT_ONLY, False, "event namespace is outside remediation scope")

        if classification.risk_score < self.minimum_risk_score:
            return Decision(Action.ALERT_ONLY, False, "model risk score is below the remediation threshold")

        if event.severity.casefold() not in {"critical", "high"}:
            return Decision(Action.ALERT_ONLY, False, "Falco severity is below the remediation threshold")

        return Decision(
            Action.ISOLATE_WORKLOAD,
            True,
            "high-confidence high-severity anomaly in the allowed demo namespace",
        )
