# firmware/hal — typed ports (SV0-01.03)

SDK-free HAL between the pure reducer (`firmware/core/sos_core.hpp`) and adapters.

| Port | Header | Mock | Board stub |
| --- | --- | --- | --- |
| Clock | `ports.hpp` `IClock` | `mock/mock_ports.hpp` | `board/board_stubs.hpp` |
| MotionSample | `IMotion` + `MotionSample` | MockMotion | BoardMotion |
| LocationFix | `ILocation` + `LocationFix` | MockLocation | BoardLocation |
| Journal | `IJournal` | MockJournal | BoardJournal |
| Transport | `ITransport` | MockTransport | BoardTransport |
| Audio | `IAudio` | MockAudio | BoardAudio |
| Ui | `IUi` | MockUi | BoardUi |

Supervisor health fields live in `types.hpp` (`SupervisorSnapshot`, `ComponentHealth`) as types only.

## Rules

- No Arduino / Wire / BLE / ESP-IDF includes in these headers.
- Mock adapters are SIM evidence only (`Health::Mocked`).
- Board stubs return `NotImplemented` / null location — never fake measured fixes.
- Transport `attempt_send` ≠ durable server receipt ≠ human ACK.
- Full requirements→ticket map remains SV0-01.04.

## Host glue

`host_safety_glue.hpp` shows how qualified hold + journal + transport attempt interact with `Core` under mocks.
