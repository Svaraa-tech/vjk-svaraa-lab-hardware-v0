# Execution — WB-005

## What changed

- `services/simulator/{clock,core,engine}.py` — virtual clock, reducer port, journal/outbox/traces
- `services/api/app/sim_routes.py` — `/lab/v1/sim/*`
- `firmware/host-bridge/main.cpp` — JSONL C++ bridge around `sos_core.hpp`
- Workbench **Device Simulator** tab: SOS hold, reducer panel, read-only trace, full scenario button
- Scenario `manual_no_gps` headless + UI path

## Limitations

- Python core mirrors C++; bridge not yet required for every UI click (in-process engine default)
- Replay is read-only trace scrub, not full deterministic re-inject UI yet
