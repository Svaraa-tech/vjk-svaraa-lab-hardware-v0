#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/env.sh"

API_VENV="$ROOT/services/api/.venv"
LOG_DIR="$ROOT/.workbench/logs"
mkdir -p "$LOG_DIR"

if [[ ! -x "$API_VENV/bin/uvicorn" ]]; then
  echo "API venv missing — run make setup" >&2
  exit 1
fi
if [[ ! -d "$ROOT/apps/workbench/node_modules" ]]; then
  echo "workbench node_modules missing — run make setup" >&2
  exit 1
fi

# Stop previous Lab listeners
bash "$ROOT/scripts/stop.sh" || true

# Seed DB if missing
if [[ ! -f "$ROOT/.workbench/lab.db" ]]; then
  (
    cd "$ROOT/services/api"
    "$API_VENV/bin/uvicorn" app.main:app --host 127.0.0.1 --port 18001
  ) >"$LOG_DIR/api_seed.log" 2>&1 &
  seed_pid=$!
  sleep 1
  curl -sS -X POST 'http://127.0.0.1:18001/lab/v1/board/import?force=true' >/dev/null || true
  kill "$seed_pid" 2>/dev/null || true
  wait "$seed_pid" 2>/dev/null || true
fi

# Detach into new sessions so IDE/agent shells cannot kill the servers on exit
python3 - "$ROOT" "$API_VENV" "$LOG_DIR" <<'PY'
import os, subprocess, sys, pathlib

root, api_venv, log_dir = map(pathlib.Path, sys.argv[1:4])
log_dir.mkdir(parents=True, exist_ok=True)

api_log = open(log_dir / "api.log", "w")
web_log = open(log_dir / "web.log", "w")

api = subprocess.Popen(
    [str(api_venv / "bin" / "uvicorn"), "app.main:app", "--host", "127.0.0.1", "--port", "18001", "--reload"],
    cwd=str(root / "services" / "api"),
    stdout=api_log,
    stderr=subprocess.STDOUT,
    stdin=subprocess.DEVNULL,
    start_new_session=True,
)
(log_dir / "api.pid").write_text(str(api.pid))

web = subprocess.Popen(
    ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"],
    cwd=str(root / "apps" / "workbench"),
    stdout=web_log,
    stderr=subprocess.STDOUT,
    stdin=subprocess.DEVNULL,
    start_new_session=True,
    env=os.environ.copy(),
)
(log_dir / "web.pid").write_text(str(web.pid))
print(f"started api={api.pid} web={web.pid}")
PY

sleep 1
# Ensure board seed exists after API is up
curl -sS -X POST 'http://127.0.0.1:18001/lab/v1/board/import?force=false' >/dev/null || true

echo ""
echo "Svaraa V0 Lab (SIM) — servers running in background"
echo "  Workbench: http://127.0.0.1:5173/"
echo "  API:       http://127.0.0.1:18001/lab/v1/health"
echo "  Logs:      $LOG_DIR/"
echo "  Stop:      make stop"
echo ""
echo "Open in your system browser (Safari/Chrome), not only the Cursor preview."
if command -v open >/dev/null 2>&1; then
  open "http://127.0.0.1:5173/" || true
fi

echo "Press Ctrl+C to detach this terminal (servers keep running until make stop)."
tail -f "$LOG_DIR/api.log" "$LOG_DIR/web.log"
