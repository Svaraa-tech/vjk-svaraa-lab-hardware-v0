# SV0-14.02 — SV0-14.02 | Engineer product power

```yaml
ticket_id: SV0-14.02
work_type: Sub-task
source_namespace: original
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: —
```

## Problem and user outcome

Implementation: Select matched cell/NTC/protection/powerpath/gauge/coil/supervisor.

Acceptance: Reviewed schematic, thermal/current/runtime tests; magnets not protocol proof.

Owner role: Hardware / manufacturer
Dependencies: story 14 prerequisites 13; execute listed integration order unless reviewed.
Evidence: evidence/SV0-14.02/ commit, profile, versions, logs, result and reviewer.
Estimate: team to estimate after environment/hardware qualification.
Physical gates cannot be closed by mocks.

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/SV0-14.02/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
