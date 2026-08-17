# Security Gates Video Demo

## Goal

Record a 75 to 90 second landscape walkthrough of K8s AutoGuard's preventive security controls. The video should prove what happens, not merely describe features.

## Recording Setup

- Record at 1920x1080 and 30 frames per second.
- Use a terminal font size of at least 20 points.
- Record one terminal window and one browser window. Keep notifications, tokens, and personal tabs out of frame.
- Use the Windows Snipping Tool screen recorder or OBS. Start recording before you run the guided script.

## Demo Flow

Open a terminal in the repository and run:

```bash
./scripts/run-security-gates-demo.sh --interactive
```

The script pauses after every scene. Speak over the visible proof, then press Enter when you are ready to continue.

| Time | Scene | What to say |
| --- | --- | --- |
| 0-10s | Title and repository | "This is K8s AutoGuard, my Kubernetes DevSecOps lab. I am showing how it prevents unsafe workloads before they run." |
| 10-25s | Cilium status | "The two-node KIND cluster is healthy. Cilium provides identity-aware network enforcement and Hubble visibility." |
| 25-45s | Kyverno output | "Kyverno admits the secure Pod, then rejects the insecure Pod at the API server. The denial names the missing Restricted Pod Security controls." |
| 45-60s | Trivy output | "Before deployment, Trivy scans the policy and secure fixture. This gate fails on high or critical misconfigurations; this result is clean." |
| 60-75s | GitHub Actions | "The same checks run on every pull request and main-branch push. The final run is successful." |
| 75-90s | Closing frame | "K8s AutoGuard now has preventive admission control and supply-chain scanning, layered with Cilium network controls and runtime detection work." |

## Browser Evidence

After Scene 4, switch briefly to the repository's Actions tab and show the green **Security scans** run. Then open the validation evidence file:

`docs/evidence/004-preventive-security-validation.md`

## Cleanup

The Kyverno demo creates only its namespace because its Pod checks use API-server dry runs. Remove that namespace after recording:

```bash
./scripts/validate-kyverno-policy-demo.sh --cleanup
```

## Suggested Title

`K8s AutoGuard: Preventing Unsafe Kubernetes Workloads Before Runtime`
