#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
mkdir -p .local/bin
chmod 700 .local
if [ "$(uname -s)" != Linux ] || [ "$(uname -m)" != x86_64 ]; then
  echo 'Automatic installation supports Linux x86_64. Use WSL or install the pinned binaries in .local/bin.' >&2
  exit 1
fi
if [ ! -x .local/bin/kind ]; then
  base=https://github.com/kubernetes-sigs/kind/releases/download/v0.33.0
  curl --fail --location "$base/kind-linux-amd64" -o .local/kind-download
  curl --fail --location "$base/kind-linux-amd64.sha256sum" -o .local/kind.sha256
fi
if [ ! -x .local/bin/kubectl ]; then
  base=https://dl.k8s.io/release/v1.37.1/bin/linux/amd64
  curl --fail --location "$base/kubectl" -o .local/kubectl-download
  curl --fail --location "$base/kubectl.sha256" -o .local/kubectl.sha256
fi
python3 - <<'PY'
import hashlib,secrets
from pathlib import Path
p=Path('.local')
for tool in ['kind','kubectl']:
    target=p/'bin'/tool
    if not target.exists():
        data=(p/(tool+'-download')).read_bytes()
        expected=(p/(tool+'.sha256')).read_text().split()[0]
        if hashlib.sha256(data).hexdigest()!=expected:
            raise SystemExit(tool+' checksum mismatch')
        target.write_bytes(data)
        target.chmod(0o755)
secret=p/'db-password'
if not secret.exists():
    secret.write_text(secrets.token_urlsafe(32))
secret.chmod(0o600)
PY
.local/bin/kind version
.local/bin/kubectl version --client
