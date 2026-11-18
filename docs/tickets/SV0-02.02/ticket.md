# SV0-02.02 — SV0-02.02 | Assemble segregated power

```yaml
ticket_id: SV0-02.02
work_type: Sub-task
source_namespace: original
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: —
```

## Problem and user outcome

Implementation: Build USB board feeds and fused EXT_5V load distribution.

Acceptance: No positive rail tie; measured idle/peak rails remain within selected ratings.

Owner role: Hardware / firmware
Dependencies: story 02 prerequisites 01; execute listed integration order unless reviewed.
Evidence: evidence/SV0-02.02/ commit, profile, versions, logs, result and reviewer.
Estimate: team to estimate after environment/hardware qualification.
Physical gates cannot be closed by mocks.

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/SV0-02.02/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
