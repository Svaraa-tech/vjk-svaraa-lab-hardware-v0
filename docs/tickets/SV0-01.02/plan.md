# Plan — SV0-01.02 Create reproducible repository

**Plan revision:** v0.1  
**Profile:** SIM  
**Depends on:** SV0-01.01 (accepted)

## Ticket and source scope

Source **1012 / SV0-01.02**: create core, board adapters, contracts, apps, backend, tests and evidence folders; pin tool versions. Acceptance: clean checkout reproduces host tests and records compiler/core versions.

## Why this is next

Unblocked after 01.01. Required before HAL ports (01.03), workbench import (WB-001), and any app/API implementation.

## Concrete steps

1. **Initialize Git** in `Svaraa_V0_Lab/` (local only; no remote/push). Add `.gitignore` for `.workbench/`, `node_modules/`, `.venv/`, build outputs, local credentials.
2. **Create README layout** matching approved architecture:
   - `apps/workbench/` — Vite+React+TS placeholder (shell only: title + SIMULATED + theme CSS variables from ADR-0002; no Kanban/simulator logic yet)
   - `services/api/` — FastAPI minimal `/v1/health` + `/lab/v1/health`
   - `services/simulator/` — package stub + README (orchestrator later WB-005)
   - `firmware/core/` — reviewed working copy of `sos_core.hpp` with source mapping note
   - `firmware/host-bridge/` — stub README + future JSON-lines interface note (implementation can be minimal compile of core tests)
   - `firmware/nano/`, `firmware/nicla/` — empty placeholders with README (pseudocode stays in references)
   - `contracts/` — copies or symlinks/mapping from pack contracts into working tree (byte-preserved copies with provenance)
   - `simulation/{models,fixtures,scenarios,wokwi}/` — seed from pack scenarios; wokwi copy deferred or stub
   - `hardware/` — derived registry stub README
   - `tests/` — wrappers that run pack baselines + future project tests
   - Keep existing `docs/`, `data/`, `evidence/`, `references/`, `scripts/`
3. **Pin versions** (actual current on this Mac / docs):
   - Node `22.21.1` (engines field); npm lockfile via `npm create` / install
   - Python `>=3.12,<3.13` via `pyproject.toml` + uv lock
   - React 19.x + Vite 6.x + TypeScript 5.x (pin exact at install time from npm)
   - FastAPI + Uvicorn + pydantic pinned in uv lock
   - Optional Tailwind for theme tokens — yes, lightweight, maps CSS vars from `ui_theme_svaraa.md`
4. **Root developer commands** (Makefile or `package.json` scripts + `scripts/`):
   - `make doctor` — check node/python/c++/paths without installing
   - `make setup` — install JS + Python deps from lockfiles (project-local)
   - `make test` — run C++ host core + Python contracts (and any new smoke)
   - `make dev` — start API + workbench with printed URLs (minimal)
   - Document in root `README.md` (human setup); do not replace `README_CURSOR_SVARAA_V0.md`
5. **Host-test reproducibility**
   - `firmware/core` + `tests` path so `make test` rebuilds/runs 31 C++ checks and 15 Python checks against working `contracts/`
   - Record compiler (`c++ --version`), node, python, and core file hash in `evidence/SV0-01.02/<run-id>/`
6. **Theme foundation only**
   - Workbench loads light/dark CSS variables from ADR-0002; toggle persists in localStorage; page shows project name + **SIMULATED**
7. **Update checkpoints** (`CURRENT_STATE`, `NEXT_ACTION`, bootstrap board fields)
8. **Demonstrate** doctor/setup/test/dev smoke; request acceptance

## Affected files / contracts

| Path | Action |
| --- | --- |
| `.gitignore`, optional `.gitattributes` | Create |
| `README.md` | Create (setup/run) |
| `Makefile` or dual npm/make | Create |
| `apps/workbench/**` | Scaffold Vite app |
| `services/api/**` | Minimal FastAPI |
| `services/simulator/**` | Stub |
| `firmware/**` | Core copy + stubs |
| `contracts/**` | Working copies from pack |
| `simulation/**`, `hardware/**`, `tests/**` | Structure + wrappers |
| `package.json` / lockfiles / `pyproject.toml` / `uv.lock` | Pin |
| `scripts/env.sh`, `scripts/doctor.sh` | Extend |
| App product features, board, simulator engine | **not in this ticket** |

## UI behavior affected

Minimal workbench shell only: Svaraa branding, theme toggle (svaraa.ai tokens), SIMULATED banner, placeholder nav labels for Board/Simulator (non-functional or static). No scenario engine, no Kanban cards.

## Mocks vs real local implementation

| Piece | Real now? |
| --- | --- |
| Folder layout + lockfiles | Real |
| `make test` host baselines | Real |
| FastAPI `/health` | Real local HTTP |
| Board/simulator domain | Stub only |
| Notifications | Not present |

## Acceptance and negative tests

| ID | Check |
| --- | --- |
| A1 | Documented folders exist per architecture |
| A2 | Lockfiles pin Node/Python deps; engines recorded |
| A3 | `make doctor` reports toolchain |
| A4 | `make test` re-runs C++ 31 + Python 15 successfully |
| A5 | Evidence records compiler/node/python/core hash |
| A6 | Workbench builds and shows light/dark + SIMULATED |
| A7 | API health returns 200 on loopback |
| N1 | No claim that Kanban/simulator are implemented |
| N2 | No physical gates marked passed |
| N3 | References/originals unchanged |

## Demonstration

1. `source scripts/env.sh && make doctor`  
2. `make setup && make test`  
3. `make dev` → open workbench URL, toggle theme; curl API health  

## Risks, assumptions, rollback

| Risk | Mitigation |
| --- | --- |
| Vite/React major version churn | Pin exact versions in lockfile; record in evidence |
| Copying contracts drifts from pack | Provenance file with source hashes; originals untouched |
| Scope creep into WB-002 | Explicit shell-only UI |
| Git init in nested workspace | Init inside `Svaraa_V0_Lab` only |

Rollback: remove new scaffold dirs/lockfiles; keep docs/references/evidence history.

## Open decisions (recommendations)

1. **Package manager:** npm (ships with Node) — recommend **yes** (no pnpm/yarn required).  
2. **Tailwind:** yes for token mapping — recommend **yes**.  
3. **Git remote:** none — recommend **local only** until you ask.  
4. **Homebrew:** still optional — continue user-local Node/uv.

## Approval requested

Approve **SV0-01.02 plan v0.1** only. No scaffolding until approval.
