# firmware/host-bridge

JSON-lines adapter around `firmware/core/sos_core.hpp` (WB-005).

## Build

```sh
c++ -std=c++17 -Wall -Wextra -O2 main.cpp -o svaraa_host_bridge
```

## Protocol (v1)

stdin/stdout, one JSON object per line:

| cmd | fields | effect |
| --- | --- | --- |
| `ping` | — | liveness |
| `reset` | — | clear core |
| `manual_sos` | `incident_id` | live SOS |
| `update` | `incident_id`, `phase`, `revision` | verified server/human update |
| `tick` | `now_ms`, optional `incident_id` | prealert deadline |
| `snapshot` | — | phase/mode/incident/revision |

Browser never sets `verified` — only this bridge / Lab API does after durable receipt.

Python SIM engine in `services/simulator/` mirrors the same reducer for in-process runs.
