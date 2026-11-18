# SV0-05.01 — SV0-05.01 | Implement debounced manual hold

```yaml
ticket_id: SV0-05.01
work_type: Sub-task
source_namespace: original
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: —
```

## Problem and user outcome

Implementation: Nonblocking20ms debounce and proposed2s hold; boot-held input must release.

Acceptance: One qualified hold creates one live incident; bounce cannot duplicate it.

Owner role: Firmware / UX
Dependencies: story 05 prerequisites 02,07; execute listed integration order unless reviewed.
Evidence: evidence/SV0-05.01/ commit, profile, versions, logs, result and reviewer.
Estimate: team to estimate after environment/hardware qualification.
Physical gates cannot be closed by mocks.

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/SV0-05.01/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
