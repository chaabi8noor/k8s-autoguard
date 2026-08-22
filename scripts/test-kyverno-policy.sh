#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly KYVERNO_VERSION="1.18.2"
readonly KYVERNO_CLI_ARCHIVE_URL="https://github.com/kyverno/kyverno/releases/download/v${KYVERNO_VERSION}/kyverno-cli_v${KYVERNO_VERSION}_linux_x86_64.tar.gz"
readonly TEST_DIRECTORY="security/kyverno-policies/tests"
readonly TEMP_DIRECTORY="$(mktemp -d)"

cleanup() {
  rm -rf "${TEMP_DIRECTORY}"
}
trap cleanup EXIT

curl --fail --location --retry 3 --silent --show-error \
  "${KYVERNO_CLI_ARCHIVE_URL}" \
  | tar --extract --gzip --directory "${TEMP_DIRECTORY}"

"${TEMP_DIRECTORY}/kyverno" test "${REPO_ROOT}/${TEST_DIRECTORY}"
