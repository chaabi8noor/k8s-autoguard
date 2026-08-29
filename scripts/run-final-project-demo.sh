#!/usr/bin/env bash
set -euo pipefail

readonly CLUSTER_NAME="k8s-autoguard"
readonly CONTEXT="kind-${CLUSTER_NAME}"
readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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

scene "Scene 3: Real Falco detection to guarded remediation"
"${REPO_ROOT}/scripts/validate-live-falco-pipeline.sh"
pause_for_recording

scene "Scene 4: Metrics, alerts, and dashboard"
"${REPO_ROOT}/scripts/validate-observability.sh"
pause_for_recording

scene "Scene 5: Protected CI evidence"
if command -v gh >/dev/null 2>&1; then
  gh pr checks 9 --repo chaabi8noor/k8s-autoguard || true
else
  echo "Open the repository Actions page to show the protected CI checks."
fi

echo "Final demo complete. Open Grafana using the command in the video runbook."
