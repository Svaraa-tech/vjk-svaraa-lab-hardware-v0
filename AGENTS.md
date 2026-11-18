# Svaraa V0 Lab — agent instructions

Project root: this `Svaraa_V0_Lab` folder. Full build contract: `README_CURSOR_SVARAA_V0.md`. Launch guide: `START_HERE.md`.

## Session start

1. Read `AGENTS.md`, `README_CURSOR_SVARAA_V0.md`, `docs/CURRENT_STATE.md`, `docs/NEXT_ACTION.md`.
2. Read the active ticket under `docs/tickets/<id>/`, its latest `plan.md`, and any approval in `review.md`.
3. Load board authority: until the API exists, `data/seeds/board_bootstrap_v0.1.json`; afterward, the backend database.
4. Inspect the working tree. Do not overwrite owner edits. Resume the last permitted action only.

## Lifecycle (mandatory)

For every ticket: Understand → Plan → Await plan approval → Implement approved scope → Test → Document/demonstrate → Await acceptance → Mark Done only after owner acceptance.

- One active implementation ticket at a time unless a named batch is explicitly approved.
- Approvals are revision-bound (`APPROVE PLAN <id> v<rev>`). Silence, tests, or prior phase approval is not permission.
- Do not impersonate the owner or fabricate approvals from agent/test actions.

## Defaults and honesty

- Default `SVARAA_PROFILE=SIM` and `notification_provider=mock`.
- Never invent physical, phone, licensed, battery, Find My, or clinical evidence from mocks/UI.
- Preserve zero-solder path; do not merge rails or invent pins from illustrations.
- Pins/nets come from CSVs and reviewed blueprints, never from breadboard hole appearance.
- Distinguish SIM-accepted software sub-scope from BENCH/V1 parent completion.
- Keep source tickets intact; proposed workbench tickets use the `WB-*` namespace.

## Source authority

- Originals: `references/original/` (do not overwrite).
- Extracted pack: `references/agent-pack/Svaraa_V0_Engineer_Agent_Pack/` (do not re-extract over it).
- Hashes: `references/manifest.json`.
- Record conflicts in `docs/SOURCE_CONFLICTS.md`.

## Implementation boundaries

- Do not scaffold application code, install packages, or start product implementation until the roadmap and current ticket plan are approved.
- Prefer the README default stack unless an ADR is approved.
- Drive the C++ safety core through a versioned bridge; do not silently reimplement a second reducer in React.
- Animations must map to real simulation/trace events.
