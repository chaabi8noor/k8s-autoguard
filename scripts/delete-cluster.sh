#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${1:-k8s-autoguard}"

if kind get clusters | grep -Fxq "${CLUSTER_NAME}"; then
  kind delete cluster --name "${CLUSTER_NAME}"
else
  echo "Cluster '${CLUSTER_NAME}' does not exist."
fi
