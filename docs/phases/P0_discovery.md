# P0 discovery report and phased roadmap

Revision: **P0-v0.1**  
Date: 2026-11-17  
Status: awaiting owner approval

## 1. Files found and read

### Handoff / instructions

- `START_HERE.md`, `README_CURSOR_SVARAA_V0.md`, `FILE_INDEX.md`
- Pack `AGENTS.md`, `README.md`
- `docs/HARDWARE_SOFTWARE_HANDOFF.md` (baseline sections + architecture/pin schedule)
- `references/manifest.json` (98 entries verified)

### Structured sources

- `docs/bom.csv`, `pinmap.csv`, `wire_schedule.csv`, `requirements.csv`, `references.json` (S01–S39)
- `jira/svaraa_v0_jira_import.csv`, `jira/plan.json`
- `tests/test_matrix.csv`, `tests/test_core.cpp`, `tests/test_contracts.py`, `tests/requirements.txt`
- `contracts/*` (OpenAPI, device_event schema, wire_protocol, ble_profile, authenticated_relay, reference_frame, example_event)
- `firmware/sos_core.hpp`, Nano/Nicla `.pseudo.cpp`
- `backend/schema.sql`, `ingest.pseudo.py`
- `simulation/scenarios.json`, Wokwi starter files
- Historical `evidence/host_*.txt`
- All 21 SVGs including BP01–BP06, VA01_assembly, D01–D12, SEQ01_ack, UI01_apps
- Assembly image `references/original/image-1.png` (illustrative)

### Originals (not overwritten)

- ZIP, PDF, Jira CSV, `image-1.png` under `references/original/`
- PDF/CSV byte-identical to pack copies

## 2. Source inventory verification

| Item | Expected | Actual | Notes |
| --- | --- | --- | --- |
| BOM | 32 | 32 | B01–B32 |
| Connections | 38 | 38 | W01–W38 |
| Requirements | 18 | 18 | R01–R18 |
| SVG drawings | 21 | 21 | Plus DOT sources and PDF sheets |
| Tests T01–T56 | 56 | 56 | All status “NOT EXECUTED - acceptance specification” |
| References S01–S39 | 39 | 39 | |
| Epic / stories / subtasks | 1 / 14 / 72 | 1 / 14 / 72 | CSV unique IDs 87; plan.json 72 tasks; keys match |
| Manifest hashed files | 96 + 2 generated | 98 verified | 0 missing, 0 hash mismatches |
| Extracted pack files | 91 | 91 | |

**Missing critical inputs:** none for P0. Environment tools for baseline re-run are missing (SC-006).

## 3. Tooling check (no installs performed)

| Tool | Available? |
| --- | --- |
| Xcode CLT | No — blocks usable Python/C++ |
| Node ecosystem | No |
| Homebrew | No |
| PlatformIO / cmake | No |
| Ruby / Perl / shasum | Yes (inventory only) |

## 4. Baseline tests

Recorded as **not-run**. Historical pack evidence retained separately. See `evidence/P0_discovery/tooling_and_baseline.json`.

## 5. Important gaps / decisions needed

See `docs/SOURCE_CONFLICTS.md`. Decisions requested in the approval ask below:

1. Accept `Svaraa_V0_Lab/` as sole project root (SC-001).
2. Approve default stack arch-v0.1 (React/Vite/TS + FastAPI + SQLite + C++ bridge).
3. Approve WB-001…WB-010 as proposed additions (separate namespace).
4. Approve installing Xcode CLT + Homebrew/Node/Python **as part of SV0-01.02** (not before SV0-01.01 approval).
5. Approve roadmap P0-v0.1 and first ticket plan SV0-01.01 v0.1.

## 6. Phased dependency-aware roadmap

Preserve original story prerequisites. SIM mocks unlock only recorded SIM sub-scopes.

| Phase | Stories / WB focus | Reviewable outcome |
| --- | --- | --- |
| **P0** Discovery | SV0-S01 inspect all | Manifest, conflicts, roadmap, SV0-01.01 plan ← *this document* |
| **P1** Foundation + workbench | SV0-01.01→01.05, early S12; WB-001–004, WB-002 shell | Reproducible workspace, board lifecycle, persistent storage, two-tab shell, reference gallery |
| **P2** First SOS slice | SIM S07, S09, S10, S11 + S12 controls; WB-005/008/009 subset | Virtual SOS → journal → API commit → guardian ACK → pendant return (no GPS required) |
| **P3** Sensors + hardware view | SIM S02–S05, S11; WB-006/007 | Exact components/pins, sensor charts, fall prealert, five-light behavior |
| **P4** Reliability + protocols | SIM S07–S09, S11–S12; WB-008 | Nicla/BLE codecs, queues, retries, failures, replay |
| **P5** Audio/privacy/apps | SIM S06, S10, S12; WB-007/009 | Synthetic voice path, half-duplex, privacy, role flows |
| **P6** Sim acceptance / Wokwi | S11; SIM evidence toward S13; WB-010; WB-011–021 | Regression scenarios, evidence dashboard, Wokwi subset visible in Device Simulator |
| **P7** Physical integration | S02–S08, S13 | One real adapter at a time; measured bench evidence; no-solder |
| **P8** Extensions / V1 | S14 after gates | Power/RF/cellular/Find My studies; manufacturer dossier |

### Suggested P1 ticket order (after SV0-01.01)

1. SV0-01.01 — evidence vocabulary (**first**)
2. SV0-01.02 — reproducible repo + tool pins (installs happen here)
3. WB-001 — import/provenance (feeds board)
4. SV0-01.03 / 01.04 — HAL ports + traceability
5. WB-003 + WB-004 — persistent Kanban + approvals
6. WB-002 — two-tab shell + gallery
7. SV0-01.05 — CI/evidence rules
8. Early SV0-12 contract freezes as needed for API work

Parallel research allowed; only one **implementation** ticket active unless batch-approved.

## 7. Proposed workbench tickets

| ID | Summary | Links |
| --- | --- | --- |
| WB-001 | Source import, validation, provenance, traceability | S01, S11 |
| WB-002 | App shell, navigation, document/diagram gallery | S10, S11 |
| WB-003 | Persistent Kanban, hierarchy, deps, filters, CSV export | S01 |
| WB-004 | Plan approval, acceptance, audit, doc sync | S01, S11 |
| WB-005 | Deterministic run engine, C++ bridge, clock, read-only replay | S07, S11 |
| WB-006 | Interactive parts, exact pins/nets, power domains | S02 |
| WB-007 | Sensor/audio/actuator visualization panels | S03–S06 |
| WB-008 | Protocol inspector, packet journey, timelines | S03, S08, S09 |
| WB-009 | Wearer/guardian web previews + ticket cross-links | S10 |
| WB-010 | Scenarios, fault injection, evidence dashboard/export | S11, S13 |
| WB-011 | PlatformIO+Wokwi scaffold, GPIO map, sim firmware | SV0-11.01 |
| WB-012 | Lab API: Wokwi status/diagram/view/sync | SV0-11.01 |
| WB-013 | Device Simulator embedded Wokwi panel | SV0-11.01, WB-002 |
| WB-014 | Serial JSON mirror in Wokwi web panel | WB-013 |
| WB-015 | Open-in-Wokwi / elements embed deep-link | WB-013 |
| WB-016 | Lab SOS ↔ Wokwi button hold visual | WB-013, WB-005 |
| WB-017 | Doctor/evidence: PIO+Wokwi toolchain + firmware hash | WB-011, S13 |
| WB-018 | Scenario playback drives Wokwi pixels all SOS phases | WB-010, WB-013 |
| WB-019 | Pixel RGB fidelity Lab ↔ Wokwi NeoPixels | WB-013, WB-007 |
| WB-020 | Headless wokwi-cli / PIO smoke in evidence | WB-017 |
| WB-021 | Always-visible Wokwi limits banner in Device Simulator | WB-013 |

These wrap original functionality; they do not replace S07/S09 safety/backend ownership.

## 8. Simulator product requirements retained (not deferred away)

The Device Simulator must eventually provide: Overview, Pendant, Hardware Bench, Sensors, Packet Explorer, System Architecture, App Previews, Scenarios/Faults, Evidence/References — with shared header (project, profile, backend, run/seed/time, incident, **SIMULATED**). Visualizations are engine/trace-driven. Board and Simulator share backend state; tab switches must not reset runs.
