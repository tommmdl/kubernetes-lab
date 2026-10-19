#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
exec bash scripts/k.sh exec postgres-alpine-0 -- /usr/local/bin/lab-db-harden
