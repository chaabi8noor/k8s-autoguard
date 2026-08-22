#!/usr/bin/env bash
set -euo pipefail

readonly CLUSTER_NAME="${1:-k8s-autoguard}"
readonly CONTEXT="kind-${CLUSTER_NAME}"
readonly GRAFANA_SERVICE="autoguard-monitoring-grafana"

if [[ "$(kubectl config current-context)" != "${CONTEXT}" ]]; then
  echo "Expected Kubernetes context '${CONTEXT}'." >&2
  exit 1
fi

kubectl -n autoguard-system get servicemonitor,prometheusrule
kubectl -n monitoring get configmap autoguard-security-overview

echo "Checking ML API metrics through the Kubernetes service proxy..."
kubectl get --raw \
  /api/v1/namespaces/autoguard-system/services/http:autoguard-ml-api:8000/proxy/metrics \
  | grep -F "autoguard_predictions_total"

echo "Checking remediation API metrics through the Kubernetes service proxy..."
kubectl get --raw \
  /api/v1/namespaces/autoguard-system/services/http:autoguard-remediation:8000/proxy/metrics \
  | grep -F "autoguard_remediation_decisions_total"

echo "Grafana is ready for a local port-forward:"
echo "kubectl -n monitoring port-forward service/${GRAFANA_SERVICE} 3000:80"
echo "Retrieve the generated local-lab password with:"
echo "kubectl -n monitoring get secret ${GRAFANA_SERVICE} -o jsonpath='{.data.admin-password}' | base64 --decode"
