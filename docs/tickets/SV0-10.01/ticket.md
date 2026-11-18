# SV0-10.01 — SV0-10.01 | Build wearer dashboard

```yaml
ticket_id: SV0-10.01
work_type: Sub-task
source_namespace: original
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: —
```

## Problem and user outcome

Implementation: Routes, source freshness, actual battery source, privacy and current incident.

Acceptance: Unknown/mocked values labelled; app-open does not imply hardware health.

Owner role: Mobile / UX
Dependencies: story 10 prerequisites 08,09; execute listed integration order unless reviewed.
Evidence: evidence/SV0-10.01/ commit, profile, versions, logs, result and reviewer.
Estimate: team to estimate after environment/hardware qualification.
Physical gates cannot be closed by mocks.

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/SV0-10.01/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
