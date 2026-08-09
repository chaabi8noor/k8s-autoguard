#!/usr/bin/env bash
set -euo pipefail

readonly CLUSTER_NAME="${1:-k8s-autoguard}"
readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly CONFIG_FILE="${REPO_ROOT}/infra/kind/cluster.yaml"
readonly CONTEXT="kind-${CLUSTER_NAME}"

if kind get clusters | grep -Fxq "${CLUSTER_NAME}"; then
  echo "Cluster '${CLUSTER_NAME}' already exists."
else
  kind create cluster \
    --name "${CLUSTER_NAME}" \
    --config "${CONFIG_FILE}"
fi

kubectl config use-context "${CONTEXT}" >/dev/null

if kubectl -n kube-system get daemonset kindnet >/dev/null 2>&1; then
  echo "Cluster '${CLUSTER_NAME}' still uses KIND's default CNI." >&2
  echo "Delete it before installing Cilium: ./scripts/delete-cluster.sh" >&2
  exit 1
fi

"${REPO_ROOT}/scripts/install-cilium.sh"

kubectl wait --for=condition=Ready node --all --timeout=5m
"${REPO_ROOT}/scripts/install-falco.sh" "${CLUSTER_NAME}"
kubectl get nodes -o wide
