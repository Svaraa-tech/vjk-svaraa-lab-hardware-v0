# SV0-01.01 — Freeze scope and evidence vocabulary

```yaml
schema_version: "1.0"
ticket_id: SV0-01.01
source_id: "1011"
source_hash: "9d5702c0ee4a9c6e3e6064025b78c8528ef8af96ae6c1c56407649cd55be3b39" # parent CSV file
work_type: Sub-task
parent: SV0-S01
parent_source_id: "101"
priority: High
labels: [svaraa-v0]
owner_role: Lead / firmware
phase: P0/P1 foundation
profile: SIM
workflow_state: Done
implementation_state: implemented_sim
owner_acceptance: accepted_sim_scope
plan_revision: v0.2
dependencies: [] # story SV0-S01 prerequisites: None
requirements: [R13]
tests_linked: [T43, T44, T45]
```

## Problem and user outcome

Establish a shared, honest vocabulary for what SIM, USB BENCH, gated extensions, and V1 mean, and how every capability is labeled (implemented / mocked / blocked / not applicable). Prevent implied certification from mocks or UI.

## Source scope

From original CSV / plan.json:

- **Implementation:** Record SIM, USB BENCH and gated extensions in `docs/decisions.md`.
- **Acceptance:** Every capability has implemented/mocked/blocked status; no implied certification.
- **Evidence:** `evidence/SV0-01.01/` with commit/profile/versions/logs/result/reviewer.
- **Constraint:** Physical gates cannot be closed by mocks.

## Definition of ready

- P0 inventory complete (done).
- Source conflicts register exists (done).
- Plan v0.1 written and awaiting owner approval.

## Acceptance criteria

1. `docs/decisions.md` defines V0-A SIM, V0-B BENCH, V0-C EXTENSION, V1 PRODUCT with explicit “proves / does not prove” tables.
2. Capability matrix covers sensors, buses, audio, SOS/delivery phases, apps, notifications, Find My/cellular/power, workbench features — each with status vocabulary and evidence profile.
3. Evidence field definitions: implementation state, test execution result, evidence profile, owner acceptance — independent.
4. Historical pack evidence labeled separately from new runs.
5. No capability marked physically qualified without BENCH/field evidence path.
6. Ticket evidence folder records tooling versions and that baseline host tests remain not-run until SV0-01.02 environment setup (unless tools become available during this ticket without expanding scope into package installs — installs belong in 01.02).

## Out of scope for this ticket

- Creating app/scaffold, installing Node/Python packages, changing pin/contracts, implementing board UI.
