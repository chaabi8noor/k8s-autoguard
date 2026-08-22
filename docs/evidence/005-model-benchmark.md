# Model Benchmark Evidence

- Date: 2026-08-22
- Command: `.venv/bin/python -m benchmark.run_benchmark`
- Dataset: `ml/data/security_events.csv`
- Model: `ml/models/isolation_forest_v1.joblib`

## Result

| Metric | Result |
| --- | ---: |
| Labelled scenario events | 520 |
| Recall | 1.00 |
| False-positive rate | 0.08 |
| P95 in-process detection latency | 38.69 ms |

These values are from the deterministic synthetic scenario dataset used for development. They measure model classification in process; they do not represent production network latency, Falco ingestion delay, Kubernetes remediation time, or a production MTTD/MTTR claim.

The raw machine-readable output is committed in `benchmark/results/model-benchmark.json`.
