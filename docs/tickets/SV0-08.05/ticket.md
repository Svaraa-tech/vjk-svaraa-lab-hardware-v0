# SV0-08.05 — SV0-08.05 | Test real phone lifecycle

```yaml
ticket_id: SV0-08.05
work_type: Sub-task
source_namespace: original
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: —
```

## Problem and user outcome

Implementation: Native iOS restoration/Android supported background design on physical phones.

Acceptance: Termination, reboot and revoked permissions show degraded status honestly.

Owner role: Mobile / embedded
Dependencies: story 08 prerequisites 07,12; execute listed integration order unless reviewed.
Evidence: evidence/SV0-08.05/ commit, profile, versions, logs, result and reviewer.
Estimate: team to estimate after environment/hardware qualification.
Physical gates cannot be closed by mocks.

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/SV0-08.05/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
