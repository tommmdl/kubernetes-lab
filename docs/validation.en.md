# What happened in the cluster

[Português](validation.md) · [Back to the project](../README.en.md)

All **24 checks passed locally and in [GitHub Actions](https://github.com/tommmdl/kubernetes-lab/actions/runs/39080854670)**. Local execution finished at 17/10/2026 20:53:52 America/Sao_Paulo. CI ran commit `8c2510eb24fdcd0dbdfa1af5faa8e2c8f8c28a0c`.

## The exercises in practice

| Scenario | Observed behavior |
| --- | --- |
| Startup | Two Ready nodes, two API replicas and a completed schema Job |
| Storage | PostgreSQL PVC Bound |
| HTTP | Health/readiness 200, served page and note creation 201 |
| Deleted API Pod | Deployment replaced it; the note remained available |
| Scaling | Three ready replicas; applying the manifest restored two |
| Deleted database Pod | StatefulSet replaced it, preserving the same PVC and note |
| Missing image | Pull error observed; previous replicas remained available |
| Rollback | Pinned working image restored and note readable |
| Test cleanup | Only the test-created note was deleted |

The invalid update was deliberate. The test checked the pull error and requested the old API before undoing the change. This demonstrates the observed scenario, not uninterrupted availability across every kind of failure.

## What was already on the machine

Existing lab folders and containers were inspected before creating this cluster. Earlier Kubernetes and Argo CD projects were present. Hashes of 23 documentation, manifest and script files were compared before/after; those checked files remained unchanged.

The new environment uses a different cluster name and namespace. No credentials were copied from earlier projects. Personal paths, VM disk details and the computer inventory remain in a local report excluded from this repository.

## Evidence

- [Local results and checks](../evidence/local-results.json)
- [CI results and checks](../evidence/ci-results.json)
- [Workflow steps and metadata](../evidence/ci-run.json)
- [Cluster versions](../evidence/runtime.json)
- [Earlier-project preservation check](../evidence/preservation.json)
- [Complete test implementation](../tests/verify.py)

Local versions: kind 0.33.0, Kubernetes 1.37.0, kubectl 1.37.1 and Docker Engine 29.1.3. The API was pulled from GHCR by digest without a pull token. Password and kubeconfig were excluded from Git and workflow artifacts.

## Where the app remains

The local cluster remains running at http://localhost:8005. CI removed its runner cluster after saving reports; the JSON final-state field describes the moment before CI cleanup.

## Limits that matter

Persistence checks replaced a Pod, without simulating worker, disk or cluster loss. PostgreSQL has one replica and node-local storage. No backup/restore, production traffic, node loss, TLS, user authentication, Ingress, autoscaling or NetworkPolicy checks. The page was verified over HTTP without visual browser automation.

The schema step creates the initial table, not versioned migrations. Preservation checks cover selected project files, not a forensic audit of every partition. Technical execution was assistant-assisted with owner authorization.
