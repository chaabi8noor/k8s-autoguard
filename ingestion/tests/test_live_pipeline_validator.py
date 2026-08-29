import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate-live-falco-pipeline.sh"


def test_live_pipeline_validator_requires_the_same_real_falco_command_to_reach_dry_run(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    command_path = "/tmp/autoguard-runtime-test-20260829T180000Z"

    validator = tmp_path / "falco-validator"
    validator.write_text(
        f"#!/usr/bin/env bash\nprintf '%s\\n' 'AutoGuard Controlled Runtime Test {command_path}'\n"
    )
    validator.chmod(0o755)

    kubectl = bin_dir / "kubectl"
    kubectl.write_text(
        f"""#!/usr/bin/env bash
set -euo pipefail

case "$*" in
  "config current-context")
    printf '%s\\n' 'kind-k8s-autoguard'
    ;;
  *"/events/latest"*)
    printf '%s\\n' '{{ "command": "touch {command_path}", "remediation": {{ "executed_resource": "dry-run:ciliumnetworkpolicy/autoguard-isolate-shell-test" }} }}'
    ;;
  *"autoguard-event-ingestor:8000/proxy/metrics"*)
    printf '%s\\n' 'autoguard_falco_events_total{{outcome="forwarded"}} 1'
    ;;
  *"autoguard-ml-api:8000/proxy/metrics"*)
    printf '%s\\n' 'autoguard_predictions_total{{outcome="anomaly"}} 1'
    ;;
  *"autoguard-remediation:8000/proxy/metrics"*)
    printf '%s\\n' 'autoguard_remediation_decisions_total{{action="isolate_workload",mode="dry_run"}} 1'
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
            "AUTOGUARD_FALCO_VALIDATOR": str(validator),
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        },
    )

    assert result.returncode == 0, result.stderr
    assert "Real Falco-to-remediation pipeline passed." in result.stdout
