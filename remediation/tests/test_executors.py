from remediation.engine import SecurityEvent
from remediation.executors import KubernetesCiliumExecutor, DryRunExecutor, build_isolation_policy


def test_build_isolation_policy_creates_a_namespaced_default_deny_cilium_policy() -> None:
    event = SecurityEvent(
        event_id="evt-001",
        rule="Terminal shell in container",
        namespace="autoguard-demo",
        pod="shell-test-abc123",
        container="shell-test",
        severity="Critical",
    )

    policy = build_isolation_policy(event)

    assert policy["apiVersion"] == "cilium.io/v2"
    assert policy["kind"] == "CiliumNetworkPolicy"
    assert policy["metadata"]["namespace"] == "autoguard-demo"
    assert policy["spec"]["endpointSelector"]["matchLabels"]["k8s:io.kubernetes.pod.name"] == "shell-test-abc123"
    assert policy["spec"]["ingress"] == []
    assert policy["spec"]["egress"] == []


def test_dry_run_executor_records_the_isolation_without_mutating_kubernetes() -> None:
    event = SecurityEvent(
        event_id="evt-002",
        rule="Terminal shell in container",
        namespace="autoguard-demo",
        pod="shell-test-abc123",
        container="shell-test",
        severity="Critical",
    )

    resource = DryRunExecutor().isolate_workload(event)

    assert resource.startswith("dry-run:ciliumnetworkpolicy/autoguard-isolate-shell-test-abc123-")


class RecordingCustomObjectsApi:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create_namespaced_custom_object(self, **kwargs: object) -> None:
        self.calls.append(kwargs)


def test_kubernetes_executor_creates_only_a_namespaced_cilium_policy() -> None:
    api = RecordingCustomObjectsApi()
    executor = KubernetesCiliumExecutor(api)
    event = SecurityEvent(
        event_id="evt-003",
        rule="Terminal shell in container",
        namespace="autoguard-demo",
        pod="shell-test-abc123",
        container="shell-test",
        severity="Critical",
    )

    resource = executor.isolate_workload(event)

    assert resource.startswith("ciliumnetworkpolicy/autoguard-isolate-shell-test-abc123-")
    assert api.calls[0]["group"] == "cilium.io"
    assert api.calls[0]["version"] == "v2"
    assert api.calls[0]["plural"] == "ciliumnetworkpolicies"
    assert api.calls[0]["namespace"] == "autoguard-demo"
