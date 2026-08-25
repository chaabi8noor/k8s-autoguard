from pathlib import Path

import yaml


MANIFEST = Path(__file__).parents[1] / "platform.yaml"


def test_platform_manifest_declares_each_namespace_it_uses() -> None:
    documents = list(yaml.safe_load_all(MANIFEST.read_text()))
    declared_namespaces = {
        document["metadata"]["name"]
        for document in documents
        if document and document.get("kind") == "Namespace"
    }
    used_namespaces = {
        document["metadata"]["namespace"]
        for document in documents
        if document and document.get("metadata", {}).get("namespace")
    }

    assert used_namespaces <= declared_namespaces
