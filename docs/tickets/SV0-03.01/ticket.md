# SV0-03.01 — SV0-03.01 | Qualify dual I2C setup

```yaml
ticket_id: SV0-03.01
work_type: Sub-task
source_namespace: original
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: —
```

## Problem and user outcome

Implementation: Nicla external controller to Nano target0x2A; independent Nano sensor controller.

Acceptance: 10,000 frames with measured sequence/CRC results; core versions recorded.

Owner role: Embedded / ML
Dependencies: story 03 prerequisites 02; execute listed integration order unless reviewed.
Evidence: evidence/SV0-03.01/ commit, profile, versions, logs, result and reviewer.
Estimate: team to estimate after environment/hardware qualification.
Physical gates cannot be closed by mocks.

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/SV0-03.01/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
