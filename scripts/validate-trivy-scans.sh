#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly SCAN_SCRIPT="${REPO_ROOT}/scripts/scan-trivy.sh"
readonly IMAGE_TO_SCAN="quay.io/cilium/alpine-curl:v1.10.0@sha256:913e8c9f3d960dde03882defa0edd3a919d529c2eb167caa7f54194528bde364"

echo "Checking Kubernetes manifests with Trivy..."
"${SCAN_SCRIPT}" --config

echo "Checking a pinned container image with Trivy..."
"${SCAN_SCRIPT}" --image "${IMAGE_TO_SCAN}"
