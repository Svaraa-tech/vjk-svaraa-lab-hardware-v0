#!/usr/bin/env bash
# WB-020 — headless PIO / firmware smoke → evidence/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EV="$ROOT/evidence/WB-020/latest"
mkdir -p "$EV"
WOKWI="$ROOT/simulation/wokwi"

{
  echo "wokwi_smoke $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "root=$ROOT"
  if command -v pio >/dev/null 2>&1; then PIO=$(command -v pio)
  elif [[ -x "$HOME/Library/Python/3.9/bin/pio" ]]; then PIO="$HOME/Library/Python/3.9/bin/pio"
  else PIO=""; fi
  echo "pio=${PIO:-missing}"
  if [[ -n "$PIO" ]]; then
    (cd "$WOKWI" && "$PIO" run -e sim) || echo "pio_run=FAILED"
  else
    echo "pio_run=SKIPPED"
  fi
  FW="$WOKWI/.pio/build/sim/firmware.bin"
  if [[ -f "$FW" ]]; then
    echo "firmware_present=1"
    shasum -a 256 "$FW"
    ls -la "$FW"
  else
    echo "firmware_present=0"
  fi
  echo "wokwi_cli=$(command -v wokwi-cli || echo missing)"
} | tee "$EV/smoke.txt"

# Also hit Lab API if up
API="${SVARAA_API:-http://127.0.0.1:18001}"
if curl -sf "${API}/lab/v1/wokwi/smoke?run_pio=false" -X POST > "$EV/api_smoke.json"; then
  echo "api_smoke=ok" | tee -a "$EV/smoke.txt"
else
  echo "api_smoke=skipped" | tee -a "$EV/smoke.txt"
fi

echo "evidence=$EV"
