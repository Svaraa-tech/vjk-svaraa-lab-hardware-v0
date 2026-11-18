# WB-011 — PlatformIO+Wokwi project scaffold, GPIO map, sim firmware build

```yaml
ticket_id: WB-011
work_type: Workbench
source_namespace: workbench
workflow_state: Backlog
implementation_state: not_started
profile: SIM
priority: High
plan_dependencies: SV0-11.01,SV0-S11
```

## Problem and user outcome
Ship a buildable Wokwi/PlatformIO project under `simulation/wokwi/` with honest GPIO map and firmware.bin for visual SOS/pixels.

## Definition of done (SIM)
- diagram.json, platformio.ini, wokwi.toml, src/main.cpp, GPIO_MAP.md
- `pio run -e sim` succeeds; firmware.bin present
- No BLE/I2S/Nicla claims


## Source scope
- Board authority: `.workbench/lab.db`
- Evidence: `evidence/WB-011/` when tests produce artifacts
