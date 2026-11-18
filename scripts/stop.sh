#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/.workbench/logs"

for f in "$LOG_DIR/api.pid" "$LOG_DIR/web.pid"; do
  if [[ -f "$f" ]]; then
    pid=$(cat "$f" || true)
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      echo "Stopping PID $pid from $f"
      kill "$pid" 2>/dev/null || true
      # kill child npm/node tree if needed
      pkill -P "$pid" 2>/dev/null || true
    fi
    rm -f "$f"
  fi
done

for port in 18001 18000 8000 8001 5173; do
  pids=$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    echo "Stopping listener(s) on :$port -> $pids"
    kill $pids 2>/dev/null || true
    sleep 0.3
    # Detached start_new_session processes may ignore SIGTERM
    still=$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
    if [[ -n "${still:-}" ]]; then
      kill -9 $still 2>/dev/null || true
    fi
  fi
done
echo "stop done"
