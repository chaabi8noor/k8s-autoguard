"""Pure metrics used by the benchmark runner and its tests."""

from math import ceil


def summarize_predictions(
    labels: list[int], predictions: list[int], latencies_ms: list[float]
) -> dict[str, float | int]:
    if not labels or len(labels) != len(predictions) or len(labels) != len(latencies_ms):
        raise ValueError("labels, predictions, and latencies_ms must be non-empty and aligned")

    true_positives = sum(label == 1 and prediction == 1 for label, prediction in zip(labels, predictions))
    false_negatives = sum(label == 1 and prediction == 0 for label, prediction in zip(labels, predictions))
    false_positives = sum(label == 0 and prediction == 1 for label, prediction in zip(labels, predictions))
    true_negatives = sum(label == 0 and prediction == 0 for label, prediction in zip(labels, predictions))
    ordered_latencies = sorted(latencies_ms)
    p95_index = ceil(len(ordered_latencies) * 0.95) - 1

    return {
        "events": len(labels),
        "recall": true_positives / (true_positives + false_negatives),
        "false_positive_rate": false_positives / (false_positives + true_negatives),
        "p95_detection_ms": ordered_latencies[p95_index],
    }
