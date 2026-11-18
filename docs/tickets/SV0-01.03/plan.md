# Plan — SV0-01.03 Define typed HAL ports

**Plan revision:** v0.1  
**Profile:** SIM  
**Depends on:** SV0-01.01, SV0-01.02 (accepted)

## Ticket and source scope

Source **1013 / SV0-01.03**: define Clock, MotionSample, LocationFix, Journal, Audio, Ui, and Transport without SDK types in the core. Acceptance: the same deterministic core runs under mock and board adapters.

## Why this is next

Unblocks SIM adapters, host-bridge orchestration (WB-005), and later Nano/Nicla board code without contaminating `sos_core.hpp` with Arduino/Wire/BLE types.

## Design summary

Keep `firmware/core/sos_core.hpp` as the pure reducer (unchanged semantics). Add a sibling HAL layer:

```text
firmware/core/sos_core.hpp          # existing reducer (no HAL includes required)
firmware/hal/types.hpp              # shared POD types (samples, fixes, results)
firmware/hal/ports.hpp              # abstract port interfaces (pure virtual or concept-style structs)
firmware/hal/mock/*.hpp + *.cpp     # deterministic SIM adapters
firmware/hal/board/*.hpp            # board adapter *interfaces/stubs* only (no Arduino SDK)
firmware/hal/README.md              # mapping to handoff §10 table
```

Handoff contracts to encode:

| Port | Contract |
| --- | --- |
| Clock | Monotonic ms always; optional trusted UTC (nullable / untrusted flag) |
| MotionSample | Accel mg[3], gyro 0.1°/s[3], valid/saturated/overrun, acquisition time |
| LocationFix | Source, nullable lat/lon, accuracy_m, fix_at, age_ms, valid |
| Journal | Bounded immutable append/commit/replay; explicit failure codes |
| Transport | Reachability / auth / attempt / receipt separated; retry same identity |
| Audio | Bounded capture/playback, privacy, session timeout; lower priority |
| Ui | Render actual phase + independent health; no optimistic success |

Also define a small `Supervisor` health/progress struct (handoff lists it) as types only if needed for Ui/Transport health surfaces — not a full watchdog implementation.

**Mock vs board:** Mock adapters compile and are exercised on host. Board adapters are header stubs documenting intended Nano/Nicla wiring points without including Arduino headers in this ticket.

**Integration smoke:** A host test harness that:
1. Uses `MockClock` + feeds times into existing `Core::tick` / `manual_sos` / `fall_candidate`
2. Appends a frozen canonical event blob via `MockJournal` (bytes opaque to core)
3. Records a `MockTransport` attempt without claiming server receipt
4. Proves `sos_core` still passes the original 31 checks unchanged

Optional thin `HostSafetyGlue` (header/cpp) that maps button-qualified inputs → `Core` methods using only HAL types — still no SDK.

## Concrete steps

1. Add `firmware/hal/` headers for types + ports as above.
2. Implement mock adapters with deterministic behavior and injectable faults (journal full, transport down, stale location nulls).
3. Add board stub headers (`board_clock.hpp`, etc.) that mirror ports but `#error` or `static_assert` if someone tries to use them without a future `SVARAA_BOARD` build — or simply document unimplemented methods returning `NotImplemented`.
4. Add `tests/host/test_hal_mock.cpp` (or `.py` not needed) compiling against mocks + core.
5. Extend `scripts/test.sh` / Makefile to run new HAL host test alongside existing baselines.
6. Document port ↔ requirement/story links lightly in `firmware/hal/README.md` (full R-map remains 01.04).
7. Record evidence under `evidence/SV0-01.03/<run-id>/`.
8. Demonstrate compile + test output; request acceptance.

## Affected files

| Path | Action |
| --- | --- |
| `firmware/hal/**` | Create |
| `firmware/core/sos_core.hpp` | Prefer **no change**; only if include hygiene needed |
| `tests/host/test_hal_mock.cpp` | Create |
| `scripts/test.sh`, maybe `Makefile` | Extend |
| `docs/tickets/SV0-01.03/*` | Implementation/tests/review |
| Arduino sketches / React | **unchanged** |

## UI behavior affected

None.

## Mocks vs real local implementation

| Piece | This ticket |
| --- | --- |
| HAL type/port definitions | Real |
| Mock adapters + host tests | Real |
| Board adapters | Stub interfaces only |
| Physical sensors/radios | Not implemented |
| JSON-lines host-bridge process | Not yet (WB-005) |

## Acceptance and negative tests

| ID | Check |
| --- | --- |
| A1 | Ports exist for Clock, MotionSample, LocationFix, Journal, Audio, Ui, Transport |
| A2 | No Arduino/Wire/BLE/SDK includes in `firmware/core` or `firmware/hal` public headers |
| A3 | Mock adapters compile; host HAL test passes |
| A4 | Original 31-check `test_core` still passes unchanged |
| A5 | Location/battery nulls representable (no invented coordinates) |
| A6 | Transport distinguishes attempt vs receipt |
| N1 | Must not mark BENCH sensor/radio tests passed |
| N2 | Must not claim journal survives power-cut on real flash |
| N3 | Board stubs must not silently return fake “healthy” measurements as if measured |

## Demonstration

```sh
source scripts/env.sh
make test   # includes new HAL mock host test + prior baselines
```

Show `firmware/hal/README.md` port table and a failing mock fault (e.g. journal full) returning explicit error.

## Risks, assumptions, rollback

| Risk | Mitigation |
| --- | --- |
| Over-abstracting before bridge exists | Keep PODs + small virtual/struct ports; no framework |
| Temptation to put policy in HAL | Core owns SOS phases; HAL only I/O ports |
| Board stub misuse | Explicit `NotImplemented` / docs; SIM default |

Rollback: delete `firmware/hal` and `test_hal_mock`; revert test script.

## Open decisions (recommendations)

1. **C++ style:** pure abstract base classes with `virtual` — recommend **yes** (simple, host-testable).  
2. **Keep Supervisor as types-only** this ticket — recommend **yes**.  
3. **Do not modify reducer API** unless required — recommend **no change**.

## Approval requested

Approve **SV0-01.03 plan v0.1** only. No HAL code until approval.
