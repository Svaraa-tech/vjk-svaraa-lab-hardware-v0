# services/simulator

Deterministic SIM run engine (WB-005):

- `clock.py` — virtual monotonic clock (pause/step/speed)
- `core.py` — Python port of `firmware/core/sos_core.hpp` (keep aligned)
- `engine.py` — journal, outbox, traces, `manual_no_gps` scenario

C++ JSONL bridge: `firmware/host-bridge/`.

API: `/lab/v1/sim/*` on the Lab FastAPI service.
