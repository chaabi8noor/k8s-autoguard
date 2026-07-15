## Local Kubernetes Lab

# K8s AutoGuard

An autonomous DevSecOps platform for detecting, analyzing, and remediating Kubernetes security events.

> Current milestone: reproducible local Kubernetes baseline.

### Prerequisites

- Docker Desktop with WSL 2 integration
- kubectl
- kind

### Create the cluster

```bash
./scripts/create-cluster.sh
