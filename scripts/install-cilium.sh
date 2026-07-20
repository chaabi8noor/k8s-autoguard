#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly CILIUM_VERSION="1.19.5"
readonly VALUES_FILE="${REPO_ROOT}/infra/helm/cilium-values.yaml"

helm upgrade --install cilium oci://quay.io/cilium/charts/cilium \
  --namespace kube-system \
  --create-namespace \
  --version "${CILIUM_VERSION}" \
  --values "${VALUES_FILE}" \
  --wait \
  --timeout 25m

kubectl rollout status daemonset/cilium --namespace kube-system --timeout=10m
kubectl rollout status daemonset/cilium-envoy --namespace kube-system --timeout=10m
kubectl rollout status deployment/cilium-operator --namespace kube-system --timeout=10m
kubectl rollout status deployment/hubble-relay --namespace kube-system --timeout=10m
kubectl rollout status deployment/hubble-ui --namespace kube-system --timeout=10m
