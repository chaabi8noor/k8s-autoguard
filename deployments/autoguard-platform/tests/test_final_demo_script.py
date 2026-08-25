import os
import shutil
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).parents[3] / "scripts" / "run-final-project-demo.sh"


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(0o755)


def test_disposable_demo_clients_replace_the_curl_image_entrypoint(
    tmp_path: Path,
) -> None:
    """Both API clients must run curl as their command, not as an argument."""
    scripts_dir = tmp_path / "scripts"
    bin_dir = tmp_path / "bin"
    scripts_dir.mkdir()
    bin_dir.mkdir()
    shutil.copy2(SCRIPT, scripts_dir / SCRIPT.name)

    for validator in (
        "validate-kyverno-policy-demo.sh",
        "validate-falco-runtime-demo.sh",
        "validate-observability.sh",
    ):
        _write_executable(scripts_dir / validator, "#!/usr/bin/env bash\nexit 0\n")

    _write_executable(
        bin_dir / "kubectl",
        """#!/usr/bin/env bash
set -euo pipefail

args="$*"
if [[ "$args" == "config current-context" ]]; then
  printf '%s\\n' "kind-k8s-autoguard"
elif [[ "$args" == run\\ * || "$args" == *" run "* ]]; then
  if [[ "$args" == *"autoguard-ml-signal"* || "$args" == *"autoguard-remediation-signal"* ]]; then
    if [[ "$args" != *"--command -- curl --silent --show-error --fail"* ]]; then
      echo "demo client did not replace the curl image entrypoint" >&2
      exit 1
    fi
  fi
fi
""",
    )
    _write_executable(bin_dir / "cilium", "#!/usr/bin/env bash\nexit 0\n")
    _write_executable(bin_dir / "gh", "#!/usr/bin/env bash\nexit 0\n")

    result = subprocess.run(
        ["bash", str(scripts_dir / SCRIPT.name)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"},
    )

    assert result.returncode == 0, result.stderr
