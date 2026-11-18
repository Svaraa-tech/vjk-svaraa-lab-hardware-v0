#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/env.sh"
EV="${SVARAA_EVIDENCE_DIR:-$ROOT/evidence/host_latest}"
mkdir -p "$EV"

echo "== C++ host core =="
c++ -std=c++17 -Wall -Wextra -Werror \
  "$ROOT/tests/host/test_core.cpp" \
  -o "$ROOT/tests/host/svaraa_test_core"
"$ROOT/tests/host/svaraa_test_core" | tee "$EV/host_core.txt"

echo "== C++ HAL mock ports =="
c++ -std=c++17 -Wall -Wextra -Werror \
  "$ROOT/tests/host/test_hal_mock.cpp" \
  -o "$ROOT/tests/host/svaraa_test_hal"
"$ROOT/tests/host/svaraa_test_hal" | tee "$EV/host_hal.txt"

echo "== Python contracts =="
HOST_VENV="$ROOT/tests/host/.venv"
if [[ ! -x "$HOST_VENV/bin/python" ]]; then
  echo "missing tests/host/.venv — run make setup" >&2
  exit 1
fi
(
  cd "$ROOT"
  "$HOST_VENV/bin/python" -m unittest discover -s tests/host -p 'test_*.py' -v
) 2>&1 | tee "$EV/host_contracts.txt"

{
  echo "date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "c++=$(c++ --version | head -1)"
  echo "node=$(node --version 2>/dev/null || true)"
  echo "python=$("$HOST_VENV/bin/python" --version)"
  echo "core_sha256=$(shasum -a 256 "$ROOT/firmware/core/sos_core.hpp" | awk '{print $1}')"
  echo "hal_types_sha256=$(shasum -a 256 "$ROOT/firmware/hal/types.hpp" | awk '{print $1}')"
} | tee "$EV/versions.txt"

echo "tests OK — evidence in $EV"
