#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly NAMESPACE="autoguard-demo"
readonly WORKLOADS_FILE="${REPO_ROOT}/security/cilium-policies/demo-workloads.yaml"
readonly POLICY_FILE="${REPO_ROOT}/security/cilium-policies/api-ingress-from-trusted-client.yaml"
readonly API_URL="http://api:8080"

cleanup() {
  kubectl delete namespace "${NAMESPACE}" --ignore-not-found --wait=true
}

request_api() {
  local client="$1"

  kubectl -n "${NAMESPACE}" exec "deployment/${client}" -- \
    curl --silent --show-error --fail \
      --connect-timeout 3 --max-time 5 \
      --output /dev/null "${API_URL}"
}

wait_for_reachable() {
  local client="$1"

  for _ in {1..10}; do
    if request_api "${client}" >/dev/null 2>&1; then
      echo "${client} can reach the API."
      return 0
    fi
    sleep 1
  done

  echo "${client} could not reach the API." >&2
  return 1
}

if [[ "${1:-}" == "--cleanup" ]]; then
  cleanup
  exit 0
fi

if [[ $# -gt 0 ]]; then
  echo "Usage: $0 [--cleanup]" >&2
  exit 2
fi

kubectl delete -f "${POLICY_FILE}" --ignore-not-found
kubectl apply -f "${WORKLOADS_FILE}"

for deployment in api trusted-client untrusted-client; do
  kubectl rollout status "deployment/${deployment}" \
    --namespace "${NAMESPACE}" --timeout=5m
done

echo "Checking the open baseline..."
wait_for_reachable trusted-client
wait_for_reachable untrusted-client

kubectl apply -f "${POLICY_FILE}"

echo "Checking policy enforcement..."
wait_for_reachable trusted-client

for _ in {1..10}; do
  if ! request_api untrusted-client >/dev/null 2>&1; then
    echo "untrusted-client is blocked by policy."
    exit 0
  fi
  sleep 1
done

echo "untrusted-client remained reachable after policy enforcement." >&2
exit 1
