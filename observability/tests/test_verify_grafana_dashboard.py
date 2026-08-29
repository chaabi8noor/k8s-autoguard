import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).parents[2]
SCRIPT = REPO_ROOT / "scripts" / "verify-grafana-dashboard.sh"


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(0o755)


def test_verifier_confirms_the_dashboard_after_the_sidecar_syncs(tmp_path: Path) -> None:
    """The installer must prove Grafana registered the dashboard, not just its ConfigMap."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    _write_executable(bin_dir / "sleep", "#!/usr/bin/env bash\\nexit 0\\n")
    _write_executable(
        bin_dir / "kubectl",
        """#!/usr/bin/env bash
set -euo pipefail

args="$*"

if [[ "$args" == *"test -s /tmp/dashboards/autoguard-security-overview.json"* ]]; then
  exit 0
fi

if [[ "$args" == *"api/dashboards/uid/autoguard-security-overview"* ]]; then
  if [[ "$args" != *"GF_SECURITY_ADMIN_USER"* ]]; then
    echo "Grafana credentials were not read inside the Grafana container" >&2
    exit 1
  fi
  exit 0
fi

echo "Unexpected kubectl call: $args" >&2
exit 1
""",
    )

    result = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"},
    )

    assert result.returncode == 0, result.stderr
    assert "Grafana dashboard 'autoguard-security-overview' is registered." in result.stdout
