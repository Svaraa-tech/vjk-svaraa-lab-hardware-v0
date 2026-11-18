#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/env.sh"

ok=0
warn=0

echo "Svaraa V0 Lab doctor"
echo "root=$ROOT"
echo "arch=$(uname -m)  os=$(sw_vers -productVersion 2>/dev/null || uname -s)"

if xcode-select -p >/dev/null 2>&1; then
  echo "OK   xcode-select: $(xcode-select -p)"
  ok=$((ok + 1))
else
  echo "MISS xcode-select"
  warn=$((warn + 1))
fi

if command -v c++ >/dev/null 2>&1 && c++ --version >/dev/null 2>&1; then
  echo "OK   c++: $(c++ --version | head -1)"
  ok=$((ok + 1))
else
  echo "MISS c++"
  warn=$((warn + 1))
fi

if command -v node >/dev/null 2>&1; then
  echo "OK   node: $(node --version) ($(command -v node))"
  ok=$((ok + 1))
else
  echo "MISS node"
  warn=$((warn + 1))
fi

if command -v npm >/dev/null 2>&1; then
  echo "OK   npm: $(npm --version)"
  ok=$((ok + 1))
else
  echo "MISS npm"
  warn=$((warn + 1))
fi

if [[ -n "${SVARAA_PYTHON:-}" && -x "${SVARAA_PYTHON}" ]]; then
  echo "OK   python: $($SVARAA_PYTHON --version) ($SVARAA_PYTHON)"
  ok=$((ok + 1))
elif command -v python3 >/dev/null 2>&1; then
  echo "OK   python: $(python3 --version) ($(command -v python3))"
  ok=$((ok + 1))
else
  echo "MISS python"
  warn=$((warn + 1))
fi

if command -v uv >/dev/null 2>&1; then
  echo "OK   uv: $(uv --version)"
  ok=$((ok + 1))
else
  echo "INFO uv: not required when python venv works"
fi

if command -v brew >/dev/null 2>&1; then
  echo "OK   brew: $(brew --version | head -1)"
else
  echo "INFO brew: not installed (user-local Node/uv is acceptable)"
fi

# PlatformIO + Wokwi subset (WB-017)
WOKWI="$ROOT/simulation/wokwi"
PIO_BIN=""
if command -v pio >/dev/null 2>&1; then
  PIO_BIN="$(command -v pio)"
elif [[ -x "$HOME/Library/Python/3.9/bin/pio" ]]; then
  PIO_BIN="$HOME/Library/Python/3.9/bin/pio"
elif [[ -x "$HOME/Library/Python/3.12/bin/pio" ]]; then
  PIO_BIN="$HOME/Library/Python/3.12/bin/pio"
fi
if [[ -n "$PIO_BIN" ]]; then
  echo "OK   platformio: $($PIO_BIN --version 2>/dev/null | head -1) ($PIO_BIN)"
  ok=$((ok + 1))
else
  echo "MISS platformio (pio) — needed for Wokwi firmware build"
  warn=$((warn + 1))
fi

if [[ -f "$WOKWI/diagram.json" && -f "$WOKWI/platformio.ini" && -f "$WOKWI/wokwi.toml" ]]; then
  echo "OK   wokwi project: simulation/wokwi/{diagram,platformio,wokwi.toml}"
  ok=$((ok + 1))
else
  echo "MISS wokwi project files under simulation/wokwi"
  warn=$((warn + 1))
fi

FW="$WOKWI/.pio/build/sim/firmware.bin"
if [[ -f "$FW" ]]; then
  HASH=$(shasum -a 256 "$FW" | awk '{print $1}')
  echo "OK   firmware.bin sha256=$HASH bytes=$(wc -c < "$FW" | tr -d ' ')"
  ok=$((ok + 1))
else
  echo "MISS firmware.bin — run: (cd simulation/wokwi && pio run -e sim)"
  warn=$((warn + 1))
fi

if command -v wokwi-cli >/dev/null 2>&1; then
  echo "OK   wokwi-cli: $(command -v wokwi-cli) (optional)"
else
  echo "INFO wokwi-cli: not installed (optional headless)"
fi

echo "summary: ok=$ok missing=$warn"
exit "$warn"
