# Implementation — SV0-01.03

Approved plan: **v0.1** (via owner `do next`)  
Implemented: 2026-11-17 / 2026-11-18 UTC

## What changed and why

Added SDK-free HAL ports so the pure reducer can run under SIM mocks now and board stubs later without Arduino/Wire/BLE types in the core.

## Actual artifacts

| Path | Role |
| --- | --- |
| `firmware/hal/types.hpp` | POD types + Result/Health |
| `firmware/hal/ports.hpp` | IClock, IMotion, ILocation, IJournal, ITransport, IAudio, IUi |
| `firmware/hal/mock/mock_ports.hpp` | Deterministic mocks + faults |
| `firmware/hal/board/board_stubs.hpp` | NotImplemented board stubs |
| `firmware/hal/host_safety_glue.hpp` | Hold → core → journal → transport attempt |
| `firmware/hal/README.md` | Port map |
| `tests/host/test_hal_mock.cpp` | 33 host checks |
| `scripts/test.sh` | Runs core + HAL + Python |

`firmware/core/sos_core.hpp` unchanged.

## Limitations

- Journal bytes are opaque markers (schema freeze later).
- Board stubs are not wired to hardware.
- Host-bridge JSON-lines process still WB-005.
- Supervisor is types-only.
