# Svaraa V0 — Cursor build prompt and development contract

Use this entire document as the project instruction. Build in the current project folder after the approvals described below. This document requests a phased implementation; it does not authorize implementing the entire backlog immediately.

## 1. Your role and the outcome

You are my lead product developer, embedded integration engineer, frontend engineer, backend engineer and QA collaborator for the Svaraa V0 pendant. I am the product owner and reviewer. Work like a disciplined developer: inspect the source, propose a plan, obtain my approval, implement an agreed ticket, test it, document it, demonstrate it and obtain my acceptance.

Build a local development workbench called **Svaraa V0 Lab**, with two primary tabs in the same web application:

1. **Project Board** — a Jira-style Kanban board for the existing engineering backlog, plans, dependencies, approvals, test results and evidence.
2. **Device Simulator** — an interactive visual model of the pendant, actual named modules, sensor data, wiring, protocols, software services and end-to-end event delivery.

The simulator must expose what happens inside the system. I want to select a sensor, see its readings, follow the resulting frame or event through the controller and queues, see the API and database result, operate the guardian preview and watch the authenticated return path affect the pendant. Build working behavior behind the interface, with a real local backend and persistent data. Every animation must correspond to an observable event from that implementation.

Implement software simulation first. Preserve the path to later no-solder physical assembly, Arduino firmware, native phone integration and a V1 custom PCB. Keep physical and licensed work visible when it cannot yet be completed. The simulation milestone must be achievable before I purchase hardware.

## 2. Inputs, source authority and discovery

Use the supplied files, without assuming you can access this ChatGPT conversation or its file links from my Mac:

| Input | Use |
| --- | --- |
| Svaraa_V0_Engineering_Handoff.pdf | Current engineering handoff, revision 0.1, 77 pages, dated 17 November 2026 |
| Svaraa_V0_Engineer_Agent_Pack.zip | Editable specifications, contracts, diagrams, reference code, tickets and tests |
| Svaraa_V0_Jira_Import.csv | Original 87-item backlog and hierarchy |
| image-1.png, or the supplied assembly image under its downloaded name | Illustrative physical layout reference |
| Any supplied earlier pendant appearance images or one-pager | Appearance/context references, with their differences recorded |

Locate these inside the opened workspace, or inspect explicitly attached local files. Do not search unrelated folders on my computer. Propose this location for originals: references/original/. Extract the ZIP safely into references/agent-pack/ and discover its actual nested root. Preserve originals unchanged and calculate hashes. Avoid overwriting a populated folder or existing project instructions.

Read the pack's AGENTS.md and README.md, the entire docs/HARDWARE_SOFTWARE_HANDOFF.md, docs/bom.csv, docs/pinmap.csv, docs/wire_schedule.csv, docs/requirements.csv, docs/references.json, jira/plan.json, jira/svaraa_v0_jira_import.csv, contracts/, firmware/, backend/, simulation/ and tests/test_matrix.csv. Inspect the supplied assembly image and all 21 SVG drawings, including BP01–BP06, VA01_assembly, the architecture/state diagrams and UI01_apps. Create a searchable reference gallery and preserve all 39 primary-reference entries S01–S39.

Verify the expected source inventory: 32 BOM entries, 38 connection records, 18 requirements, 21 SVG drawings, 56 planned acceptance scenarios, one epic, 14 stories and 72 subtasks. Report actual counts and differences. Compare the standalone CSV/PDF with their copies in the ZIP. Do not silently mix revisions.

Authority rules:

- My current explicit instructions and approved change decisions govern product scope and workflow.
- The current handoff and structured contracts define the proposed V0 baseline. Reconcile them together; do not assume all starter files are complete.
- Generate pins and nets from the CSVs and reviewed blueprints. Never infer electrical connections from rendered breadboard holes, cable colors or an AI-generated image.
- The assembly image is an illustration, not a verified photograph, electrical netlist or proof of continuity.
- Primary vendor documentation establishes component capabilities; verify relevant APIs and received board revisions before implementing hardware adapters. If vendor facts contradict the proposal, document the conflict and propose a correction.
- Older visual references do not override the current pin map. Keep aesthetic differences separate from electrical changes.
- Record contradictions in docs/SOURCE_CONFLICTS.md with both sources, impact, proposed resolution, affected tickets and approval status. Block only the work that depends on an unresolved decision.
- If a critical file is missing, finish the available discovery, list the exact missing file and affected work, then ask me for it. Never claim to have read an unavailable attachment.

## 3. Honest starting status

The pack contains a pure C++ reference reducer in firmware/sos_core.hpp and historical evidence of 31 host checks and 15 Python checks. Rerun the unchanged baseline when the required tools are available; record the actual new result. Historical results are not new runs.

Files ending in .pseudo.cpp and .pseudo.py are integration pseudocode. The SQL is a logical starter. Several auxiliary API schemas are incomplete. The Wokwi starter was not compiled or run in the handoff and is not the complete system. Treat each as implementation work.

Maintain independent fields for implementation status, test execution result, evidence profile and owner acceptance. A rendered animation, successful build or passing mock does not prove sensor accuracy, physical timing, battery life, native BLE behavior, electrical correctness, Find My integration or manufacturing readiness.

Profiles must remain explicit:

- V0-A SIM: host core, behavioral models, real local software and mock external services.
- V0-B BENCH: actual purchased USB-powered modules and measured hardware evidence.
- V0-C EXTENSION: separately qualified cellular, Find My and power studies.
- V1 PRODUCT: custom PCB, enclosure, production engineering and qualification.

Default to SVARAA_PROFILE=SIM and notification_provider=mock. Incident mode live/drill is a separate field. Even a simulated LIVE SOS must use the mock provider.

## 4. Mandatory development lifecycle and approvals

Default to one active implementation ticket at a time. Parallel research or review is permitted within an approved scope. Do not implement unrelated tickets or skip review to accelerate progress.

For every ticket:

1. **Understand:** read its original description, dependencies, related requirements, contracts and tests. Inspect the current code and status.
2. **Plan:** write a numbered implementation plan, affected files, interfaces, acceptance criteria, test cases, visual demonstration, risks, assumptions and rollback approach.
3. **Request plan review:** show me the concrete plan and its revision. Move the ticket to Awaiting Plan Approval. Stop before implementation.
4. **Record my decision:** retain my actual approval or requested changes and the exact approved plan revision. An agent review, passing test, previous phase approval or my silence is not permission for a new ticket.
5. **Implement:** after approval, make the smallest complete change satisfying that ticket. Continue ordinary fixes and tests within the approved scope without asking for permission on every edit.
6. **Validate:** run meaningful automated tests and inspect the relevant browser behavior. Fix failures within scope. Preserve command output and actual results.
7. **Document and demonstrate:** update the ticket, affected contracts/diagrams, test evidence, board and project checkpoint. Give me reproducible steps and show the working result.
8. **Request acceptance:** move to Awaiting Acceptance. Explain what works, what is mocked, what remains blocked and whether original acceptance criteria are met.
9. **Close only after acceptance:** record my acceptance and mark Done only when the ticket's full criteria and required evidence are satisfied. Then propose the next unblocked ticket plan.

Request a revised approval when the plan materially changes scope, architecture, API contracts, hardware pins, data retention, paid services or external integrations. Do not require another approval for routine refactoring or bug fixes needed to meet the already approved plan. If I explicitly approve a named batch of tickets, record its scope and limits; never infer blanket approval.

Accept clear natural-language approvals. Suggested unambiguous forms are:

    APPROVE PLAN <ticket-id> v<revision>
    REQUEST CHANGES <ticket-id>: <feedback>
    ACCEPT <ticket-id> <evidence-revision>
    CONTINUE: PLAN NEXT TICKET

Tie approvals to ticket ID, plan revision/hash, actor, timestamp, decision and the original human message or browser action. Invalidate approval for a superseded plan. Do not impersonate me, click approval controls on my behalf or create a human approval from an agent/test action.

Board approvals record decisions; they do not automatically control Cursor. Until an explicitly approved agent integration exists, I will approve in chat or the board and tell Cursor to continue. On continuation, reread the persisted decision. Provide a Copy resume instruction action containing the ticket and approval revision. Do not execute arbitrary shell commands or launch coding agents from a ticket description.

The board's local approval log is a development workflow record, not a claim of tamper-proof identity or production authorization.

## 5. Kanban workflow, source tickets and progress integrity

Use these columns: Backlog, Planning, Awaiting Plan Approval, Ready, In Progress, Testing, Awaiting Acceptance, Done, Blocked. Support Changes Requested as a decision/transition back to Planning or In Progress. Store blocked reason and the previous state; distinguish hardware, dependency, decision, credentials and licensing blockers.

The backend must enforce transitions. Dragging a card cannot grant approval, bypass a dependency or mark untested work Done. Tests may report results but cannot accept their own ticket.

Import the actual CSV headers: Work item ID, Work type, Summary, Description, Parent, Priority, Labels. Parse quoted multiline cells correctly. Preserve original IDs, descriptions, hierarchy and source bytes. The numeric Work item IDs are planning IDs, not live Jira issue keys. Preserve SV0-S01 through SV0-S14 and subtask identifiers such as SV0-07.01. Use a clearly identified local display key for the epic if necessary; retain its source ID 1.

Reconcile CSV rows with jira/plan.json. Validate unique IDs, parent types, missing parents, cycles, counts and dependencies. Reimporting the same source must not duplicate tickets or overwrite decisions/evidence. Present source changes as a reviewed diff. Keep proposed additions in a separate namespace and show original versus added counts.

Track source requirement IDs R01–R18, test IDs T01–T56, story dependencies, owner roles, phase, profile, implementation state, approval state, evidence links and completion criteria on each card. Owner roles are not actual Jira assignees.

A software sub-scope may be accepted while its physical gate stays open. Record this as SIM scope accepted with BENCH pending; do not mark the complete original physical ticket or parent story Done. Show software milestone progress and whole-product qualification separately. Parent completion must roll up actual required child acceptance rather than an optimistic percentage.

This is a local Jira-style board. CSV export is required. Actual Jira authentication, synchronization, issue creation or messaging requires a separate approved integration ticket.

## 6. Phase plan grounded in the existing backlog

Propose and obtain approval for a dependency-aware roadmap before coding. Preserve the original dependencies. For simulation-only work, explicitly record when a typed mock satisfies an interface dependency without satisfying the underlying physical ticket.

Model readiness per evidence profile. An owner-approved mock interface contract may unlock a specific SIM scope through a dependency-substitution record containing the dependent ticket, original blocker, profile, contract/version, limitations and approval reference. It does not remove the original dependency, satisfy BENCH/V1 readiness or authorize closing the original ticket or parent. The transition service must enforce these distinctions; pending hardware must not prevent unrelated approved simulation work.

| Phase | Existing story coverage | Reviewable outcome |
| --- | --- | --- |
| P0 — Discovery | SV0-S01; inspect all stories | Source manifest, conflicts, original backlog, architecture proposal, phased plan and first ticket plan |
| P1 — Foundation and workbench | SV0-S01, early SV0-S12; approved workbench additions | Reproducible workspace, board, review lifecycle, persistent storage, two-tab shell, reference gallery |
| P2 — First complete SOS slice | SIM scope of SV0-S07, S09, S10, S11 with S12 controls | Qualified virtual button to journal, local API commit, guardian acknowledgment and pendant return; no GPS required |
| P3 — Sensors and hardware view | SIM scope of SV0-S02, S03, S04, S05, S11 | Exact component/pin explorer, deterministic sensor models, charts, fall prealert, tags and five-light behavior |
| P4 — Reliability and protocol detail | SV0-S07, S08, S09, S11, S12 SIM scope | Nicla/BLE codecs, queues, routing, authentication boundaries, retries, failures and replay visualized |
| P5 — Audio, privacy and complete app flows | SV0-S06, S10, S12 SIM scope | Synthetic voice path, half-duplex buffers, privacy handling, wearable/guardian flows and tool allowlist |
| P6 — Simulation acceptance and Wokwi | SV0-S11; SIM evidence contributing to S13 | Repeatable regression scenarios, evidence dashboard, documented Wokwi subset, simulation release review |
| P7 — Physical integration | SV0-S02 through S08 and S13, respecting physical dependencies | Purchased-module receiving, power review, one real adapter at a time, actual phone tests and measured bench evidence |
| P8 — Extensions and V1 | SV0-S14 after its required gates | Power/RF/cellular/Find My studies and a manufacturer handoff with unresolved gates explicit |

Preserve these original story meanings and prerequisites:

| Story | Meaning | Original prerequisites |
| --- | --- | --- |
| SV0-S01 | Baseline and reproducible workspace | None |
| SV0-S02 | Solder-free electrical bring-up | 01 |
| SV0-S03 | Nicla motion and wake coprocessor | 02 |
| SV0-S04 | Location and barometer adapters | 02, 03 |
| SV0-S05 | Physical interaction and feedback | 02, 07 |
| SV0-S06 | Audio and assistant integration | 02, 03, 12 |
| SV0-S07 | Safety reducer, journal and route policy | 01, 03 |
| SV0-S08 | BLE gateway and ownership | 07, 12 |
| SV0-S09 | Backend and escalation | 01, 07, 12 |
| SV0-S10 | Wearer and guardian apps | 08, 09 |
| SV0-S11 | Simulation and automated QA | 01, 07, 09 |
| SV0-S12 | Security, privacy and update controls | 01 |
| SV0-S13 | Bench qualification and release | 02–12 |
| SV0-S14 | V1 PCB and manufacturing handoff | 13 |

Add the following as proposed workbench tickets, linked to the existing stories. Approve their scope during P0; split large tickets into reviewable increments without changing source ticket identities:

- WB-001: source import, validation, provenance and traceability; links S01/S11.
- WB-002: application shell, navigation and document/diagram gallery; links S10/S11.
- WB-003: persistent Kanban, hierarchy, dependencies, filters and CSV export; links S01.
- WB-004: plan approval, acceptance, audit and ticket-document synchronization; links S01/S11.
- WB-005: deterministic run engine, C++ bridge, clock controls and read-only replay; links S07/S11.
- WB-006: interactive parts, exact pins/nets and power-domain visualization; links S02.
- WB-007: sensor, audio and actuator visualization panels; links S03–S06.
- WB-008: protocol inspector, packet journey and correlated timelines; links S03/S08/S09.
- WB-009: wearer/guardian web previews and cross-links to tickets; links S10.
- WB-010: scenario controls, fault injection, evidence dashboard and export; links S11/S13.
- WB-011…021: Wokwi/PlatformIO subset — firmware build, Lab API, Device Simulator panel, serial mirror, open-in-Wokwi, hold sync, doctor/evidence, scenario pixels, RGB fidelity, CLI smoke, limits banner; links SV0-11.01.

Do not rebuild backend or safety functionality in these tickets when an original ticket owns it. The workbench tickets provide the integration and visualization around that functionality.

## 7. Proposed implementation architecture

Inspect existing code before choosing dependencies. If this is a fresh workspace, propose the following default stack and confirm it in the P0 plan:

- React, TypeScript and Vite for the web application.
- Accessible components and a coherent design system; Tailwind CSS is optional if it reduces effort.
- SVG and React Flow for selectable hardware/system graphs and animated edges; a maintained chart library for sensor time series.
- Optional Three.js-based orientation view only after the core SVG interface works. Do not make a 3D renderer a prerequisite for the first useful demo.
- FastAPI and Python for the local API, deterministic simulation orchestration, mock adapters and evidence services.
- SQLite for local persistence, with explicit migrations, foreign keys, transactions and repository boundaries. Preserve the domain model so a future database change is isolated. Do not claim SQLite proves PostgreSQL concurrency behavior.
- A native C++17 executable wrapping the existing reducer through a versioned JSON-lines interface. Let the backend drive it; do not silently rewrite the safety core as independent React logic.
- Typed contracts derived from reviewed JSON Schema/OpenAPI, with runtime validation at boundaries.
- Unit/contract tests, backend integration tests and Playwright browser tests. Retain the supplied C++/Python baseline checks.
- PlatformIO and a separate Wokwi project for the supported firmware-emulation subset; native mobile tooling comes in the later phone milestone.

Pin compatible versions based on actual current documentation and the local Mac environment. Retain lockfiles and toolchain manifests. Do not install every possible framework, add cloud infrastructure, require a paid API or introduce Docker as a prerequisite without a reason in the approved plan.

Keep the architecture modular but runnable locally with a small number of processes. The browser sends commands and renders projections. The domain engine determines behavior. The backend validates and persists product actions. External notification, voice provider, radio and unavailable hardware interfaces use explicit mock adapters.

If a TypeScript core or WebAssembly becomes preferable later, propose an ADR and prove parity on the same fixtures before changing the source of truth. Never maintain two contradictory reducers.

## 8. Project structure and persisted state

Keep everything in one project folder. Use this structure or explain a simpler equivalent in the plan:

| Path | Responsibility |
| --- | --- |
| README_CURSOR_SVARAA_V0.md | This durable build instruction |
| README.md | Human setup, run, demo and troubleshooting guide |
| AGENTS.md; .cursor/rules/ | Concise persistent agent/lifecycle instructions |
| references/original/ | Untouched input files and assembly image |
| references/agent-pack/ | Untouched extracted source package |
| references/manifest.json | Source paths, hashes, versions and original identities |
| apps/workbench/ | Board, simulator, role previews and reference viewer |
| services/api/ | API, authorization, domain persistence and mock providers |
| services/simulator/ | Virtual clock, scenarios, models, adapters and trace orchestration |
| firmware/core/ | Reviewed working copy of the C++ core with source mapping |
| firmware/host-bridge/ | C++ JSON-lines adapter and protocol tests |
| firmware/nano/; firmware/nicla/ | Later board implementations, separate from pseudocode |
| contracts/ | Versioned working schemas and API/wire contracts |
| simulation/models/; simulation/fixtures/ | Deterministic sensor/network models and synthetic data |
| simulation/scenarios/; simulation/wokwi/ | Scenario definitions and separate emulation project |
| hardware/ | Derived component registry, netlist and reviewed mapping data |
| docs/tickets/<ticket-id>/ | Per-ticket specification, plan, implementation and review |
| docs/architecture/; docs/adr/ | System explanations and approved decisions |
| docs/phases/; docs/reviews/ | Phase plans and milestone acceptance |
| docs/traceability/ | Requirements-to-ticket-to-code-to-test mappings |
| docs/CURRENT_STATE.md; docs/NEXT_ACTION.md | Resume checkpoint and next permitted action |
| data/seeds/; data/exports/ | Synthetic seed data and portable snapshots |
| .workbench/ | Local runtime database, run data and local generated credentials; ignored by Git |
| tests/; evidence/<ticket-id>/<run-id>/ | Automated checks and actual execution evidence |
| scripts/; .github/workflows/ | Reproducible commands and CI when approved |

Choose one authority for runtime board state: the backend database. Original imported descriptions remain immutable source records. Ticket Markdown is the readable specification/plan; approval references its content digest. Have the backend validate that digest before beginning or accepting work. Export deterministic board snapshots and a human-readable ticket status section through one writer. Do not allow frontend localStorage, loose JSON and SQLite to become competing authorities.

Before the backend exists, use an explicitly versioned bootstrap planning snapshot and documents. Import that snapshot once with a recorded migration and then retire it as a writable authority. Restart and browser reload must preserve tickets, decisions, evidence references and completed run history. A server restart may mark an active run interrupted; do not pretend it continued if it did not.

Use localStorage only for harmless UI preferences. Detect document/state drift and show a reconciliation action; never silently overwrite a newer plan or fabricate approval. Keep secrets, raw personal audio and real location out of committed fixtures and evidence. Use synthetic households and device identities by default.

## 9. Persistent instructions and session continuity

During documentation bootstrap, merge these essential rules into the applicable AGENTS.md without deleting existing user instructions. Create a concise .cursor/rules/svaraa-lifecycle.mdc with valid MDC frontmatter and alwaysApply: true. Keep the approval rule, SIM/mock default, no invented physical evidence and checkpoint-reading requirement directly in the rule body; reference this README for the full specification.

At the start of each later session, read AGENTS.md, this prompt, docs/CURRENT_STATE.md, docs/NEXT_ACTION.md, the active ticket, its latest plan/approval and the board snapshot from its authority. Inspect the working tree and avoid overwriting my edits. Resume the last permitted action; do not start the project over or treat a summary as approval.

Use Git for small reviewable changes after the repository foundation is approved. Include ticket IDs in commits. Do not push, publish, deploy or alter remote Jira without authorization. If no commit exists yet, record a working-tree content digest rather than inventing a commit hash.

## 10. Web application layout

Build a polished desktop-first interface with usable narrower layouts, keyboard navigation, clear focus, readable contrast and reduced-motion support. Use the supplied Svaraa visual identity; plum/gold can guide the palette, but engineering information must remain legible. Avoid replacing the provided pendant design with a generic smartwatch.

The two primary tabs are Project Board and Device Simulator. Both share one backend, project state and selected context. Tab changes, route changes and component rerenders must not restart a scenario or reset an incident. Preserve selected ticket, filters, selected component, trace selection and replay position.

Use a shared header showing project, profile, backend connection, current scenario/run, seed, simulated time and active incident status. Display SIMULATED prominently. Within the simulator provide navigable subviews: Overview, Pendant, Hardware Bench, Sensors, Packet Explorer, System Architecture, App Previews, Scenarios/Faults, and Evidence/References.

Use a selected-object inspector, synchronized timeline and expandable logs. A ticket's Run scenario opens the simulator with its linked scenario. Selecting a component or packet offers View source, Open ticket, View tests and Show evidence. Provide direct routes/bookmarks to tickets, scenarios, runs and components. Keep operational wearer/guardian screens simple; put detailed engineering controls in the simulator shell.

## 11. Project Board requirements

Implement draggable cards with accessible keyboard/menu alternatives, epic/story expansion, subtasks, priority, phase, profile, blocker and owner-role labels. Include search and filters for status, source/added ticket, story, sensor, requirement, profile, approvals and evidence gaps.

The detail drawer must contain original scope, dependencies, acceptance criteria, latest plan, implementation notes, review discussion, actual tests, evidence links, changed files and source references. Provide a dependency view and show why a transition is unavailable.

Expose distinct owner actions: Approve plan, Request changes, Accept implementation, Reject acceptance and Reopen. Each action must target a displayed revision and require an intentional human interaction. Show approvals and history chronologically. Simulated product users and developer workflow actors must be separate concepts.

Provide a phase view and a useful progress summary: accepted software scope, tests actually passed, tests not run, blocked physical gates and unapproved work. Do not convert 56 planned scenarios into 56 passing tests. Show historical pack evidence under its source revision, separate from new execution evidence.

CSV import/export, project export, restore validation and reset behavior must be explicit. Reset simulation must never erase the board or approvals. Destructive project reset requires a clearly scoped user action and backup/export opportunity.

## 12. Interactive physical hardware visualization

Model the actual named baseline components and their roles:

- Arduino Nano ESP32 with factory headers ABX00083; Arduino Nicla Voice ABX00061.
- Nicla's onboard BMI270 motion sensor, BMM150 and wake microphone/NDP120 pipeline. Do not add a duplicate BMI270 purchase.
- BMP390 pressure sensor; SparkFun MAX-M10S GNSS and antenna.
- External pre-soldered INMP441 conversational microphone; MAX98357 amplifier and speaker.
- SN74AHCT125N PDIP buffer; Adafruit 3630 prewired 20-pixel strand, with only indices 0–4 active.
- Grove vibration motor and buzzer, dedicated SOS S1 and V0 software-privacy S2.
- Separate JH1 sensor hub and JH2 Nicla signal adapter, cables, passives, USB feeds and external 5 V distribution.

Provide a selectable 2D top view with actual component identities, zoom/pan, named pins, wire/net highlighting and inspectors. Show both Arduino header labels and raw GPIO numbers. Toggle signal, power, protocol, freshness and ticket-coverage overlays. Include all 38 connection records in a searchable table and link each to its source blueprint.

Load connections from the reviewed data files, not hardcoded illustration coordinates. Display these baseline mappings as a cross-check, and resolve any source disagreement before changing them:

| Function | Nano label / raw GPIO | Endpoint |
| --- | --- | --- |
| SOS input | D2 / 5 | S1 to ground; source-defined pull-up/filter |
| Private Nicla clock | D3 / 6 | Nicla J5.3 through isolated JH2 |
| Private Nicla data | D4 / 7 | Nicla J5.4 through isolated JH2 |
| I2S BCLK | D5 / 8 | INMP441 SCK and amplifier BCLK |
| I2S word select | D6 / 9 | INMP441 WS and amplifier LRC |
| Microphone receive | D7 / 10 | INMP441 SD into Nano |
| Amplifier transmit | D8 / 17 | Nano to amplifier DIN |
| Pixel data | D9 / 18 | AHCT125 input, buffer output through resistor to pixel DIN |
| Software privacy | D10 / 21 | S2 to ground |
| Haptic control | D12 / 47 | Grove vibration SIG |
| Buzzer control | A0 / 1 | Grove buzzer SIG |
| Main sensor data | A4 / 11 | JH1 SDA |
| Main sensor clock | A5 / 12 | JH1 SCL |

Main I2C: Nano is controller, BMP390 address 0x77 and MAX-M10S address 0x42. Private I2C: Nicla is controller, Nano is target 0x2A. Both proposed buses are 100 kHz/3.3 V and remain distinct. Do not draw Nano directly reading Nicla's internal sensor bus. Do not carry conversational PCM over the private I2C link.

Show JH2 V+ insulated/unconnected and Nicla separately USB-powered. Nano 3V3 powers the source-approved low-current sensors/microphone. External 5 V powers the amplifier, pixels, buffer and Grove loads. Grounds are common; positive rails remain separate. Nano VIN/VUSB headers stay unconnected in this USB profile. Display speaker OUT+ and OUT− as a differential pair, not a ground return. Read exact AHCT125 pins, pull-ups, resistors and capacitors from the source drawings/schedule.

Provide an assembly walkthrough and checks for duplicate pin use, incompatible voltage-domain annotations, unused reserved pins and accidental rail merges. Label these as static model checks. They cannot prove physical continuity, current capacity or that a breadboard was correctly assembled. Keep the supplied assembly image available alongside the deterministic wiring view, explicitly labeled illustrative.

## 13. Sensor and actuator visualization requirements

Every sensor panel must show source, units, acquisition time, freshness, validity, model/driver status and profile. Missing data must remain missing; stale data must be marked stale. Never generate a reassuring value to conceal a stopped sensor.

| Component | Visualizations and controls |
| --- | --- |
| BMI270 accelerometer | Synchronized X/Y/Z plots in declared units, magnitude, configurable gravity convention, saturation/gap flags, sample rate, calibration state; rest/walk/swing/fixture-drop presets |
| BMI270 gyroscope | X/Y/Z angular-rate plots, limits, bias/noise controls and synchronized motion timeline |
| Orientation | Optional manipulable pendant/axis model driven by the same scenario; label derived/simulated orientation and do not imply absolute yaw is observable without a qualified reference |
| BMM150 | Optional magnetic field panel, explicitly disabled/not acquired until an approved model or adapter exists; not required for baseline fall detection |
| BMP390 | Pressure trend, sample health, baseline-relative altitude if configured, baseline/drift controls; pressure is not a direct fall or body-temperature measurement |
| MAX-M10S | Track and fix status, source, age, estimated accuracy radius, coordinates, no-fix/stale states and acquisition-loss/recovery controls; offline coordinate view if map tiles are unavailable |
| Nicla wake pipeline | Synthetic wake event, model/class/confidence, wake enabled state, privacy request/result timeline; identify scripted events as scripted |
| INMP441 | Synthetic PCM waveform, capture state, sample rate, buffer occupancy, overflow/drop counters and stalled-consumer control |
| MAX98357 and speaker | Playback waveform/envelope, half-duplex state, queue levels and optional browser audio enabled by a user gesture |
| Five logical LEDs | One upper and four lower pendant lights; link color/pattern to actual state and explain it in text; bench strand shows all 20 with 5–19 off |
| Buzzer and haptic | Timeline of commanded patterns and duration; visible commanded/unknown-physical-output distinction |
| S1 SOS | Press, hold and release input, debounce timeline, hold progress and held-at-boot fault |
| S2 privacy | Requested/effective/privacy-applied states; software privacy label and visible remote-unmute rejection |
| Power | USB source and baseline battery_percent=null; separate optional explicitly synthetic battery/power fault models with provenance |

Keep plots time-aligned with packet and state timelines. Allow zoom, pause, cursors, raw sample inspection, units/axis explanations and CSV export. Downsample for display without altering domain decisions or losing the original samples required by a test. Make noise/drift deterministic through the seed. Define physical units and model assumptions; do not use independent random timers in each React component.

Use a seven-petal appearance where supported by the latest supplied design, one top status light and four lower programmable lights. Do not add extra active LEDs or side buttons to the final pendant appearance because the bench has additional controls. Show S2 as a V0 bench control. Do not infer final dimensions or a fabrication-ready enclosure from the picture.

## 14. Deterministic simulation engine

Implement a virtual clock and scheduled event queue with deterministic ordering, seeded randomness and bounded buffers. The clock drives sensor acquisition, debounce, hold duration, fall countdown, retries, transport delay, command expiry and mock escalation. Rendering frame rate never controls safety behavior.

Provide play, pause, resume, single-step, speed controls, restart scenario and create new run. Define tie-breaking for events with equal timestamps. Record run ID, seed, scenario version, contract/model versions and initial state. A run command must receive an explicit accepted/rejected result; repeated control requests must not accidentally duplicate actions.

Drive the existing C++ core through a typed bridge with declared input events, output effects, snapshots, errors and version negotiation. Bound message sizes and handle subprocess exit or malformed output visibly. Keep core-only replay tests fast. The wrapper supplies the clock, IDs and verified results; it must not accept a browser's arbitrary verified=true as proof of authentication.

Separate input generation, sensor/HAL adapters, reducer, journal, route selection, transport, backend transaction, notification provider and frontend projection. The same scenario should work headlessly and in the UI. Changes from sliders/buttons become timestamped inputs to the engine rather than direct edits to success indicators.

Distinguish deterministic domain simulation from actual local HTTP execution. Label simulated latency separately from measured host/network latency. If a test uses an in-process transport for deterministic scheduling, show that adapter. The integrated demo must also exercise the actual local API. Do not claim bit-for-bit timing reproducibility for host OS scheduling; compare canonical domain outcomes and recorded ordering.

Recorded-run replay must be read-only: scrubbing a timeline never resends an API request, acknowledgment or notification. A fork/rerun gets a new run identity and explicit state isolation. On refresh, reconnect to the active run and catch up from the server. On missing trace ranges, fetch a snapshot and visibly report the gap.

## 15. Packet movement and protocol explorer

Animate an edge only when an actual trace event exists. Use separate layers for electrical signals, protocol frames, domain events, API requests, durable transactions, notification attempts and human actions. Label model-generated transactions as simulated; do not invent real register traffic or waveforms for drivers that do not exist.

The end-to-end journey must expose sensor/input, controller, local journal, route selection, Wi-Fi or phone gateway, API validation, database commit, outbox, mock notification, guardian action, authenticated return and pendant feedback. Expand each layer on demand so the overview stays readable.

Represent queued, transmitting, link-acknowledged, dropped, corrupted, retrying, server-committed, human-acknowledged and resolved distinctly. I2C ACK, BLE indication confirmation, HTTP response, provider submission and human response are different events. A moving dot is never sufficient evidence of delivery.

Use a separate trace envelope with run_id, trace_id/span_id, causal parent, simulated timestamp, observed wall timestamp where relevant, layer, source/destination, protocol, outcome, attempt, queue delay, payload size and applicable device/boot/event/incident/command IDs. Include origin such as behavioral-model, encoded-codec, actual-local-http or measured-hardware. Show decoded fields, raw hex when available, checksum status and failure reason. Keep observability metadata outside the strict device-event schema.

Support packet filtering, payload search, pause/step, correlated waterfall/sequence view and export as JSONL. Selecting one SOS event should highlight every retry, route, receipt and related incident action. Show causal links rather than pretending every sensor sample has its own cloud event ID.

### Nicla private I2C detail

Implement the supplied 32-byte codec and display its byte layout: magic/version/type/flags, sequence, uptime, payload length, payload/padding, reserved byte and CRC. Preserve little-endian fields, magic 0x53, version 1, maximum 18-byte payload, zero padding and CRC16-CCITT-FALSE over bytes 0–29. Display the six-int16 IMU payload with acceleration in mg and angular rate in 0.1 degrees/s. Use contracts/reference_frame.py as a reference, with independent known vectors and malformed-frame tests.

Visualize the reverse eight-byte command mailbox and CRC8, proposed 10 Hz polling, command sequence, repeated-command behavior and command-result frame. Transfer ACK does not mean a privacy request was applied. Freeze undefined health/command-result layouts, flag bit assignments and sequence/uptime wrap handling in an approved contract decision before claiming complete byte-level interoperability.

### BLE and I2S detail

Load the GATT UUIDs and fragment format from contracts/ble_profile.yaml. Show the ten-byte fragment header, payload capacity ATT_MTU minus 3 minus 10, 2048-byte message limit, 255-fragment bound and 5000 ms reassembly timeout. Demonstrate MTU 23, out-of-order fragments, conflicting duplicates, missing fragments and CRC errors. BLE remains a behavioral adapter until real phone/board evidence exists; do not stream PCM through this event channel by implication.

I2S is a timed sample stream, not an acknowledged message bus. Show BCLK/WS relationships, capture/playback blocks and buffer pressure. Label the proposed 16 kHz, two 32-bit slots and 1.024 MHz BCLK as configured model parameters; physical alignment and timing remain a bench gate.

## 16. Emergency state and delivery invariants

Preserve the reducer's states Ready, Prealert, Pending, ServerAccepted, HumanAck and Resolved. Manual SOS can enter Pending directly. cancel_requested is an overlay on the active incident, not deletion or a replacement delivery phase.

- Manual SOS must work independently of wake word, GNSS fix, cloud AI and an open app screen.
- Model the proposed 20 ms debounce and two-second qualified hold. Require release after a held-at-boot input before arming.
- Model the proposed 20-second fall prealert. A short tap may cancel the un-escalated candidate; a manual hold can escalate without waiting for the countdown.
- Repeated holds in an active live incident must not create duplicate incidents.
- With no route, show local feedback and Pending/not delivered while retaining the event and attempting bounded retries.
- ServerAccepted requires a verified matching receipt after durable backend commit. HumanAck requires an authorized human action. Resolved requires an explicit authorized disposition.
- Reject wrong-incident, wrong-mode, unverified, stale-revision and phase-regressing updates.
- A genuine qualified manual input or sensor candidate preempts a drill. A laboratory live-mode event still cannot reach a real provider in the default environment.
- Never display Help is coming solely because a packet was sent, a provider accepted work or a frontend button was clicked.

Display the state machine, current state, last input, resulting effects, guards, cancel overlay and independent component health. Show the handoff's 150 ms feedback/200 ms scheduling values as design targets. Measure simulated or host timing in the proper profile; do not present it as measured pendant timing.

## 17. Location, custom tags, voice and privacy

Location must carry source, validity, latitude, longitude, accuracy_m, fix_at and age_ms. Use qualifying GNSS first and a consented nearby-phone fix only under the reviewed policy. Missing coordinates remain null; last-known fixes remain visibly historical. The initial proposed freshness policy is age at most 30 seconds and estimated accuracy at most 50 metres, configurable and not a positioning guarantee.

Send SOS without waiting for location. A later fix creates a new location.updated event on the same incident. Custom tags store a label and provenance; allow no-fix/offline tags with honest pending state. A label must not manufacture coordinates. Optional geofences need explicit dwell/hysteresis policy and separate validation.

Keep wake recognition on Nicla conceptually separate from external INMP441 conversational PCM. Use synthetic wake events, PCM and assistant responses first. Any real browser microphone requires my explicit enable action and a clear browser-source label. No ambient recording/upload by default. Browser audio playback must be opt-in, bounded and stoppable.

Model half-duplex capture/playback and bounded buffers. Audio and assistant work must not block manual SOS, the journal or emergency feedback. An allowlisted assistant tool may propose an authorized tag or query status; it cannot disable SOS, forge acknowledgment, erase incidents, change ownership or claim dispatch.

Effective privacy includes S2, local policy and authorized privacy-on. Remote privacy-off cannot override closed S2. Stop capture/upload and discard unsent audio. Show Nicla privacy requested, pending, applied, failed and unsupported separately. Do not claim the wake mic is muted merely because a command was sent. Preserve motion and manual SOS; an unresolved inability to mute independently must be exposed as a capability conflict. V0 S2 is software-enforced, not hard microphone isolation.

## 18. Product APIs, persistence and mock data

Implement the existing endpoint families without silently replacing their semantics:

| API | Behavior |
| --- | --- |
| POST /v1/device-events | Validate and atomically accept immutable device observations |
| GET /v1/incidents/{incident_id} | Return an authorized current snapshot/revision |
| POST /v1/incidents/{incident_id}/ack | Explicit authorized human acknowledgment |
| POST /v1/incidents/{incident_id}/resolve | Audited authorized resolution |
| POST /v1/incidents/{incident_id}/cancel-request | Record cancellation request overlay |
| GET /v1/devices/{device_id}/commands | Return bounded unexpired commands; reading is not execution |
| POST /v1/devices/{device_id}/commands/{command_id}/acks | Distinguish received, executed, rejected and expired |
| GET /v1/devices/{device_id}/snapshot | Capability/freshness-aware device state |
| POST /v1/location-tags | Authorized label with preserved provenance |
| POST /v1/drills | Server-issued drill identity and test-only scope |
| POST /v1/pairing-sessions | Reviewed ownership/physical-presence flow |
| POST /v1/voice-sessions | Explicit consent and scoped authorization |
| GET /v1/health | Minimal service liveness, not whole-device health |

Add workbench APIs under a separate namespace, proposed as /lab/v1/, for tickets, transitions, approvals, references, scenarios, runs, input commands, traces and evidence. Add a versioned WebSocket event stream with subscription/reconnect/resume semantics. These are new workbench contracts requiring plan review, not existing pendant firmware endpoints.

Before generating stable clients, freeze incomplete auxiliary request/response schemas, heartbeat/tag/drill payloads and error envelopes in the relevant S09/S12 contract work. Preserve schema_version 1.0 fields unless a reviewed version change is necessary. Existing event kinds include sos.created, sos.cancel_requested, device.heartbeat, location.updated, location.tagged and drill.step. A device upload cannot assert caregiver acknowledgment.

Required reliability behavior:

- Allocate one event ID per immutable observation. Retry original canonical bytes with the same event ID and Idempotency-Key.
- Create new event IDs for later location/cancel observations on the same incident. Never mutate a queued event to add newer data or a fault flag.
- Commit event, incident transition, receipt and outbox atomically before returning durable success.
- Identical duplicates converge on the stored receipt; conflicting bodies under the same ID return 409. Resolve the starter's duplicate-response convention in a reviewed contract decision.
- Two concurrent routes must not create duplicate incidents or outbox jobs.
- Human actions use action_id and expected_revision. Reuse action ID on retry and reconcile stale revisions; do not use silent last-writer-wins.
- On reboot, new observations get a new boot ID; replayed records retain their original IDs and body.
- Implement bounded queues, journal integrity/commit markers, partial-write recovery, critical-event capacity and observable degradation. Avoid writing every raw 100 Hz sample to persistent device storage.
- Use the proposed retry intervals 2, 4, 8, 16 and 30 seconds capped, with seeded jitter in simulation. Handle 401/403/409/422 differently from retryable timeout/5xx failures.
- Recheck incident state before delayed notification work. Provider submission is not human acknowledgment.

Seed at least two synthetic households, a wearer/guardian relationship, an unassigned guardian, a revoked assignment, multiple devices, sample tags, drills and incident histories. Enforce access in backend services, including detail and action endpoints. A frontend role toggle is a demo selector, not an authorization mechanism.

Generate development identities/keys locally as needed, keep them out of source and label them development-only. Do not ship a fleet secret or disable TLS verification. Restrict the local workbench to loopback by default; document local HTTP separately from authenticated remote HTTPS/WSS. Sharing or public deployment needs a separate approved plan.

Implement the authenticated return boundary from contracts/authenticated_relay.yaml with reviewed libraries and test vectors. Verify key/signature, audience, nonce, expiry/replay, incident/mode and revision before applying effects. CRC is not authentication. Unknown UTC requires an explicit reviewed policy; do not accept unsafe commands by assuming time. Keep real provisioning/native transport qualification open even if local signature tests pass.

## 19. Wearer and guardian web previews

Render both roles within the same simulator, side by side or in a sub-tab. Use the actual local APIs and authorization adapters. A guardian click must reach the backend and create its real local audit/command before the pendant projection changes.

Wearer: connection routes, source freshness, privacy, null-aware battery/location, SOS/prealert controls, pending/server-received/human-acknowledged/resolved states, tags and drill guidance.

Guardian: assigned wearers, stale/offline visibility, incident trigger/mode/time, location provenance/accuracy/age, timeline, acknowledge, resolve and cancellation request status. Show when the backend recorded acknowledgment but pendant confirmation is pending.

Use persistent drill labels, clear failure/retry states, large controls and text/icon cues alongside color. Refresh authoritative state on simulated app reopen/notification tap. Include permission loss, background/suspended/force-closed phone scenarios as modeled behaviors; a web preview cannot qualify native mobile radio lifecycle or guarantee a permanent connection.

## 20. Required scenario and fault library

Import and retain all T01–T56 source cases with their original profiles and status. Link new automated scenarios to them; do not replace physical procedures with synthetic tests. Convert the five supplied scenario descriptions into runnable cases after their plans are approved.

Provide executable, visual scenarios covering at least these groups:

| Group | Cases and expected visible behavior |
| --- | --- |
| Manual input | Short tap; qualified hold; repeated hold; bounce; held-at-boot; one incident only when appropriate |
| Location | No fix, stale fix, poor accuracy, late fix, phone permission denial, offline tag; provenance/nulls remain honest |
| Motion | Rest, walk, pendant swing, synthetic candidate, cancel prealert, timeout escalation, clipped/gapped/stale IMU |
| Routes | All routes down, Wi-Fi recovery, phone-only route, two-route duplicate, gateway reconnect and queued replay |
| Receipts | Failure before commit versus response lost after commit; retry same bytes; one durable event/outbox job |
| Human actions | Provider accepted without human ACK, delayed human ACK, stale revision, late receipt after ACK, resolve/cancel race |
| Drills | Valid drill, expired/invalid drill ID, manual live preemption, qualified sensor preemption; all notifications remain mock |
| Nicla | Corrupt CRC, bad version/length/padding, missing frame, stale sequence, controller reboot, privacy pending/failed |
| BLE | MTU 23, reordered/missing/conflicting fragments, oversize, CRC failure, timeout and reconnect |
| Storage | Journal full, corrupted tail, interrupted commit, reboot recovery, storage failure with visible volatile fallback |
| Audio/privacy | Slow consumer, buffer overflow, SOS during playback, privacy mid-capture, rejected remote unmute |
| Authorization | Wrong household/device, revoked guardian, forged return, replayed/expired command, unknown trusted time |
| Health/update | Sensor stopped while network healthy, stalled required task, supervised update/OTA model deferred during incident |
| Workbench | Tab switch/refresh without reset, stale approval revision, forbidden card transition, deterministic replay and evidence isolation |

Each scenario definition needs ID, version, seed, initial state, timestamped inputs, fault schedule, expected state/events, linked requirements/tickets/tests and evidence profile. Show expected versus observed, first divergence and links to the relevant packets. Synthetic fall traces demonstrate logic only; no clinical accuracy claim or dangerous human fall procedure.

Allow faults per layer with visible activation and reset. Distinguish dropping a simulated radio packet, failing an actual local HTTP call and hiding a rendering update. Test code must not assert success by setting the success state directly.

## 21. Testing, performance and evidence

Run unchanged source tests first where possible. Then test meaningful behavior at each boundary: core/codec vectors, schemas, state transitions, idempotent transactions, queue recovery, authorization, approval transitions and end-to-end browser flows. Add tests for real failure risks, not snapshots that merely repeat implementation constants.

Use a fake clock for deterministic domain tests. Exercise the actual local backend in integration tests and prove persistence across restart. Use Playwright to verify tab switching, ticket review, sensor interaction, packet selection, role actions, fault scenarios and read-only replay. Inspect layout and interaction at representative desktop/narrow viewports, keyboard navigation and reduced-motion settings.

Make a concrete performance proposal for approval: expected sensor rates, chart refresh, maximum retained samples, trace throughput, active runs and queue bounds. Test on the actual development machine and report its specs. Use batched rendering, chart downsampling and bounded buffers. Backpressure must be visible. Do not discard critical state events silently or infer hardware real-time guarantees from browser frame rate.

For every run, store ticket/run IDs, date, source/working-tree revision, profile, tool versions, command, exit code, scenario/seed, expected/actual result, logs, useful screenshots/traces, limitations and reviewer. Use passed, failed, blocked and not-run accurately. Record browser-only, host, Wokwi, bench and field evidence separately.

Build traceability from requirement to ticket to implementation to scenario/test to evidence. Surface orphaned requirements, missing tests and tests without an actual run. A successful pipeline cannot automatically provide owner acceptance or close physical/licensed gates.

## 22. Ticket documentation template

Create one folder per original ticket and approved added ticket inside docs/tickets/. An initial ticket.md must preserve source metadata and acceptance criteria for every imported item. Add detailed files when a ticket becomes active; avoid hundreds of empty decorative files.

Each active ticket must contain:

- ticket.md: ID/source ID, type, parent, original description, owner role, priority, dependencies, phase/profile, source references, requirements and acceptance criteria.
- plan.md: revision/hash, proposed design, ordered steps, affected files/contracts, mocks, test matrix, visual demo, risks, rollback and open decisions.
- implementation.md: what changed, why, actual files/interfaces, migration/config details, deviations and known limitations.
- tests.md: acceptance mapping, commands, results, evidence links and explicitly untested areas.
- review.md: my feedback, exact approval/acceptance records, agent review notes and revision history.

Use this ticket narrative structure:

    Problem and user outcome
    Source scope and requirement links
    Definition of ready and dependencies
    Approved implementation plan and revision
    Acceptance criteria, including negative cases
    Implementation and relevant code/contract links
    Actual validation and reproducible demonstration
    Evidence profile and remaining physical/external gates
    Owner review, changes requested and final acceptance
    Follow-ups, rollback and next dependency unlocked

Maintain machine-readable metadata with schema_version, ticket_id, source_id, source_hash, parent/dependencies, phase/profile, workflow state, implementation state, plan_revision/hash, approval references, acceptance references and evidence links. State changes go through the authoritative workflow service or its validated CLI, not manual edits to contradictory copies. Cite file/section/reference IDs for engineering decisions.

## 23. Commands, onboarding and developer experience

After the foundation plan is approved, provide scripts behind a simple root command interface. Proposed commands: make doctor, make setup, make dev, make test, make test-e2e, make seed, make demo, make export-evidence and make stop. Implement and verify each documented command before claiming it works. A package-script equivalent is acceptable if simpler.

Doctor checks the Mac architecture, Python, Node/package manager, C++ compiler and later PlatformIO/Wokwi prerequisites without changing the system. Setup uses pinned project-local dependencies. Dev starts the frontend, API and necessary bridge/orchestrator, prints exact local URLs and cleans up child processes. Seed is idempotent. Demo selects a documented synthetic scenario. Stop shuts down this project's processes only.

Explain expected startup output, first demo steps, port conflicts, dependency failures, database migrations, restarting after interruption and restoring exports. The core SIM experience must not require physical hardware, a cloud key, real notifications or a Wokwi license. Any later optional integration must show its own setup and status.

Keep mock APIs functional: actual local requests, validation, persistence and error handling. Do not deliver a frontend whose buttons only display toasts or a mock HTTP server that returns success regardless of input.

## 24. Wokwi, physical adapters and V1 boundaries

Keep the custom web behavioral simulator distinct from firmware emulation. Recheck the current Wokwi support matrix when implementing its ticket. The reviewed support matrix does not provide ESP32-S3 I2S, Bluetooth or I2C target-mode simulation. Use typed mocks for those boundaries and label them. Wokwi runs a built firmware image; the PlatformIO build and correct environment/pin mapping come first.

Provide a separate Wokwi project for supported buttons, GPIO/pixels and qualified network behavior. If embedding is unavailable or inappropriate, offer an explicit external-open action; do not promise a full Wokwi runtime inside the custom tab. Document licensing and local-network/gateway constraints if that optional path is used.

When I have purchased hardware, replace one approved adapter at a time. Preserve the zero-solder requirement: factory headers, compatible plug-in connectors, breadboard-compatible parts and prewired/screw-terminal assemblies. Keep bench instructions, receiving photos and measured evidence with the relevant tickets. Flashing, electrical integration and actual phone qualification require their concrete plans and reviews.

Do not invent a battery gauge in the USB baseline, a functioning cellular modem, an Apple Find My data API, production charging compatibility or a finished PCB. Custom geotags are software. Find My is a separate licensed lost-item integration; keep its program/dev-kit gates visible and do not feed invented Find My coordinates into SOS.

Cellular, battery/charging, hard microphone isolation, RF/enclosure and production test remain reviewed engineering work. Show their requirements, dependencies and evidence slots in the UI. Do not mark their capability operational because an extension card or animation exists. Produce a V1 dossier only from the actual completed work and clearly identified remaining gates.

## 25. Review response format

Before implementation, respond with:

    Ticket and source scope:
    Why this is the next unblocked task:
    Plan revision and concrete steps:
    Files/contracts and UI behavior affected:
    Mocks versus real local implementation:
    Acceptance and negative tests:
    Demonstration I will be able to review:
    Risks, unresolved decisions and rollback:
    Approval requested: this ticket's stated plan revision only.

After implementation, respond with:

    Ticket and approved plan:
    What changed and why:
    How to open and exercise the result:
    Tests actually run and their results:
    Evidence and documentation paths:
    Remaining mocks, blockers and limitations:
    Acceptance criteria met or unmet:
    Owner decision requested:
    Proposed next ticket, without starting it:

Be candid about failures and unavailable tools. A test marked not-run is better than an invented pass. If the browser cannot be inspected in your environment, say so and give me a concrete manual review procedure; do not claim visual QA occurred.

## 26. Definition of the first complete simulation milestone

Request milestone acceptance only when:

1. A fresh setup can run the local app from documented commands.
2. All original 87 backlog items and their hierarchy are preserved; added work is identified separately.
3. The board persists reviews/status and enforces plan approval and owner acceptance.
4. Board/Simulator tab switching does not reset active behavior.
5. The exact named components, pins, buses, power-domain annotations and source diagrams are browsable.
6. Sensor, audio and actuator models produce meaningful inspectable data with explicit provenance.
7. The supplied C++ core participates in the simulation through a tested bridge, or an approved parity-proven alternative.
8. Manual SOS can move through local creation, durable API acceptance, human acknowledgment and pendant return while showing every layer.
9. No-route, stale/no-fix, duplicate, lost receipt, privacy, drill preemption and authorization failures behave honestly.
10. Packet animations correspond to trace records, and replay cannot repeat side effects.
11. Wearer/guardian previews use local APIs and show server versus pendant confirmation separately.
12. Each completed ticket has a reviewed plan, implementation notes, actual tests, evidence and owner acceptance.
13. Physical, mobile, licensed and V1 qualifications remain explicitly open where their evidence is unavailable.

Passing this milestone means a reviewed software demonstrator. It does not mean every original manufacturing or bench ticket is Done.

## 27. Your first action now

Do **P0 discovery only**. This prompt authorizes reading the supplied workspace files, safely extracting the pack, calculating manifests, inspecting images/diagrams, documenting source conflicts, importing a planning snapshot and drafting the roadmap and first ticket plan. You may run the unchanged source host tests using already available dependencies and temporary build outputs. If tools/dependencies are missing, record not-run and put installation in the foundation plan.

Create only the documentation/bootstrap records and concise persistent lifecycle instructions needed for this review. Do not scaffold application code, install packages, change hardware contracts, start product implementation or claim the board already exists before my approval.

Your first response must include the actual files found and read, source counts, available/missing tooling, baseline tests actually executed, important gaps, proposed architecture, phase/dependency map, proposed workbench tickets, and a detailed plan for the first original ticket SV0-01.01. Present any decisions that genuinely require my input with a recommendation and consequence. Then ask me to approve the roadmap and that first ticket plan, and wait.

After approval, follow the lifecycle above until the agreed work is complete. Keep this folder usable by another developer or a new Cursor session at every checkpoint.

## 28. Reference handling

Preserve every entry in the source pack's docs/references.json, map S01–S39 into the local reference viewer and cite the relevant source IDs in ticket plans and engineering notes. Use the shipped contracts/CSV/SVG/source files as local citations with hashes and paths. Review relevant current primary documentation when selecting software versions or implementing an adapter; record checked dates and unavailable references without inventing their contents.

Additional implementation references for the proposed workbench:

- Cursor rules: https://cursor.com/docs/rules
- Cursor planning: https://cursor.com/docs/agent/plan-mode
- FastAPI WebSockets: https://fastapi.tiangolo.com/advanced/websockets/
- React Flow custom edges: https://reactflow.dev/learn/customization/custom-edges
- Wokwi ESP32 support: https://docs.wokwi.com/guides/esp32
- Wokwi with PlatformIO: https://docs.wokwi.com/vscode/platformio
- Apple Find My program: https://developer.apple.com/find-my/

Do not substitute an attractive visual or an agent's confidence for a tested contract, an actual measurement or my recorded approval.
