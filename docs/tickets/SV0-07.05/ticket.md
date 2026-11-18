# SV0-07.05 — SV0-07.05 | Isolate drills and live events

```yaml
ticket_id: SV0-07.05
work_type: Sub-task
source_namespace: original
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: —
```

## Problem and user outcome

Implementation: Server-issued drill ID and test-only recipients; real physicalSOS preempts.

Acceptance: New live incident ID on preemption; no drill into live provider.

Owner role: Embedded lead
Dependencies: story 07 prerequisites 01,03; execute listed integration order unless reviewed.
Evidence: evidence/SV0-07.05/ commit, profile, versions, logs, result and reviewer.
Estimate: team to estimate after environment/hardware qualification.
Physical gates cannot be closed by mocks.

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/SV0-07.05/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
