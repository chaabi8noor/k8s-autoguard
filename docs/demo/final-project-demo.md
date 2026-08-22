# Final Video Demo Runbook

Target length: 6 to 8 minutes.

## Preparation

```bash
./scripts/create-cluster.sh
./scripts/deploy-autoguard-platform.sh
./scripts/install-observability.sh
./scripts/run-final-project-demo.sh --interactive
```

Use `--interactive` to pause between scenes while recording the terminal. Run Grafana in a second terminal when the script reaches the observability scene:

```bash
kubectl -n monitoring port-forward service/autoguard-monitoring-grafana 3000:80
```

## Scene Sequence

1. Show the two-node KIND cluster and healthy Cilium status.
2. Show Kyverno accepting the secure Pod and rejecting the insecure Pod.
3. Show Falco detecting the controlled runtime event.
4. Show the ML API classifying a high-risk runtime outlier.
5. Show the remediation API returning a scoped dry-run isolation decision.
6. Show `/metrics` evidence, then the Grafana security overview dashboard and Loki logs.
7. Show the four protected GitHub Actions checks on `main`.

## What to Explain

- Cilium governs network identity and policy enforcement.
- Kyverno prevents insecure workloads from being admitted.
- Falco detects runtime behavior after a workload starts.
- The model adds anomaly risk and evidence to the event.
- Remediation is guarded: dry run is the default, and mutation is limited to a Cilium policy in `autoguard-demo`.
- Grafana distinguishes detections, dry-run recommendations, and genuinely executed actions.

## Recording Checklist

- Do not display Grafana credentials or browser tabs with personal information.
- State that model benchmark results use a deterministic synthetic scenario dataset.
- Show terminal output and dashboard data produced by the current demo, not pre-recorded evidence.
- End on the repository Actions page, README, and final report PDF.
