# SV0-13.04 — SV0-13.04 | Triage gates and defects

```yaml
ticket_id: SV0-13.04
work_type: Sub-task
source_namespace: original
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: —
```

## Problem and user outcome

Implementation: Classify bench/pilot/manufacturing blockers with named owner.

Acceptance: Electrical, privacy or lostSOS issues are not cosmetic waivers.

Owner role: QA / hardware / product
Dependencies: story 13 prerequisites 02-12; execute listed integration order unless reviewed.
Evidence: evidence/SV0-13.04/ commit, profile, versions, logs, result and reviewer.
Estimate: team to estimate after environment/hardware qualification.
Physical gates cannot be closed by mocks.

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/SV0-13.04/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
