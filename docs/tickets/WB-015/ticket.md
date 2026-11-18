# WB-015 — Open-in-Wokwi / elements embed deep-link from Device Simulator

```yaml
ticket_id: WB-015
work_type: Workbench
source_namespace: workbench
workflow_state: Ready
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: WB-013,SV0-11.01
```

## Problem and user outcome
Provide an honest open path (VS Code Wokwi / optional elements embed) without claiming full-system sim.

## Source scope
- Board authority: `.workbench/lab.db`
- Evidence: `evidence/WB-015/` when tests produce artifacts

## Notes
Device Simulator already embeds a Lab-synced visual subset (WB-013). This ticket adds external Wokwi open / elements embed when licensing allows.
