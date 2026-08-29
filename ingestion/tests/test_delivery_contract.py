from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).parents[2]


def test_falco_sidekick_delivers_only_critical_lab_alerts_to_the_ingestor() -> None:
    values = yaml.safe_load((REPO_ROOT / "infra" / "helm" / "falco-values.yaml").read_text())

    assert values["falcosidekick"]["enabled"] is True
    assert values["falcosidekick"]["config"]["webhook"] == {
        "address": "http://autoguard-event-ingestor.autoguard-system.svc.cluster.local:8000/falco-events",
        "minimumpriority": "critical",
    }
    assert "priority: CRITICAL" in values["customRules"]["autoguard-runtime-rules.yaml"]


def test_platform_deploys_a_cluster_internal_event_ingestor_and_scrapes_its_metrics() -> None:
    documents = list(
        yaml.safe_load_all(
            (REPO_ROOT / "deployments" / "autoguard-platform" / "platform.yaml").read_text()
        )
    )
    deployment = next(
        document
        for document in documents
        if document["kind"] == "Deployment"
        and document["metadata"]["name"] == "autoguard-event-ingestor"
    )
    service = next(
        document
        for document in documents
        if document["kind"] == "Service"
        and document["metadata"]["name"] == "autoguard-event-ingestor"
    )
    monitors = list(
        yaml.safe_load_all(
            (REPO_ROOT / "observability" / "servicemonitors" / "autoguard-services.yaml").read_text()
        )
    )

    assert deployment["spec"]["template"]["spec"]["containers"][0]["command"] == [
        "uvicorn",
        "ingestion.runtime:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]
    assert service["spec"]["type"] == "ClusterIP"
    assert any(
        monitor["metadata"]["name"] == "autoguard-event-ingestor"
        for monitor in monitors
    )


def test_final_demo_uses_the_real_falco_to_remediation_validator() -> None:
    script = (REPO_ROOT / "scripts" / "run-final-project-demo.sh").read_text()

    assert "validate-live-falco-pipeline.sh" in script


def test_platform_image_and_deploy_script_include_the_event_ingestor() -> None:
    dockerfile = (REPO_ROOT / "Dockerfile").read_text()
    deploy_script = (REPO_ROOT / "scripts" / "deploy-autoguard-platform.sh").read_text()

    assert "COPY ingestion ./ingestion" in dockerfile
    assert "rollout restart deployment/autoguard-ml-api deployment/autoguard-remediation deployment/autoguard-event-ingestor" in deploy_script
    assert "rollout status deployment/autoguard-event-ingestor" in deploy_script


def test_falco_installation_waits_for_sidekick_before_running_live_validation() -> None:
    install_script = (REPO_ROOT / "scripts" / "install-falco.sh").read_text()

    assert "rollout status \"deployment/${RELEASE_NAME}-falcosidekick\"" in install_script
