from pathlib import Path

import yaml


VALUES_FILE = Path(__file__).parents[2] / "infra" / "helm" / "loki-values.yaml"


def test_single_binary_loki_disables_optional_memcached_caches() -> None:
    values = yaml.safe_load(VALUES_FILE.read_text())

    assert values["chunksCache"]["enabled"] is False
    assert values["resultsCache"]["enabled"] is False
    assert values["ruler"]["enabled"] is False

    mount = values["singleBinary"]["extraVolumeMounts"][0]
    assert mount == {"name": "loki-data", "mountPath": "/var/loki"}
    assert values["singleBinary"]["extraVolumes"] == [{"name": "loki-data", "emptyDir": {}}]
