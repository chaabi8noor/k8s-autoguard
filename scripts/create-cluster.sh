#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${1:-k8s-autoguard}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="${REPO_ROOT}/infra/kind/cluster.yaml"
CONTEXT="kind-${CLUSTER_NAME}"

if kind get clusters | grep -Fxq "${CLUSTER_NAME}"; then
  echo "Cluster '${CLUSTER_NAME}' already exists."
else
  kind create cluster \
    --name "${CLUSTER_NAME}" \
    --config "${CONFIG_FILE}" \
    --wait 120s
fi

kubectl config use-context "${CONTEXT}" >/dev/null
kubectl wait --for=condition=Ready node --all --timeout=120s
kubectl get nodes -o wide
