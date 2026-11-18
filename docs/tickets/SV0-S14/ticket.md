# SV0-S14 — SV0-S14 | V1 PCB and manufacturing handoff

```yaml
ticket_id: SV0-S14
work_type: Story
source_namespace: original
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: 13
```

## Problem and user outcome

Owner: Hardware / manufacturer. Prerequisites: 13. Close only with implementation, negative tests and evidence.

## Source scope

- Board authority: `.workbench/lab.db` (seed `data/seeds/board_bootstrap_v0.1.json`)
- Long-form execution/results: fill `implementation.md`, `tests.md`, `review.md` when work runs
- Evidence directory: `evidence/SV0-S14/` when tests produce artifacts

## Definition of done (SIM)

- Implementation notes recorded under this folder
- Honest test results (passed / failed / not-run / blocked)
- Board state updated; no physical/BENCH claims from SIM alone
