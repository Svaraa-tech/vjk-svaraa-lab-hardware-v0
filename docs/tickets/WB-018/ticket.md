# WB-018 — Scenario playback drives Wokwi pixels for all SOS phases

```yaml
ticket_id: WB-018
work_type: Workbench
source_namespace: workbench
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: WB-010,WB-013,SV0-S11
```

## Problem and user outcome
manual_no_gps (and later scenarios) advance Wokwi panel pixels through Ready→…→Resolved.


## Source scope
- Board authority: `.workbench/lab.db`
- Evidence: `evidence/WB-018/` when tests produce artifacts
