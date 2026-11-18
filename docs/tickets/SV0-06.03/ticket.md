# SV0-06.03 — SV0-06.03 | Implement half-duplex session

```yaml
ticket_id: SV0-06.03
work_type: Sub-task
source_namespace: original
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: —
```

## Problem and user outcome

Implementation: Explicit authorized voice session; local wake; Wi-Fi upload; turn timeout.

Acceptance: No non-triggering background audio upload; privacy ends session.

Owner role: Audio / backend
Dependencies: story 06 prerequisites 02,03,12; execute listed integration order unless reviewed.
Evidence: evidence/SV0-06.03/ commit, profile, versions, logs, result and reviewer.
Estimate: team to estimate after environment/hardware qualification.
Physical gates cannot be closed by mocks.

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/SV0-06.03/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
