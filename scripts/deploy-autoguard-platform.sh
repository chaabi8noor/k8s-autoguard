#!/usr/bin/env bash
set -euo pipefail

readonly CLUSTER_NAME="${1:-k8s-autoguard}"
readonly CONTEXT="kind-${CLUSTER_NAME}"
readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly IMAGE="k8s-autoguard-platform:dev"
readonly MANIFEST_FILE="${REPO_ROOT}/deployments/autoguard-platform/platform.yaml"

if [[ "$(kubectl config current-context)" != "${CONTEXT}" ]]; then
  echo "Expected Kubernetes context '${CONTEXT}'." >&2
  exit 1
fi

docker build --tag "${IMAGE}" "${REPO_ROOT}"
kind load docker-image "${IMAGE}" --name "${CLUSTER_NAME}"

kubectl apply -f "${MANIFEST_FILE}"
kubectl -n autoguard-system rollout status deployment/autoguard-ml-api --timeout=5m
kubectl -n autoguard-system rollout status deployment/autoguard-remediation --timeout=5m
kubectl -n autoguard-system get pods,svc -o wide
