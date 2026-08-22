"""Orchestrate model classification and policy-approved remediation."""

from dataclasses import dataclass
from typing import Mapping, Protocol

from remediation.engine import Action, Classification, Decision, RemediationPolicy, SecurityEvent


class Classifier(Protocol):
    """A local model or remote API able to classify normalized features."""

    def classify(self, features: Mapping[str, float]) -> Classification: ...


class RemediationExecutor(Protocol):
    """The only executor operation allowed by the first remediation release."""

    def isolate_workload(self, event: SecurityEvent) -> str: ...


@dataclass(frozen=True)
class RemediationResult:
    classification: Classification
    decision: Decision
    executed_resource: str | None


class RemediationService:
    """Apply policy before passing any mutation to the executor."""

    def __init__(
        self,
        classifier: Classifier,
        executor: RemediationExecutor,
        policy: RemediationPolicy | None = None,
    ) -> None:
        self.classifier = classifier
        self.executor = executor
        self.policy = policy or RemediationPolicy()

    def handle(
        self,
        event: SecurityEvent,
        features: Mapping[str, float],
    ) -> RemediationResult:
        classification = self.classifier.classify(features)
        decision = self.policy.decide(event, classification)
        executed_resource = None
        if decision.execute and decision.action is Action.ISOLATE_WORKLOAD:
            executed_resource = self.executor.isolate_workload(event)
        return RemediationResult(classification, decision, executed_resource)
