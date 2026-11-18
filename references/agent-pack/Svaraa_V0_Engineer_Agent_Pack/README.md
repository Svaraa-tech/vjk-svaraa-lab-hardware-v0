# Svaraa V0 hardware and software engineering handoff

Start with `Svaraa_V0_Engineering_Handoff.pdf`, `AGENTS.md`, and `docs/HARDWARE_SOFTWARE_HANDOFF.md`.

This package includes the physical no-solder bill of materials, pin allocation, 38-wire schedule, six electrical/module blueprints and 15 additional architecture/interface drawings. It is intended for simulation now and later assembly of real purchased modules. Battery/cellular/Find My remain separately qualified extensions.

## What is executable and what is not

`firmware/sos_core.hpp` is a pure C++ reference reducer. It passed 31 host checks. Fifteen Python checks passed for event contracts, reference framing, API references and Jira hierarchy. Logs are under `evidence/`.

Files ending `.pseudo.cpp` and `.pseudo.py` are integration pseudocode, not finished drivers/services. `backend/schema.sql` is an incomplete logical schema starter, not a secured production migration. `simulation/wokwi/` is a visual starter that was NOT compiled or run here. It only prints a mock message and changes virtual LEDs. No actual backend, emergency notification, BLE or audio is activated by it.

No physical board was assembled, flashed or measured. No real phone, fall-detection accuracy, battery life, RF performance, Find My certification or production readiness is claimed.

## Run host checks

From this directory with Python 3 and a C++17 compiler installed:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r tests/requirements.txt
python3 -m unittest discover -s tests -p 'test_*.py' -v
c++ -std=c++17 -Wall -Wextra -Werror tests/test_core.cpp -o /tmp/svaraa_test_core
/tmp/svaraa_test_core
```

## Jira

`jira/svaraa_v0_jira_import.csv`: 87 work items: one Epic, 14 Stories, 72 Sub-tasks. Use a test project and a hierarchy-capable administrative importer. Map Work item ID and Parent appropriately. Planning IDs are not existing Jira keys. Roles and dependencies in descriptions are not automatically assigned people or issue links. No Jira board was changed.

## Engineering source

`docs/`: source manual, structured blocks, BOM, pins, wires, requirement matrix and 39 primary references.
`diagrams/`: editable SVGs, architecture DOT files, and readable vector PDF sheets.
`contracts/`: OpenAPI, event JSON Schema, BLE/I2C protocols, example and reference codec.
`firmware/`: tested core and separate Nano/Nicla integration pseudocode.
`backend/`: transaction and database starters.
`tests/`: executed host tests and 56 planned acceptance scenarios.
`simulation/`: unqualified visual starter and deterministic scenario descriptions.

Do not manufacture a PCB or wire a battery from this package without qualified electrical/power/RF review. The drawings are V0 module-level connections, not Gerbers or final product schematics.
