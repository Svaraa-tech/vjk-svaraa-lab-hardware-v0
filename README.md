# Svaraa V0 Lab

Local development workbench for the Svaraa V0 pendant (SIM profile by default).

Full Cursor build contract: [`README_CURSOR_SVARAA_V0.md`](./README_CURSOR_SVARAA_V0.md). Launch guide: [`START_HERE.md`](./START_HERE.md).

## Prerequisites

- Xcode Command Line Tools (`c++`)
- Node.js 22+ and npm
- Python 3.12+

On this Mac, user-local installs are fine:

```sh
source scripts/env.sh
make doctor
```

## Setup

```sh
source scripts/env.sh
make setup
```

## Test (host baselines)

```sh
make test
```

Re-runs the C++ reducer host checks and Python contract tests. Evidence writes under `evidence/SV0-01.02/latest/` when run via `make test`.

## Dev

```sh
make dev
```

- Workbench (Project Board): http://127.0.0.1:5173  
- API health: http://127.0.0.1:18001/v1/health  
- Board summary: http://127.0.0.1:18001/lab/v1/board/summary  
- Wokwi: http://127.0.0.1:18001/lab/v1/wokwi/status (also Device Simulator panel) 

The **Project Board** tab shows all original + workbench tickets, refreshes every 5s, and opens a detail drawer on click.

Update a ticket from the shell:

```sh
scripts/board_set.sh SV0-01.03 Done "accepted"
```

Stop with Ctrl+C or `make stop`.

## Layout

| Path | Role |
| --- | --- |
| `apps/workbench/` | React + Vite shell (theme + placeholders) |
| `services/api/` | FastAPI local API |
| `services/simulator/` | Stub (engine later) |
| `firmware/core/` | Working copy of `sos_core.hpp` |
| `contracts/` | Working contract copies |
| `references/` | Untouched originals + agent pack |
| `docs/` | Plans, decisions, ADRs |

## Profile defaults

- `SVARAA_PROFILE=SIM`
- `notification_provider=mock`
- UI shows **SIMULATED** prominently

Physical / phone / licensed gates remain open until their evidence exists.
