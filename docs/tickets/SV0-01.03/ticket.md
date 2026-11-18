# SV0-01.03 — Define typed HAL ports

```yaml
schema_version: "1.0"
ticket_id: SV0-01.03
source_id: "1013"
work_type: Sub-task
parent: SV0-S01
parent_source_id: "101"
priority: High
labels: [svaraa-v0]
owner_role: Lead / firmware
phase: P1 foundation
profile: SIM
workflow_state: Awaiting Acceptance
implementation_state: implemented_sim
plan_revision: v0.1
dependencies: [SV0-01.01, SV0-01.02]
requirements: [R13]
tests_linked: [T43, T44, T45]
```

## Problem and user outcome

The safety core must stay free of Arduino/SDK types. Typed HAL ports let the same reducer run under mock (SIM) and later board adapters (BENCH) without rewriting core logic.

## Source scope

- **Implementation:** Define Clock, MotionSample, LocationFix, Journal, Audio, Ui and Transport without SDK types in the core.
- **Acceptance:** The same deterministic core runs under mock and board adapters.
- **Evidence:** `evidence/SV0-01.03/`

## Definition of ready

- SV0-01.02 accepted (done)
- `firmware/core/sos_core.hpp` present
- Host tests green via `make test`

## Out of scope

- Real Arduino Wire/I2S/BLE drivers
- Full journal flash implementation on device
- Workbench UI for HAL (later)
- Changing reducer phase semantics (unless a compile-needed fix)
