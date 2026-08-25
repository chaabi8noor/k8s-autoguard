from pathlib import Path

import yaml


VALUES_FILE = Path(__file__).parents[2] / "infra" / "helm" / "promtail-values.yaml"


def test_promtail_scopes_file_targets_to_autoguard_namespaces() -> None:
    values = yaml.safe_load(VALUES_FILE.read_text())
    scrape_configs = values["config"]["snippets"]["scrapeConfigs"]

    assert "action: keep" in scrape_configs
    assert "regex: autoguard-system|autoguard-demo|falco|falco-demo" in scrape_configs

    init_container = values["initContainer"][0]
    assert init_container["name"] == "raise-inotify-limit"
    assert init_container["command"] == ["sh", "-c", "sysctl -w fs.inotify.max_user_instances=1024"]
    assert init_container["securityContext"]["privileged"] is True
