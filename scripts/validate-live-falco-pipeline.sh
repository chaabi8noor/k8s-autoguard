#!/usr/bin/env bash
set -euo pipefail

readonly CLUSTER_NAME="k8s-autoguard"
readonly CONTEXT="kind-${CLUSTER_NAME}"
readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly FALCO_VALIDATOR="${AUTOGUARD_FALCO_VALIDATOR:-${REPO_ROOT}/scripts/validate-falco-runtime-demo.sh}"
readonly INGESTOR_LATEST_PATH="/api/v1/namespaces/autoguard-system/services/http:autoguard-event-ingestor:8000/proxy/events/latest"
readonly INGESTOR_METRICS_PATH="/api/v1/namespaces/autoguard-system/services/http:autoguard-event-ingestor:8000/proxy/metrics"
readonly ML_METRICS_PATH="/api/v1/namespaces/autoguard-system/services/http:autoguard-ml-api:8000/proxy/metrics"
readonly REMEDIATION_METRICS_PATH="/api/v1/namespaces/autoguard-system/services/http:autoguard-remediation:8000/proxy/metrics"

event_matches() {
  python3 -c '
import json
import sys

raw_payload = sys.stdin.read()
if not raw_payload.strip():
    raise SystemExit(1)

try:
    payload = json.loads(raw_payload)
except json.JSONDecodeError:
    raise SystemExit(1)
expected_command = sys.argv[1]
resource = payload.get("remediation", {}).get("executed_resource") or ""
raise SystemExit(not (
    expected_command in payload.get("command", "")
    and resource.startswith("dry-run:ciliumnetworkpolicy/")
))
' "$test_path"
}

if [[ "$(kubectl config current-context)" != "${CONTEXT}" ]]; then
  echo "Expected Kubernetes context '${CONTEXT}'." >&2
  exit 1
fi

echo "Triggering the real Falco runtime test..."
falco_output="$("${FALCO_VALIDATOR}")"
printf '%s\n' "${falco_output}"

test_path="$(printf '%s\n' "${falco_output}" | grep -Eo '/tmp/autoguard-runtime-test-[0-9TZ]+' | head -n 1 || true)"
if [[ -z "${test_path}" ]]; then
  echo "Could not identify the unique runtime command from Falco output." >&2
  exit 1
fi

echo "Waiting for Falco Sidekick to forward '${test_path}' to AutoGuard..."
for _ in {1..45}; do
  latest_event="$(kubectl get --raw "${INGESTOR_LATEST_PATH}" 2>/dev/null || true)"
  if printf '%s' "${latest_event}" | event_matches; then
    printf '%s\n' "${latest_event}"
    break
  fi
  sleep 1
done

if ! printf '%s' "${latest_event:-}" | event_matches; then
  echo "The Falco event was not forwarded to a guarded dry-run decision." >&2
  exit 1
fi

echo "Verifying the three service metrics..."
ingestor_metrics="$(kubectl get --raw "${INGESTOR_METRICS_PATH}")"
ml_metrics="$(kubectl get --raw "${ML_METRICS_PATH}")"
remediation_metrics="$(kubectl get --raw "${REMEDIATION_METRICS_PATH}")"

printf '%s\n' "${ingestor_metrics}" | \
  grep -F 'autoguard_falco_events_total{outcome="forwarded"} ' >/dev/null
printf '%s\n' "${ml_metrics}" | \
  grep -F 'autoguard_predictions_total{outcome="anomaly"} ' >/dev/null
printf '%s\n' "${remediation_metrics}" | \
  grep -F 'autoguard_remediation_decisions_total{action="isolate_workload",mode="dry_run"} ' >/dev/null

echo "Real Falco-to-remediation pipeline passed."
