#!/usr/bin/env bash
# WB-023 — workspace PIO build (symlink override) + firmware artifact copy
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WOKWI="$ROOT/simulation/wokwi"
OUT="${1:-$ROOT/evidence/WB-023/latest}"
mkdir -p "$OUT"

export PATH="${HOME}/Library/Python/3.9/bin:${HOME}/Library/Python/3.12/bin:${PATH}"
export PLATFORMIO_SETTING_ENABLE_TELEMETRY=No
# Prefer workspace PlatformIO core with symlinked home packages when present
if [[ -d "$ROOT/.workbench/platformio/platforms" || -L "$ROOT/.workbench/platformio/platforms" ]]; then
  export PLATFORMIO_CORE_DIR="$ROOT/.workbench/platformio"
fi

PIO_BIN="$(command -v pio || true)"
if [[ -z "$PIO_BIN" && -x "$HOME/Library/Python/3.9/bin/pio" ]]; then
  PIO_BIN="$HOME/Library/Python/3.9/bin/pio"
fi
if [[ -z "$PIO_BIN" ]]; then
  echo "pio missing" | tee "$OUT/build.txt"
  exit 2
fi

CFG="$WOKWI/platformio.ini"
if [[ -f "$WOKWI/platformio_local.ini" ]]; then
  CFG="$WOKWI/platformio_local.ini"
fi

{
  echo "wokwi_build $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "pio=$PIO_BIN"
  echo "cfg=$CFG"
  echo "PLATFORMIO_CORE_DIR=${PLATFORMIO_CORE_DIR:-default}"
  (cd "$WOKWI" && "$PIO_BIN" run -e sim -c "$(basename "$CFG")")
} 2>&1 | tee "$OUT/build.txt"

FW="$WOKWI/.pio/build/sim/firmware.bin"
if [[ ! -f "$FW" ]]; then
  echo "firmware missing after build" | tee -a "$OUT/build.txt"
  exit 1
fi
cp -f "$FW" "$OUT/firmware.bin"
shasum -a 256 "$FW" | tee "$OUT/firmware.sha256"
ls -la "$FW" | tee -a "$OUT/build.txt"
echo "artifact=$OUT/firmware.bin"
