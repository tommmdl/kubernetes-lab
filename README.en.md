# Kubernetes: the notes app in a local cluster

English · [Português](README.md)

## Current API: Alpine, including OpenTelemetry

The main labs now use the released Alpine digests: basic API for Docker/basic Kubernetes and instrumented API for the GitOps tracing workload. Backups were restored separately and actual image rollback preserved notes written after cutover. Database images, credentials and volumes stay in place. [Adoption, tested rollback and complete evidence](https://github.com/tommmdl/security-lab/blob/main/docs/api-adoption.en.md). Retained Debian findings remain visible.

## Current database: Alpine, with a tested rollback

The labs now use the tested PostgreSQL Alpine image by digest. Adoption used logical backups and new volumes; original Debian volumes are retained. Actual API rollback preserved a note written after cutover. Read the [migration, backup and recovery procedure](docs/postgres-adoption.en.md). Earlier security reports remain available.

The app already runs in Docker. Now the idea is to see what changes in a cluster: who recreates a Pod, how requests reach the replicas and what needs to survive when the database restarts.

This project uses the GHCR image built from [docker-lab](https://github.com/tommmdl/docker-lab). The API has two replicas; PostgreSQL uses a StatefulSet and a persistent volume. Its kind cluster is separate from other environments on the machine.

[![Tests](https://github.com/tommmdl/kubernetes-lab/actions/workflows/test.yml/badge.svg)](https://github.com/tommmdl/kubernetes-lab/actions/workflows/test.yml)

## Getting started

Use Linux/WSL with accessible Docker, Python 3, Bash and curl. Automatic kind/kubectl installation supports Linux x86_64. Initial downloads need internet access, image storage space and an available port 8005.

```bash
git clone https://github.com/tommmdl/kubernetes-lab.git
cd kubernetes-lab
bash scripts/prepare.sh
bash scripts/lab.sh up
bash scripts/lab.sh status
```

Open **http://localhost:8005**. The interface switches between Portuguese and English. Access is local; this learning API has no user authentication.

The cluster is named `devops-notes`, with application namespace `notes-lab`. The `scripts/k.sh` wrapper always uses this project's kubeconfig/context rather than the terminal's global context.

## What to look for

1. Create a note and delete an API Pod. Watch the Deployment replace it.
2. Scale the API to three replicas and inspect the Service.
3. Recreate the database Pod and see what the PVC preserves.
4. Try a missing image, inspect the failed rollout and roll back.

```bash
bash scripts/k.sh get pods -o wide
bash scripts/k.sh scale deployment/notes-api --replicas=3
bash scripts/k.sh rollout status deployment/notes-api
bash scripts/k.sh apply -f manifests/api.yaml
```

The last command restores the declared file configuration, including two replicas. The [usage guide](docs/guide.en.md) explains the components and how to investigate each scenario.

## Checking the project

```bash
python3 tests/verify.py
```

The test uses only this cluster/namespace, creates its own note and removes it afterward. It replaces Pods, scales the API, checks persistence and introduces a missing-image update followed by rollback. Database Pod replacement causes a brief interruption while it returns.

[Recorded results](docs/validation.en.md) explain what actually ran, with environment details and exercise limits. The local cluster stays running after tests so you can explore.

All 24 checks passed locally and in GitHub Actions, including Pod recovery, persistence, scaling and rollback.

## When you are done

```bash
bash scripts/lab.sh down
```

**This deletes the cluster and database contents, including PVCs.** The volume protects data during Pod replacement; it is not a backup outside the cluster. The script only deletes the cluster matching this project's name and local ownership marker.

Kind, kubectl, password and kubeconfig remain under ignored `.local/`. Keep the password while retaining the database: generating a new file does not rotate the initialized PostgreSQL credential.

[See the other portfolio projects](https://github.com/tommmdl/devops-portfolio)

## Next step: GitOps

[argocd-lab](https://github.com/tommmdl/argocd-lab) uses this application and cluster to explore drift and self-heal. After Argo CD takes over, change configuration through that repository; scaling exercises here may be automatically reverted.

To watch application health, [monitoring-lab](https://github.com/tommmdl/monitoring-lab) adds Prometheus, Grafana and HTTP probes to the same cluster, with an alert drill that keeps the API available.

To practice how configuration reaches containers, [kubernetes-config-lab](https://github.com/tommmdl/kubernetes-config-lab) provides 26 exercises on environment, ConfigMaps, Secrets, TLS and Downward API in a separate namespace, with Portuguese and English solutions.

## Previous security stages (historical evidence)

The earlier image pins included the first API and PostgreSQL remediation round. At that stage PostgreSQL stayed on version 17 and Bookworm; its gosu helper and Go dependencies changed. The API updates Flask/liblzma and removes installation-only pip tooling from runtime. See the [full before/after reports](https://github.com/tommmdl/security-lab/blob/main/docs/remediation.en.md). Remaining findings still block the separate security gate.

Remediation validation: 23 Compose checks, a controlled restore of three notes from the original PostgreSQL image into the rebuilt image, and 19 local tracing checks. The running Argo CD application is Synced/Healthy and retains the same PVC. Full evidence and remaining issues are linked above.

The [PostgreSQL critical-finding review](https://github.com/tommmdl/security-lab/blob/main/docs/postgresql-critical.en.md) removes unused SQLite and limits the application role. Existing volumes require explicit `lab-db-harden` execution after image replacement; initialization hooks do not rerun. For this Kubernetes lab, use `bash scripts/harden-db.sh` from the kubernetes-lab checkout after saving data/globals/HBA backups. Maintenance then uses `psql -U notes_admin -d notes` through the database container Unix socket. Two critical scan findings remain visible and blocking.

After the PostgreSQL critical review, the API uses an ordinary SQL role and the database image no longer includes SQLite. The application remains healthy; 24 Kubernetes and 19 tracing checks passed in CI. The [full review](https://github.com/tommmdl/security-lab/blob/main/docs/postgresql-critical.en.md) keeps both remaining critical findings and their limits visible.

The [API HIGH-finding review](https://github.com/tommmdl/security-lab/blob/main/docs/api-high-review.en.md) groups 44 occurrences into eight CVEs and checks their actual prerequisites. Resource bounds and privilege restrictions mitigate exposure; the API image stays blocked and full findings remain visible.
