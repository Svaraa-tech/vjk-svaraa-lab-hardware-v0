# Start here — Svaraa V0 Lab

This folder contains the complete Cursor build instruction and its reference files. It is a development handoff; the web application and simulator have not been built in this folder.

## Open the project

1. Extract Svaraa_Cursor_Starter_Pack.zip.
2. Open the extracted Svaraa_V0_Lab folder in Cursor.
3. Read README_CURSOR_SVARAA_V0.md, which defines the phased backlog, two-tab workbench, visual simulation, approval lifecycle and per-ticket documentation.
4. Paste the kickoff message below into Cursor.

The original PDF, source ZIP, Jira CSV and assembly image are already in references/original/. The original source ZIP is also extracted under references/agent-pack/Svaraa_V0_Engineer_Agent_Pack/. Cursor should inspect the existing extraction and manifest; it does not need to overwrite or re-extract them.

## Kickoff message

```text
Read README_CURSOR_SVARAA_V0.md in full and follow it as the project build instruction.

Use references/original/ and the existing extracted source under references/agent-pack/Svaraa_V0_Engineer_Agent_Pack/. Verify references/manifest.json and FILE_INDEX.md. Do not overwrite the originals or re-extract over existing files.

Perform P0 discovery and planning only. Inspect the engineering handoff, source contracts, original 87-item backlog, tests, all supplied diagrams and the assembly image. Record actual findings and unresolved decisions.

Propose the phased roadmap, the workbench additions and a detailed plan for SV0-01.01. Include the Kanban and Device Simulator tabs, actual named sensor visualizations, packet movement, mock APIs, data persistence, evidence and per-ticket documentation requirements from the README.

Create only the authorized documentation/bootstrap records. Do not scaffold the application, install packages or begin product implementation until I approve the roadmap and first ticket plan. Present the concrete plan and wait for my approval.
```

## Review and continue

Review each proposed ticket plan before approving implementation. After Cursor demonstrates and tests a ticket, explicitly accept it or request changes. The main README defines revision-bound approval and acceptance records.

A browser approval in the future Kanban app records a decision; it does not automatically start Cursor. Tell Cursor to continue so it can read the recorded decision and resume the permitted action.

## Important reference distinctions

- The engineering handoff defines a proposed V0 design and historical host-test evidence. Physical qualification remains open.
- The generated assembly image is an illustrative layout reference. The structured pin/wire schedules and reviewed blueprints govern connection mapping; do not infer electrical nets from apparent breadboard holes.
- Simulation starts with synthetic data and mock external notification providers. Physical sensors, native phone behavior and licensed extensions require their own evidence.
- Preserve the original source tickets. Approved simulation sub-scope does not close a physical gate or its parent ticket.

## Files and integrity

FILE_INDEX.md lists every package file using paths relative to this folder. references/manifest.json records SHA-256 hashes and byte sizes for the unchanged README, original inputs and extracted reference files. It also identifies the generated startup/index files. The manifest itself is deliberately not self-hashed.

The complete build specification is in README_CURSOR_SVARAA_V0.md; this page is only the launch guide.
