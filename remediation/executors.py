"""Build narrowly scoped Kubernetes remediation resources."""

import hashlib
import re
from typing import Any

from remediation.engine import SecurityEvent


def _policy_name(event: SecurityEvent) -> str:
    pod_slug = re.sub(r"[^a-z0-9-]+", "-", event.pod.casefold()).strip("-")
    suffix = hashlib.sha256(event.event_id.encode("utf-8")).hexdigest()[:8]
    return f"autoguard-isolate-{pod_slug[:34].rstrip('-')}-{suffix}"


def build_isolation_policy(event: SecurityEvent) -> dict[str, Any]:
    """Create a namespaced Cilium default-deny policy for one affected Pod."""

    return {
        "apiVersion": "cilium.io/v2",
        "kind": "CiliumNetworkPolicy",
        "metadata": {
            "name": _policy_name(event),
            "namespace": event.namespace,
            "labels": {
                "app.kubernetes.io/managed-by": "k8s-autoguard",
                "autoguard.io/event-id": event.event_id,
            },
        },
        "spec": {
            "endpointSelector": {
                "matchLabels": {"k8s:io.kubernetes.pod.name": event.pod}
            },
            "ingress": [],
            "egress": [],
        },
    }


class DryRunExecutor:
    """Report the resource that would be created without calling Kubernetes."""

    def isolate_workload(self, event: SecurityEvent) -> str:
        policy = build_isolation_policy(event)
        return f"dry-run:ciliumnetworkpolicy/{policy['metadata']['name']}"


class KubernetesCiliumExecutor:
    """Create the scoped Cilium custom resource through the Kubernetes API."""

    def __init__(self, custom_objects_api: Any) -> None:
        self.custom_objects_api = custom_objects_api

    def isolate_workload(self, event: SecurityEvent) -> str:
        policy = build_isolation_policy(event)
        self.custom_objects_api.create_namespaced_custom_object(
            group="cilium.io",
            version="v2",
            namespace=event.namespace,
            plural="ciliumnetworkpolicies",
            body=policy,
        )
        return f"ciliumnetworkpolicy/{policy['metadata']['name']}"
