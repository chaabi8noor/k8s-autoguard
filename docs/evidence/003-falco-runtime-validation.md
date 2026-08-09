# Falco Runtime Validation Evidence

- Date: 2026-08-09
- Cluster: `kind-k8s-autoguard`
- Falco chart: `9.1.0`
- Falco image: `0.44.1`
- Runtime driver: modern eBPF with least-privileged mode

## Sensor Health

The Falco DaemonSet reached `2/2` ready and available Pods: one on `k8s-autoguard-control-plane` and one on `k8s-autoguard-worker`.

Falco logs confirmed that both agents loaded the `syscall` event source and opened the modern BPF probe.

## Custom Rule Validation

`scripts/validate-falco-runtime-demo.sh` scheduled `falco-demo/shell-test` on `k8s-autoguard-worker`, identified the Falco Pod on that node, then ran:

```text
touch /tmp/autoguard-runtime-test-20260809T075636Z
```

Falco emitted the `AutoGuard Controlled Runtime Test` rule at `Notice` priority. Its JSON output included the command, container name, image repository, Pod name, namespace, tags, and ISO 8601 timestamp.

## Built-in Rule Validation

A real interactive `kubectl exec -it ... -- sh` session in `falco-demo/shell-test` generated Falco's built-in `Terminal shell in container` alert at `Notice` priority.

The event included `proc.tty`, `proc.cmdline=sh`, the workload image, `k8s.pod.name=shell-test`, `k8s.ns.name=falco-demo`, and the MITRE execution tag `T1059`.

## Interpretation

An interactive shell in a container is an investigation signal, not automatic proof of malicious activity. Production use should correlate the event with Kubernetes audit logs and tune expected administrative workflows.
