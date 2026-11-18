# Source conflicts and discovery gaps

Schema: informal register for P0. Status values: `open`, `proposed`, `resolved`, `accepted`.

## SC-001 — Workspace open path vs Lab project root

| Field | Value |
| --- | --- |
| Sources | `START_HERE.md` instructs opening `Svaraa_V0_Lab`; Cursor workspace currently includes parent `Hardware_V0/` with a duplicate README copy |
| Impact | Easy to write docs/code in the wrong root |
| Proposed resolution | Treat `Svaraa_V0_Lab/` as the sole project root. Parent `Hardware_V0/README_CURSOR_SVARAA_V0.md` is byte-identical (sha256 `e952e076…`) and informational only |
| Affected tickets | SV0-01.02, WB-001 |
| Status | proposed (recommend accept during P0 approval) |

## SC-002 — OpenAPI auxiliary response schemas incomplete

| Field | Value |
| --- | --- |
| Sources | `contracts/openapi.yaml` vs README §18 endpoint families |
| Impact | 12 of 13 success responses lack content schemas (only `POST /v1/device-events` references `EventReceipt`). Request bodies for several endpoints are thin or missing |
| Proposed resolution | Freeze schemas in SV0-S09/S12 contract work before generating stable clients; do not invent fields in P1 shell |
| Affected tickets | SV0-09.*, SV0-12.*, WB-008, WB-009 |
| Status | open (blocks client codegen, not P0 planning) |

## SC-003 — SQL starter vs product persistence needs

| Field | Value |
| --- | --- |
| Sources | `backend/schema.sql` (logical starter) vs README persistence/board requirements |
| Impact | Missing households, authorization, board/workflow, traces, evidence, migrations |
| Proposed resolution | Keep pack SQL as reference; design Lab SQLite schema under SV0-09 / WB-003 with migrations. Do not claim PostgreSQL concurrency from SQLite |
| Affected tickets | SV0-09.*, WB-003, WB-004 |
| Status | open (expected; not a source contradiction) |

## SC-004 — Earlier one-pager vs current pin/module baseline

| Field | Value |
| --- | --- |
| Sources | Handoff §01 “Reconciliation with the original brief” vs earlier visual one-pager (generic ESP32-S3, duplicate BMI270) |
| Impact | Aesthetic/module confusion if older images are treated as electrical authority |
| Proposed resolution | Current handoff/CSV pinmap wins. Older appearance refs remain aesthetic-only. Five logical lights; seven-petal appearance is visual, not five extra LEDs |
| Affected tickets | SV0-02.*, WB-006 |
| Status | resolved in handoff text; record retained |

## SC-005 — Assembly image is illustrative

| Field | Value |
| --- | --- |
| Sources | `references/original/image-1.png` vs `docs/pinmap.csv` + `docs/wire_schedule.csv` + BP01–BP06 |
| Impact | Risk of inferring nets from rendered holes/colors |
| Proposed resolution | Image labeled illustrative only. Electrical authority = CSV + blueprints. Simulator must load reviewed connection data, not hardcoded art coordinates as netlist |
| Affected tickets | WB-006, SV0-02.* |
| Status | accepted as process rule |

## SC-006 — Baseline host tests / toolchain on this Mac

| Field | Value |
| --- | --- |
| Sources | Pack README run instructions vs local tooling |
| Impact | Was blocking new host evidence |
| Resolution | Owner required immediate installs (SV0-01.01 v0.2). CLT 27.2 + user-local Node 22 + uv Python 3.12 installed. Host baselines re-run **passed** (31 + 15). Homebrew `/opt/homebrew` still needs sudo |
| Affected tickets | SV0-01.01, SV0-01.02, SV0-01.05 |
| Status | resolved for CLT/Node/Python; Homebrew optional open |

## SC-007 — Wire-protocol / health / command-result layouts partially frozen

| Field | Value |
| --- | --- |
| Sources | `contracts/wire_protocol.yaml` notes vs README §15 “freeze undefined health/command-result layouts…” |
| Impact | Byte-level interoperability claims premature for some frame types |
| Proposed resolution | Implement golden IMU/CRC paths first; freeze remaining layouts in an ADR before claiming full Nicla interoperability |
| Affected tickets | SV0-03.03, SV0-03.04, WB-008 |
| Status | open |

## SC-008 — Duplicate-response convention for identical event retries

| Field | Value |
| --- | --- |
| Sources | README §18 reliability vs starter OpenAPI 200 semantics |
| Impact | Ambiguous whether duplicate idempotent ingest returns identical receipt body/status details |
| Proposed resolution | Decide in S09 contract review; recommend converge on stored receipt with stable 200 and same receipt payload |
| Affected tickets | SV0-09.*, T20–T27 |
| Status | open |

## Non-conflicts verified

- Standalone original PDF and pack PDF: byte-identical.
- Standalone Jira CSV and pack CSV: byte-identical.
- Parent README and Lab README: byte-identical.
- CSV hierarchy ↔ `jira/plan.json`: 14 stories / 72 subtasks; keys match; no missing parents.
- Expected inventory counts match (see `docs/phases/P0_discovery.md`).
