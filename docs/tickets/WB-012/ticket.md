# WB-012 — Lab API for Wokwi status, diagram, view, and engine sync

```yaml
ticket_id: WB-012
work_type: Workbench
source_namespace: workbench
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: SV0-11.01,WB-011
```

## Problem and user outcome
Expose `/lab/v1/wokwi/*` so the workbench can load diagram metadata and mirror Lab engine phase into Wokwi visuals.

## Definition of done (SIM)
- status, diagram, view, sync endpoints
- Evidence profile labeled Wokwi


## Source scope
- Board authority: `.workbench/lab.db`
- Evidence: `evidence/WB-012/` when tests produce artifacts
