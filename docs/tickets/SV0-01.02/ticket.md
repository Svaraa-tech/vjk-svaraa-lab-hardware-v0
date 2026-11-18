# SV0-01.02 — Create reproducible repository

```yaml
schema_version: "1.0"
ticket_id: SV0-01.02
source_id: "1012"
work_type: Sub-task
parent: SV0-S01
parent_source_id: "101"
priority: High
labels: [svaraa-v0]
owner_role: Lead / firmware
phase: P1 foundation
profile: SIM
workflow_state: Done
implementation_state: implemented_sim
owner_acceptance: accepted_sim_scope
plan_revision: v0.1
dependencies: [SV0-01.01]
requirements: [R13]
tests_linked: [T43, T44, T45]
```

## Problem and user outcome

A clean checkout of this folder can recreate the toolchain pins, folder layout, and host baseline tests with recorded compiler/core versions — without inventing a finished product UI.

## Source scope

- **Implementation:** Create core, board adapters, contracts, apps, backend, tests and evidence folders; pin qualified tool versions.
- **Acceptance:** Clean checkout reproduces host tests and records actual compiler/core versions.
- **Evidence:** `evidence/SV0-01.02/`

## Definition of ready

- SV0-01.01 accepted (done).
- CLT / Node / Python available on this Mac (done).
- Architecture arch-v0.1 + UI theme ADR-0002 accepted.

## Out of scope

- Full Kanban/simulator UI behavior (WB-002+)
- Product SOS slice APIs beyond stubs
- PlatformIO/Wokwi full setup
- Homebrew (optional; user-local tools remain valid)
