from ml.data.generate_dataset import build_dataset
from ml.model import FEATURE_COLUMNS


def test_build_dataset_creates_labeled_normal_and_attack_scenarios() -> None:
    dataset = build_dataset(normal_count=40, anomaly_count=20, seed=7)

    assert len(dataset) == 60
    assert set(dataset["label"]) == {"normal", "anomaly"}
    assert {"baseline", "interactive-shell", "sensitive-file-read", "network-scan", "resource-abuse"}.issubset(
        set(dataset["scenario"])
    )
    assert set(FEATURE_COLUMNS).issubset(dataset.columns)
