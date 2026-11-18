# WB-013 — Device Simulator embedded Wokwi panel (diagram + pixels + serial)

```yaml
ticket_id: WB-013
work_type: Workbench
source_namespace: workbench
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: SV0-11.01,WB-012,WB-002
```

## Problem and user outcome
Device Simulator web tab shows the same Wokwi subset (board, SOS button, 5 pixels, serial) synced from the engine.

## Definition of done (SIM)
- WokwiPanel visible in Device Simulator
- Sync from engine updates phase/pixels


## Source scope
- Board authority: `.workbench/lab.db`
- Evidence: `evidence/WB-013/` when tests produce artifacts
