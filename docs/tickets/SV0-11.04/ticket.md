# SV0-11.04 — SV0-11.04 | Build end-to-end drill test

```yaml
ticket_id: SV0-11.04
work_type: Sub-task
source_namespace: original
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: —
```

## Problem and user outcome

Implementation: Virtual device -> actual local backend -> bothUI roles -> return acknowledgment.

Acceptance: Correlated event log and zero real emergency-provider calls.

Owner role: QA / embedded
Dependencies: story 11 prerequisites 01,07,09; execute listed integration order unless reviewed.
Evidence: evidence/SV0-11.04/ commit, profile, versions, logs, result and reviewer.
Estimate: team to estimate after environment/hardware qualification.
Physical gates cannot be closed by mocks.

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/SV0-11.04/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
