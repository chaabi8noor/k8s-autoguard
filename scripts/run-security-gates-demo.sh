#!/usr/bin/env bash
set -euo pipefail

readonly CLUSTER_NAME="k8s-autoguard"
readonly CONTEXT="kind-${CLUSTER_NAME}"
readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly DEMO_IMAGE="quay.io/cilium/alpine-curl:v1.10.0@sha256:913e8c9f3d960dde03882defa0edd3a919d529c2eb167caa7f54194528bde364"

interactive=false

usage() {
  echo "Usage: $0 [--interactive]" >&2
}

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
    usage
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

scene "Scene 2: Kyverno blocks an insecure Pod"
kubectl get clusterpolicy autoguard-require-pod-security
"${REPO_ROOT}/scripts/validate-kyverno-policy-demo.sh"
pause_for_recording

scene "Scene 3: Trivy manifest gate"
"${REPO_ROOT}/scripts/scan-trivy.sh" --config
pause_for_recording

scene "Scene 4: GitHub Actions evidence"
if command -v gh >/dev/null 2>&1; then
  gh api \
    "repos/chaabi8noor/k8s-autoguard/actions/runs?branch=main&per_page=1" \
    --jq '.workflow_runs[0] | "Latest main security workflow: \(.conclusion) \(.html_url)"' \
    || echo "GitHub Actions status could not be fetched. Open the repository Actions tab."
else
  echo "GitHub CLI is unavailable. Open the repository Actions tab for CI evidence."
fi

printf "\nDemo complete. Cleanup: %s --cleanup\n" \
  "${REPO_ROOT}/scripts/validate-kyverno-policy-demo.sh"
