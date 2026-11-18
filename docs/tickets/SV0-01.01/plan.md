# Plan — SV0-01.01 Freeze scope and evidence vocabulary

**Plan revision:** v0.2  
**Supersedes:** v0.1  
**Plan content digest (sha256):** *see review.md after freeze*  
**Workflow target after approval:** In Progress → Testing → Awaiting Acceptance  
**Profile:** SIM (documentation + immediate toolchain bootstrap)

## Ticket and source scope

Original subtask **1011 / SV0-01.01**: record SIM, USB BENCH, and gated extensions in `docs/decisions.md`; every capability has implemented/mocked/blocked status; no implied certification.

## Owner-approved amendments (2026-11-17)

1. **UI basis:** Lab web UI light/dark modes follow https://www.svaraa.ai/ design tokens (plum/gold identity; extracted CSS variables recorded in decisions).
2. **Toolchain now:** Do **not** defer Xcode CLT / Node / Python installs to SV0-01.02 — install immediately as part of this continuation.
3. Remainder of P0 recommendations accepted (roadmap P0-v0.1, arch-v0.1, WB-001…010, Lab root).

## Why this is next

SV0-S01 has no prerequisites. Vocabulary + environment must exist before repository scaffolding (01.02) and workbench import (WB-001).

## Concrete steps

1. Create `docs/decisions.md` as the living scope/evidence vocabulary document.
2. Define profiles: V0-A SIM, V0-B BENCH, V0-C EXTENSION, V1 PRODUCT — each with proves / does not prove.
3. Define independent status fields (`implementation_state`, `test_result`, `evidence_profile`, `owner_acceptance`).
4. Build capability matrix across hardware, safety, transport, apps, gated extensions, and workbench.
5. Record Svaraa.ai light/dark token tables as the Lab visual basis (engineering contrast still required).
6. Define SIM dependency-substitution record template.
7. Install Xcode CLT, Homebrew, Node, and Python on this Mac; record versions in evidence.
8. Re-run unchanged pack baseline host tests if tools allow; otherwise keep not-run with reason.
9. Write implementation.md / tests.md; store evidence under `evidence/SV0-01.01/`.
10. Demonstrate matrix + theme tokens + toolchain/baseline results; request acceptance.

## Affected files / contracts

| Path | Action |
| --- | --- |
| `docs/decisions.md` | Create |
| `docs/architecture/ui_theme_svaraa.md` | Create (token extract) |
| `docs/tickets/SV0-01.01/*` | Update |
| `evidence/SV0-01.01/...` | Create |
| `evidence/P0_discovery/*` | Tool install logs |
| `data/seeds/board_bootstrap_v0.1.json` | Workflow fields |
| Hardware contracts / app scaffold | **unchanged in this ticket** (scaffold remains SV0-01.02) |

## UI behavior affected

None rendered yet. Decisions freeze the future Lab theme contract for WB-002+.

## Mocks vs real local implementation

- Documentation is real.
- Toolchain installs are real host changes.
- Baseline tests are real re-runs when possible.
- No product UI/runtime mocks introduced here.

## Acceptance and negative tests

| ID | Check |
| --- | --- |
| A1 | Every matrix capability has an explicit status vocabulary value |
| A2 | SIM cannot be labeled as physical qualification |
| A3 | LIVE SOS + mock provider distinction documented |
| A4 | Battery percent null under USB baseline documented |
| A5 | Find My / cellular / hard mic isolation marked gated |
| A6 | Light + dark Svaraa.ai token tables recorded |
| A7 | CLT/Node/Python installed or blocked with explicit owner-visible reason |
| N1 | Must not mark T01–T07 electrical tests passed |
| N2 | Historical 31/15 checks not relabeled as new unless re-executed |

## Demonstration

Owner reviews `docs/decisions.md`, theme extract, and evidence of toolchain + any baseline re-run.

## Risks, assumptions, rollback

| Risk | Mitigation |
| --- | --- |
| CLT/Homebrew requires privileges / time | Log actual outcome; do not invent success |
| Scope bleed into full 01.02 scaffold | Explicit: installs yes, app folders no until 01.02 plan |
| Theme vs engineering density | Tokens guide brand; charts/board must stay legible |

Rollback: revert decisions/theme docs; toolchain uninstall not automatic (leave installed tools).

## Approval requested / recorded

Owner message approved v0.1 with amendments above → treated as **APPROVE PLAN SV0-01.01 v0.2**.
