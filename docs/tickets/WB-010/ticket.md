# WB-010 — Scenario controls, fault injection, evidence dashboard and export

```yaml
ticket_id: WB-010
work_type: Workbench
source_namespace: workbench
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: —
plan_dependencies: SV0-S11,SV0-S13
```

## Problem and user outcome

Workbench addition; links SV0-S11,SV0-S13

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/WB-010/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
