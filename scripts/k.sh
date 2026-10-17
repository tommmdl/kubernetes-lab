#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
exec .local/bin/kubectl --kubeconfig "$PWD/.local/kubeconfig" --context kind-devops-notes --namespace notes-lab "$@"
