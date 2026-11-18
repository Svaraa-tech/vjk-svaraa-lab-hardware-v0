# SV0-13.05 — SV0-13.05 | Freeze V0 dossier

```yaml
ticket_id: SV0-13.05
work_type: Sub-task
source_namespace: original
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: —
```

## Problem and user outcome

Implementation: Versions, wiring, tests, limits and engineering sign-off.

Acceptance: Release is bench demonstrator only, not a sole emergency lifeline.

Owner role: QA / hardware / product
Dependencies: story 13 prerequisites 02-12; execute listed integration order unless reviewed.
Evidence: evidence/SV0-13.05/ commit, profile, versions, logs, result and reviewer.
Estimate: team to estimate after environment/hardware qualification.
Physical gates cannot be closed by mocks.

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/SV0-13.05/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
