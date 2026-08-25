import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts" / "validate-falco-runtime-demo.sh"


def test_validator_recreates_the_controlled_test_pod(tmp_path: Path) -> None:
    """A failed Pod from a previous run must not make the next demo time out."""
    bin_dir = tmp_path / "bin"
    state_dir = tmp_path / "state"
    bin_dir.mkdir()
    state_dir.mkdir()

    kubectl = bin_dir / "kubectl"
    kubectl.write_text(
        """#!/usr/bin/env bash
set -euo pipefail

args="$*"
printf '%s\\n' "$args" >> "$FAKE_KUBECTL_STATE/calls"

case "$args" in
  "config current-context")
    printf '%s\\n' "kind-k8s-autoguard"
    ;;
  *"rollout status daemonset/falco"*)
    ;;
  *"delete pod shell-test"*)
    touch "$FAKE_KUBECTL_STATE/pod-deleted"
    ;;
  "apply -f "*)
    if [[ ! -f "$FAKE_KUBECTL_STATE/pod-deleted" ]]; then
      echo "stale test pod was not deleted" >&2
      exit 1
    fi
    ;;
  *"wait --for=condition=Ready pod/shell-test"*)
    ;;
  *"get pod/shell-test -o jsonpath={.spec.nodeName}"*)
    printf '%s' "worker"
    ;;
  *"get pods -l app.kubernetes.io/name=falco"*)
    printf '%s' "falco-node"
    ;;
  *"exec shell-test -- touch "*)
    printf '%s' "${@: -1}" > "$FAKE_KUBECTL_STATE/test-path"
    ;;
  *"logs falco-node -c falco --since=2m"*)
    printf 'AutoGuard Controlled Runtime Test %s\\n' "$(< "$FAKE_KUBECTL_STATE/test-path")"
    ;;
esac
"""
    )
    kubectl.chmod(0o755)

    result = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "FAKE_KUBECTL_STATE": str(state_dir),
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        },
    )

    assert result.returncode == 0, result.stderr
