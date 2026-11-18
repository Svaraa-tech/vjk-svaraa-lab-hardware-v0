# Implementation — SV0-01.02

Approved plan: **v0.1**  
Implemented: 2026-11-17 / 2026-11-18 UTC

## What changed and why

Created a reproducible Lab repository layout with pinned JS/Python deps, host-test wrappers, minimal FastAPI health endpoints, and a theme-aware workbench shell — without claiming Kanban/simulator product features.

## Actual artifacts

| Path | Notes |
| --- | --- |
| `.gitignore`, local `.git/` | Initialized; no remote |
| `README.md`, `Makefile`, `scripts/{doctor,setup,test,dev,stop,env}.sh` | Developer loop |
| `apps/workbench/` | Vite 7.3.8 + React 19.3.1 + TS 5.9.3; svaraa.ai tokens; SIM banner |
| `services/api/` | FastAPI 0.121.2; `/v1/health`, `/lab/v1/health` |
| `services/simulator/` | Stub README |
| `firmware/core/sos_core.hpp` | Working copy + SOURCE_MAPPING |
| `contracts/` | Working copies + PROVENANCE.json |
| `tests/host/` | Adapted pack baselines |
| `simulation/*`, `hardware/` | Structure stubs |
| `evidence/SV0-01.02/latest/` | Versions, test logs, health JSON, build log |

## Deviations / limitations

- Tailwind deferred; plain CSS variables implement the approved theme (same tokens).
- Browser MCP could not open `http://127.0.0.1:5173` (connection refused from isolated browser). Shell curl returned HTTP 200; manual UI review needed.
- Homebrew still not installed (sudo).
- No Kanban/simulator logic (by plan).
- `npm audit` reported vulnerabilities in the Vite tree; not remediated in this ticket (record only).

## Known follow-ups

- SV0-01.03 typed HAL ports
- WB-001 import / WB-002 real navigation
- Optional `npm audit` remediation ticket
