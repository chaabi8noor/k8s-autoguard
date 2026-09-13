from pathlib import Path

import yaml


VALUES_FILE = Path(__file__).parents[2] / "infra" / "helm" / "kube-prometheus-stack-values.yaml"


def test_grafana_has_a_local_lab_startup_grace_period() -> None:
    values = yaml.safe_load(VALUES_FILE.read_text())

    assert values["grafana"]["livenessProbe"]["initialDelaySeconds"] >= 180

    limits = values["grafana"]["resources"]["limits"]
    assert limits["cpu"] == 1
    assert limits["memory"] == "1Gi"


def test_local_lab_omits_optional_cluster_wide_components() -> None:
    values = yaml.safe_load(VALUES_FILE.read_text())

    assert values["kubeStateMetrics"]["enabled"] is False
    assert values["alertmanager"]["enabled"] is False
    assert values["nodeExporter"]["enabled"] is False
