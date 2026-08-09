#!/usr/bin/env bash
set -euo pipefail

readonly CLUSTER_NAME="${1:-k8s-autoguard}"
readonly CONTEXT="kind-${CLUSTER_NAME}"
readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly NAMESPACE="falco"
readonly RELEASE_NAME="falco"
readonly CHART="falcosecurity/falco"
readonly CHART_VERSION="9.1.0"
readonly VALUES_FILE="${REPO_ROOT}/infra/helm/falco-values.yaml"

if [[ "$(kubectl config current-context)" != "${CONTEXT}" ]]; then
  echo "Expected Kubernetes context '${CONTEXT}'." >&2
  exit 1
fi

helm repo add falcosecurity https://falcosecurity.github.io/charts --force-update
helm repo update falcosecurity

helm upgrade --install "${RELEASE_NAME}" "${CHART}" \
  --namespace "${NAMESPACE}" \
  --create-namespace \
  --version "${CHART_VERSION}" \
  --values "${VALUES_FILE}" \
  --wait \
  --timeout 20m

kubectl rollout status "daemonset/${RELEASE_NAME}" \
  --namespace "${NAMESPACE}" \
  --timeout=10m

kubectl get pods --namespace "${NAMESPACE}" -o wide
