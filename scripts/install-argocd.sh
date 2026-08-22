#!/usr/bin/env bash
set -euo pipefail

readonly CLUSTER_NAME="${1:-k8s-autoguard}"
readonly CONTEXT="kind-${CLUSTER_NAME}"
readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly NAMESPACE="argocd"
readonly CHART="argo/argo-cd"
readonly CHART_VERSION="8.5.8"

if [[ "$(kubectl config current-context)" != "${CONTEXT}" ]]; then
  echo "Expected Kubernetes context '${CONTEXT}'." >&2
  exit 1
fi

helm repo add argo https://argoproj.github.io/argo-helm --force-update
helm repo update argo
helm upgrade --install argocd "${CHART}" \
  --namespace "${NAMESPACE}" \
  --create-namespace \
  --version "${CHART_VERSION}" \
  --set global.domain=argocd.localhost \
  --wait \
  --timeout 15m
kubectl apply -f "${REPO_ROOT}/gitops/argocd/autoguard-platform-application.yaml"
kubectl -n "${NAMESPACE}" get applications.argoproj.io k8s-autoguard-platform
