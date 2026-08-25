from pathlib import Path


SCRIPT = Path(__file__).parents[3] / "scripts" / "deploy-autoguard-platform.sh"


def test_deploy_script_restarts_workloads_after_loading_the_local_image() -> None:
    assert "rollout restart deployment/autoguard-ml-api deployment/autoguard-remediation" in SCRIPT.read_text()
