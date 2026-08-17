#!/usr/bin/env bash
set -euo pipefail

readonly CLUSTER_NAME="${1:-k8s-autoguard}"
readonly CONTEXT="kind-${CLUSTER_NAME}"
readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly NAMESPACE="kyverno"
readonly RELEASE_NAME="kyverno"
readonly CHART="kyverno/kyverno"
readonly CHART_VERSION="3.8.2"
readonly VALUES_FILE="${REPO_ROOT}/infra/helm/kyverno-values.yaml"
readonly POLICY_FILE="${REPO_ROOT}/security/kyverno-policies/autoguard-require-pod-security.yaml"
readonly POLICY_NAME="autoguard-require-pod-security"

if [[ "$(kubectl config current-context)" != "${CONTEXT}" ]]; then
  echo "Expected Kubernetes context '${CONTEXT}'." >&2
  exit 1
fi

helm repo add kyverno https://kyverno.github.io/kyverno/ --force-update
helm repo update kyverno

helm upgrade --install "${RELEASE_NAME}" "${CHART}" \
  --namespace "${NAMESPACE}" \
  --create-namespace \
  --version "${CHART_VERSION}" \
  --values "${VALUES_FILE}" \
  --wait \
  --timeout 15m

kubectl wait \
  --for=condition=Established \
  crd/clusterpolicies.kyverno.io \
  --timeout=5m

kubectl apply -f "${POLICY_FILE}"
kubectl get clusterpolicy "${POLICY_NAME}"
kubectl get pods --namespace "${NAMESPACE}" -o wide
