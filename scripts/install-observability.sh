#!/usr/bin/env bash
set -euo pipefail

readonly CLUSTER_NAME="${1:-k8s-autoguard}"
readonly CONTEXT="kind-${CLUSTER_NAME}"
readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly MONITORING_NAMESPACE="monitoring"
readonly LOKI_NAMESPACE="loki"
readonly MONITORING_RELEASE="autoguard-monitoring"
readonly PROMETHEUS_CHART="prometheus-community/kube-prometheus-stack"
readonly PROMETHEUS_VERSION="88.5.3"
readonly LOKI_CHART="grafana/loki"
readonly LOKI_VERSION="7.3.0"
readonly PROMTAIL_CHART="grafana/promtail"
readonly PROMTAIL_VERSION="6.17.1"

if [[ "$(kubectl config current-context)" != "${CONTEXT}" ]]; then
  echo "Expected Kubernetes context '${CONTEXT}'." >&2
  exit 1
fi

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts --force-update
helm repo add grafana https://grafana.github.io/helm-charts --force-update
helm repo update

helm upgrade --install "${MONITORING_RELEASE}" "${PROMETHEUS_CHART}" \
  --namespace "${MONITORING_NAMESPACE}" \
  --create-namespace \
  --version "${PROMETHEUS_VERSION}" \
  --values "${REPO_ROOT}/infra/helm/kube-prometheus-stack-values.yaml" \
  --wait \
  --timeout 20m

helm upgrade --install loki "${LOKI_CHART}" \
  --namespace "${LOKI_NAMESPACE}" \
  --create-namespace \
  --version "${LOKI_VERSION}" \
  --values "${REPO_ROOT}/infra/helm/loki-values.yaml" \
  --wait \
  --timeout 15m

helm upgrade --install promtail "${PROMTAIL_CHART}" \
  --namespace "${LOKI_NAMESPACE}" \
  --create-namespace \
  --version "${PROMTAIL_VERSION}" \
  --values "${REPO_ROOT}/infra/helm/promtail-values.yaml" \
  --wait \
  --timeout 15m

kubectl apply -f "${REPO_ROOT}/observability/servicemonitors/autoguard-services.yaml"
kubectl apply -f "${REPO_ROOT}/observability/alerts/autoguard-alerts.yaml"
kubectl apply -f "${REPO_ROOT}/observability/dashboards/autoguard-security-overview.yaml"

kubectl -n "${MONITORING_NAMESPACE}" rollout status deployment/autoguard-monitoring-grafana --timeout=10m
kubectl -n "${LOKI_NAMESPACE}" rollout status statefulset/loki --timeout=10m
kubectl -n "${LOKI_NAMESPACE}" rollout status daemonset/promtail --timeout=10m
kubectl -n "${MONITORING_NAMESPACE}" get pods
kubectl -n "${LOKI_NAMESPACE}" get pods
