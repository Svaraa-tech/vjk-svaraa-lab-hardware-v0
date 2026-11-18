# Proposed architecture — Svaraa V0 Lab

Revision: **arch-v0.1** (P0 proposal; not implemented)  
Status: awaiting owner approval with roadmap

## Goals

One local web workbench with:

1. **Project Board** — Jira-style Kanban over the original 87-item backlog, plans, approvals, tests, evidence.
2. **Device Simulator** — interactive pendant/hardware view driven by a shared domain/simulation engine and real traces (not decorative animation).

Default profile SIM + mock notifications. Path preserved to no-solder BENCH, phone, and V1.

## Recommended stack (README default, confirmed for this Mac after tooling install)

| Layer | Choice | Why |
| --- | --- | --- |
| Web app | React + TypeScript + Vite | Fast local DX; fits board + multi-view simulator |
| UI | Accessible components; Tailwind optional | Engineering density needs legible contrast; plum/gold identity |
| Graphs | SVG + React Flow | Selectable hardware/system graphs and animated edges tied to traces |
| Charts | Maintained TS chart lib (pin at install) | Sensor time series aligned to simulation clock |
| 3D | Optional Three.js later | Not required for first useful demo |
| API | FastAPI (Python) | Matches pack contracts/tests language; orchestration + mocks |
| Persistence | SQLite + migrations + FK | Local durable board/incidents/traces; domain repos isolate future DB change |
| Safety core | Existing C++17 `sos_core.hpp` via JSON-lines host bridge | Single reducer source of truth |
| Contracts | JSON Schema / OpenAPI + runtime validation | Boundary checks; freeze incomplete schemas before codegen |
| Tests | unittest/pytest, C++ host tests, Playwright | Pack baselines retained; browser flows for board/simulator |
| Firmware emu | Separate PlatformIO/Wokwi project later | Not a substitute for the behavioral simulator |

Pin exact versions during SV0-01.02 after CLT/Node/Python are available. No Docker, paid APIs, or cloud required for SIM.

## Process topology (local)

```text
Browser (Board | Simulator projections)
    │  HTTP + /lab/v1 WebSocket
    ▼
services/api  ──► SQLite (.workbench/)
    │
    ├── services/simulator (virtual clock, models, scenarios, traces)
    │         │
    │         └── firmware/host-bridge ──► firmware/core (sos_core)
    └── mock adapters (notifications, missing radios/hardware)
```

- Browser sends commands and renders projections.
- Domain engine owns behavior and ordering.
- API validates and persists product + workbench actions.
- Trace events drive edge animations; replay is read-only.

## Project layout (target after foundation approval)

Matches README §8: `apps/workbench/`, `services/api/`, `services/simulator/`, `firmware/{core,host-bridge,nano,nicla}/`, `contracts/`, `simulation/`, `hardware/`, `docs/`, `data/`, `.workbench/`, `tests/`, `evidence/`, `scripts/`.

## Authority rules

| Concern | Authority |
| --- | --- |
| Runtime board state | Backend DB (after import); until then `data/seeds/board_bootstrap_v0.1.json` |
| Original ticket text | Immutable source CSV/plan records |
| Ticket plans | `docs/tickets/<id>/plan.md` content digest |
| Approvals | Persisted decision log (human only) |
| UI prefs | localStorage only |

## Dependency substitution (SIM)

An owner-approved mock interface may unlock a **specific SIM scope** via an explicit substitution record. It does not close the original physical ticket or parent story.

## Explicit non-goals for early phases

- Real emergency providers, Find My data API, cellular modem, battery gauge in USB baseline
- Claiming Wokwi covers ESP32-S3 I2S / BLE / I2C target mode
- Dual reducers (TS/WASM) without ADR + fixture parity

## ADRs deferred until needed

- ADR: TypeScript/WASM core parity (only if bridge proves insufficient)
- ADR: Nicla health/command-result byte layouts freeze
- ADR: Duplicate idempotent ingest response convention
