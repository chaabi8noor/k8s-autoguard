#!/usr/bin/env bash
set -euo pipefail

readonly CLUSTER_NAME="k8s-autoguard"
readonly CONTEXT="kind-${CLUSTER_NAME}"
readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly FALCO_NAMESPACE="falco"
readonly DEMO_NAMESPACE="falco-demo"
readonly DEMO_POD="shell-test"
readonly WORKLOAD_FILE="${REPO_ROOT}/security/falco-rules/shell-test-workload.yaml"
readonly CUSTOM_RULE="AutoGuard Controlled Runtime Test"

cleanup() {
  kubectl delete namespace "${DEMO_NAMESPACE}" --ignore-not-found --wait=true
}

find_alert() {
  kubectl -n "${FALCO_NAMESPACE}" logs \
    "${FALCO_POD}" \
    -c falco \
    --since=2m | \
    grep -F "${CUSTOM_RULE}" | \
    grep -F "${TEST_PATH}"
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

kubectl -n "${FALCO_NAMESPACE}" rollout status daemonset/falco --timeout=5m
kubectl apply -f "${WORKLOAD_FILE}"
kubectl -n "${DEMO_NAMESPACE}" wait \
  --for=condition=Ready "pod/${DEMO_POD}" \
  --timeout=2m

readonly TEST_NODE="$(kubectl -n "${DEMO_NAMESPACE}" get "pod/${DEMO_POD}" \
  -o jsonpath='{.spec.nodeName}')"
readonly FALCO_POD="$(kubectl -n "${FALCO_NAMESPACE}" get pods \
  -l app.kubernetes.io/name=falco \
  --field-selector="spec.nodeName=${TEST_NODE}" \
  -o jsonpath='{.items[0].metadata.name}')"

if [[ -z "${FALCO_POD}" ]]; then
  echo "No Falco Pod was found on node '${TEST_NODE}'." >&2
  exit 1
fi

readonly RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
readonly TEST_PATH="/tmp/autoguard-runtime-test-${RUN_ID}"

echo "Using Falco sensor '${FALCO_POD}' on node '${TEST_NODE}'."
echo "Triggering the controlled runtime command..."
kubectl -n "${DEMO_NAMESPACE}" exec "${DEMO_POD}" -- touch "${TEST_PATH}"

echo "Waiting for Falco alert '${CUSTOM_RULE}'..."
for _ in {1..30}; do
  if alert="$(find_alert 2>/dev/null)"; then
    printf '%s\n' "${alert}"
    echo "Falco detected the controlled runtime command."
    exit 0
  fi
  sleep 1
done

echo "Falco did not emit the expected alert for '${TEST_PATH}'." >&2
kubectl -n "${FALCO_NAMESPACE}" logs \
  "${FALCO_POD}" \
  -c falco \
  --since=2m >&2
exit 1
