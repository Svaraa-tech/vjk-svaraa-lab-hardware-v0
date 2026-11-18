# Tests — SV0-01.03

## Acceptance mapping

| ID | Result | Evidence |
| --- | --- | --- |
| A1 seven ports | met | `firmware/hal/ports.hpp` |
| A2 no SDK in core/hal | met | headers use only std + sos_core in glue |
| A3 mock host test | met | `host_hal.txt` — 33 checks PASS |
| A4 core 31 unchanged | met | `host_core.txt` |
| A5 null location | met | MockLocation clear_fix + board stub |
| A6 attempt ≠ receipt | met | MockTransport assertions |
| N1 no BENCH pass | met | Health::Mocked / Missing |
| N2 no flash claim | met | MockJournal only |
| N3 board no fake fix | met | NotImplemented + empty optionals |

## Command

```sh
source scripts/env.sh
SVARAA_EVIDENCE_DIR=evidence/SV0-01.03/latest make test
```

## Results

| Suite | Result |
| --- | --- |
| C++ core | passed (31) |
| C++ HAL | passed (33) |
| Python contracts | passed (15) |
