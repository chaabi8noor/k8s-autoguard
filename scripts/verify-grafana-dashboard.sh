#!/usr/bin/env bash
set -euo pipefail

readonly MONITORING_NAMESPACE="monitoring"
readonly GRAFANA_DEPLOYMENT="autoguard-monitoring-grafana"
readonly DASHBOARD_UID="autoguard-security-overview"
readonly DASHBOARD_FILE="/tmp/dashboards/${DASHBOARD_UID}.json"
readonly MAX_ATTEMPTS=30
readonly RETRY_DELAY_SECONDS=2

for ((attempt = 1; attempt <= MAX_ATTEMPTS; attempt++)); do
  if kubectl -n "${MONITORING_NAMESPACE}" exec "deployment/${GRAFANA_DEPLOYMENT}" -c grafana -- \
    test -s "${DASHBOARD_FILE}"; then
    if kubectl -n "${MONITORING_NAMESPACE}" exec "deployment/${GRAFANA_DEPLOYMENT}" -c grafana -- \
      sh -ceu '
        curl --fail --silent --show-error \
          --user "${GF_SECURITY_ADMIN_USER}:${GF_SECURITY_ADMIN_PASSWORD}" \
          "http://127.0.0.1:3000/api/dashboards/uid/autoguard-security-overview" >/dev/null
      '; then
      echo "Grafana dashboard '${DASHBOARD_UID}' is registered."
      exit 0
    fi
  fi

  sleep "${RETRY_DELAY_SECONDS}"
done

echo "Grafana did not register dashboard '${DASHBOARD_UID}' within $((MAX_ATTEMPTS * RETRY_DELAY_SECONDS)) seconds." >&2
exit 1
