#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
cluster=devops-notes
node_image=kindest/node:v1.37.0@sha256:a1ed56cfb0e7b93589bdf97c8cd566405a265939e3620fc4f5de89adff580ae5
case "${1:-help}" in
  up)
    if .local/bin/kind get clusters | grep -Fxq "$cluster"; then
      test -f .local/cluster-owned || { echo 'Existing cluster is not owned by this checkout; refusing to modify it.' >&2; exit 1; }
      .local/bin/kind export kubeconfig --name "$cluster" --kubeconfig "$PWD/.local/kubeconfig"
    else
      .local/bin/kind create cluster --name "$cluster" --image "$node_image" --config cluster/kind.yaml --kubeconfig "$PWD/.local/kubeconfig" --wait 5m
      printf '%s\n' "$cluster" > .local/cluster-owned
    fi
    chmod 600 .local/kubeconfig
    bash scripts/k.sh apply -f manifests/namespace.yaml
    bash scripts/k.sh create secret generic notes-db --from-file=password=.local/db-password --dry-run=client -o yaml | bash scripts/k.sh apply -f -
    bash scripts/k.sh apply -f manifests/config.yaml -f manifests/postgres.yaml
    bash scripts/k.sh rollout status statefulset/postgres --timeout=240s
    bash scripts/k.sh apply -f manifests/migrate.yaml
    bash scripts/k.sh wait --for=condition=complete job/notes-schema --timeout=180s
    bash scripts/k.sh apply -f manifests/api.yaml
    bash scripts/k.sh rollout status deployment/notes-api --timeout=240s
    echo 'Open http://localhost:8005'
    ;;
  status)
    bash scripts/k.sh get nodes
    bash scripts/k.sh get deploy,statefulset,pods,services,pvc,jobs
    ;;
  down)
    test -f .local/cluster-owned || { echo 'Ownership marker missing; refusing to delete a cluster.' >&2; exit 1; }
    .local/bin/kind delete cluster --name "$cluster"
    python3 -c 'from pathlib import Path; Path(".local/cluster-owned").unlink(missing_ok=True); Path(".local/kubeconfig").unlink(missing_ok=True)'
    ;;
  *) echo 'Usage: bash scripts/lab.sh {up|status|down}' ;;
esac
