#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/env.sh"

PY="${SVARAA_PYTHON:-python3}"

echo "== workbench npm install =="
(cd "$ROOT/apps/workbench" && npm install)

echo "== api python venv =="
(cd "$ROOT/services/api" && "$PY" -m venv .venv && .venv/bin/pip install -U pip && .venv/bin/pip install -r requirements.txt)

echo "== host-test python venv =="
(cd "$ROOT/tests/host" && "$PY" -m venv .venv && .venv/bin/pip install -U pip && .venv/bin/pip install -r requirements.txt)

echo "setup complete"
