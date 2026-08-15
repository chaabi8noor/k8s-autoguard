#!/usr/bin/env bash
set -euo pipefail

readonly CLUSTER_NAME="k8s-autoguard"
readonly CONTEXT="kind-${CLUSTER_NAME}"
readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly NAMESPACE="autoguard-policy-demo"
readonly POLICY_NAME="autoguard-require-pod-security"
readonly SECURE_MANIFEST="${REPO_ROOT}/security/kyverno-policies/test-fixtures/secure-pod.yaml"
readonly INSECURE_MANIFEST="${REPO_ROOT}/security/kyverno-policies/test-fixtures/insecure-pod.yaml"

cleanup() {
  kubectl delete namespace "${NAMESPACE}" --ignore-not-found --wait=true
}

if [[ "${1:-}" == "--cleanup" ]]; then
  cleanup
  exit 0
fi

if [[ $# -gt 0 ]]; then
  echo "Usage: $0 [--cleanup]" >&2
  exit 2
fi

if [[ "$(kubectl config current-context)" != "${CONTEXT}" ]]; then
  echo "Expected Kubernetes context '${CONTEXT}'." >&2
  exit 1
fi

if ! kubectl get clusterpolicy "${POLICY_NAME}" >/dev/null 2>&1; then
  echo "Expected Kyverno policy '${POLICY_NAME}' is not installed." >&2
  exit 1
fi

kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

echo "Checking secure workload admission..."
kubectl apply --dry-run=server -f "${SECURE_MANIFEST}"

echo "Checking insecure workload rejection..."
if kubectl apply --dry-run=server -f "${INSECURE_MANIFEST}"; then
  echo "Insecure workload was admitted by the API server." >&2
  exit 1
fi

echo "Insecure workload was blocked by Kyverno."
