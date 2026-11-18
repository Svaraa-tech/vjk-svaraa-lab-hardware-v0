# SV0-11.03 — SV0-11.03 | Inject communication faults

```yaml
ticket_id: SV0-11.03
work_type: Sub-task
source_namespace: original
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: —
```

## Problem and user outcome

Implementation: No-route, lost response, duplicate, reorder, clock jump and reconnect fixtures.

Acceptance: Idempotency and monotonic deadlines hold.

Owner role: QA / embedded
Dependencies: story 11 prerequisites 01,07,09; execute listed integration order unless reviewed.
Evidence: evidence/SV0-11.03/ commit, profile, versions, logs, result and reviewer.
Estimate: team to estimate after environment/hardware qualification.
Physical gates cannot be closed by mocks.

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/SV0-11.03/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
