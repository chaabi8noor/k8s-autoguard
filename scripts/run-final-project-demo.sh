#!/usr/bin/env bash
set -euo pipefail

readonly CLUSTER_NAME="k8s-autoguard"
readonly CONTEXT="kind-${CLUSTER_NAME}"
readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly CURL_IMAGE="quay.io/cilium/alpine-curl:v1.10.0@sha256:913e8c9f3d960dde03882defa0edd3a919d529c2eb167caa7f54194528bde364"

interactive=false

pause_for_recording() {
  if [[ "${interactive}" == true ]]; then
    read -r -p "Press Enter to continue to the next scene..."
  fi
}

scene() {
  printf "\n========== %s ==========\n" "$1"
}

case "${1:-}" in
  "")
    ;;
  --interactive)
    interactive=true
    ;;
  *)
    echo "Usage: $0 [--interactive]" >&2
    exit 2
    ;;
esac

if [[ "$(kubectl config current-context)" != "${CONTEXT}" ]]; then
  echo "Expected Kubernetes context '${CONTEXT}'." >&2
  exit 1
fi

scene "Scene 1: Healthy Cilium foundation"
kubectl get nodes -o wide
cilium status --wait
pause_for_recording

scene "Scene 2: Preventive admission control"
"${REPO_ROOT}/scripts/validate-kyverno-policy-demo.sh"
pause_for_recording

scene "Scene 3: Runtime detection"
"${REPO_ROOT}/scripts/validate-falco-runtime-demo.sh"
pause_for_recording

scene "Scene 4: ML anomaly classification"
kubectl run autoguard-ml-signal \
  --namespace autoguard-system \
  --rm \
  --restart=Never \
  --image "${CURL_IMAGE}" \
  -- curl --silent --show-error --fail \
  --request POST \
  --header "Content-Type: application/json" \
  --data '{"cpu_percent":97,"memory_percent":94,"network_connections":160,"process_count":48,"shell_exec":1,"sensitive_file_access":1,"denied_egress":12}' \
  http://autoguard-ml-api:8000/predict
pause_for_recording

scene "Scene 5: Guarded dry-run remediation"
kubectl run autoguard-remediation-signal \
  --namespace autoguard-system \
  --rm \
  --restart=Never \
  --image "${CURL_IMAGE}" \
  -- curl --silent --show-error --fail \
  --request POST \
  --header "Content-Type: application/json" \
  --data '{"event":{"event_id":"demo-001","rule":"Terminal shell in container","namespace":"autoguard-demo","pod":"shell-test","container":"shell-test","severity":"Critical"},"features":{"shell_exec":1.0}}' \
  http://autoguard-remediation:8000/events
pause_for_recording

scene "Scene 6: Metrics, alerts, and dashboard"
"${REPO_ROOT}/scripts/validate-observability.sh"
pause_for_recording

scene "Scene 7: Protected CI evidence"
if command -v gh >/dev/null 2>&1; then
  gh pr checks 9 --repo chaabi8noor/k8s-autoguard || true
else
  echo "Open the repository Actions page to show the protected CI checks."
fi

echo "Final demo complete. Open Grafana using the command printed in Scene 6."
