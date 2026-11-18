#!/usr/bin/env bash
# Copy diagram + built firmware into the workbench public/ bundle for Pages embed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/simulation/wokwi"
DST="$ROOT/apps/workbench/public/wokwi"
BIN="$SRC/.pio/build/sim/firmware.bin"
ELF="$SRC/.pio/build/sim/firmware.elf"

mkdir -p "$DST"
cp "$SRC/diagram.json" "$DST/diagram.json"
if [[ ! -f "$BIN" || ! -f "$ELF" ]]; then
  echo "Missing firmware — run: (cd simulation/wokwi && PLATFORMIO_CORE_DIR=.platformio pio run -e sim -c platformio_local.ini)" >&2
  exit 1
fi
cp "$BIN" "$DST/firmware.bin"
cp "$ELF" "$DST/firmware.elf"
ls -lh "$DST"
echo "Synced Wokwi public assets."
