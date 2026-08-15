#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly TRIVY_IMAGE="aquasec/trivy:0.69.3"
readonly CACHE_VOLUME="k8s-autoguard-trivy-cache"
readonly CONFIG_TARGET="/workspace/security/kyverno-policies"
readonly INSECURE_FIXTURE="/workspace/security/kyverno-policies/test-fixtures/insecure-pod.yaml"

usage() {
  echo "Usage: $0 --config | --image IMAGE" >&2
}

run_trivy() {
  docker run --rm \
    --volume "${CACHE_VOLUME}:/root/.cache/" \
    --volume "${REPO_ROOT}:/workspace:ro" \
    "${TRIVY_IMAGE}" "$@"
}

scan_config() {
  run_trivy config \
    --severity HIGH,CRITICAL \
    --exit-code 1 \
    --skip-files "${INSECURE_FIXTURE}" \
    "${CONFIG_TARGET}"
}

scan_image() {
  local image="$1"

  run_trivy image \
    --scanners vuln \
    --severity HIGH,CRITICAL \
    --ignore-unfixed \
    --exit-code 0 \
    "${image}"
}

case "${1:-}" in
  --config)
    [[ $# -eq 1 ]] || { usage; exit 2; }
    scan_config
    ;;
  --image)
    [[ $# -eq 2 ]] || { usage; exit 2; }
    scan_image "$2"
    ;;
  *)
    usage
    exit 2
    ;;
esac
