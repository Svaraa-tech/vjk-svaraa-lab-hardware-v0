# Svaraa V0 — scope, profiles, and evidence vocabulary

Ticket: **SV0-01.01** (plan v0.2)  
Updated: 2026-11-17  
Default runtime: `SVARAA_PROFILE=SIM`, `notification_provider=mock`

This document freezes how we describe capability state. It does **not** certify hardware, phones, licensed programs, or manufacturing readiness.

---

## 1. Profiles

| Profile | Demonstrates | Does **not** prove |
| --- | --- | --- |
| **V0-A SIM** | Host core, behavioral models, local API/DB, mock external services, workbench UI driven by traces | Sensor accuracy, physical timing, BLE radio, battery life, Find My, clinical falls, solder-free assembly quality |
| **V0-B BENCH** | Purchased USB-powered modules, measured rails/continuity, real adapters one at a time | Wearable enclosure runtime, cellular, public dispatch, production readiness |
| **V0-C EXTENSION** | Separate qualified studies (cellular DK, Find My program work, power/charging) | Automatic product integration from buying a kit |
| **V1 PRODUCT** | Custom PCB, enclosure, production engineering, qualification dossier | That a breadboard copy is shippable |

Incident mode `live` / `drill` is independent of profile. A lab LIVE SOS still uses the **mock** notification provider until an explicit later approval.

---

## 2. Independent status fields

Never collapse these into one “green” flag.

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `implementation_state` | `not_started` · `in_progress` · `implemented_sim` · `implemented_bench` · `deferred` · `blocked` | Code/model presence for a scope |
| `test_result` | `not-run` · `passed` · `failed` · `blocked` | Last **actual** execution for a named test/scenario |
| `evidence_profile` | `SIM` · `Host` · `BENCH` · `Phone` · `Wokwi` · `Review` · `Gated` · `Field` | What kind of evidence was produced |
| `owner_acceptance` | `none` · `changes_requested` · `accepted_sim_scope` · `accepted_full` | Human acceptance only |

Rules:

- A passing mock or UI animation cannot set `owner_acceptance` or close a physical gate.
- Historical pack evidence is labeled `source_revision=pack` and is **not** a new run.
- `accepted_sim_scope` may unlock further SIM work via a substitution record; parent physical tickets stay open.

### SIM dependency-substitution record (template)

```yaml
dependent_ticket: SV0-xx.yy
original_blocker: SV0-0n.mm   # physical or unimplemented interface
profile: SIM
contract: path/or/name@version
limitations: "..."
approval_ref: "APPROVE ... timestamp/actor"
does_not: ["close original ticket", "satisfy BENCH", "authorize V1"]
```

---

## 3. Evidence vocabulary labels

| Label | Use when |
| --- | --- |
| Vendor fact | Cited primary datasheet/API; verify received revision |
| Proposed V0 design | Our selected pin/protocol/timing; must be implemented and qualified |
| Host tested | Host executable checks actually run in this environment |
| Physical gate | Needs boards/instruments/phones/field |
| Licensed / V1 gate | Needs program membership, supplier validation, or product engineering |

Delivery phases remain distinct: local trigger → durable server receipt → human acknowledgment → resolution. Provider submission ≠ human ACK. “Help is coming” requires authorized human disposition policy — never packet-sent alone.

---

## 4. Lab UI theme basis (owner amendment)

Web Lab light/dark modes follow **https://www.svaraa.ai/** tokens.

- Full token tables: `docs/architecture/ui_theme_svaraa.md`
- Screenshots: `evidence/SV0-01.01/theme/svaraa-light.png`, `svaraa-dark.png`
- Light: warm canvas `#fbf7f2`, plum primary `#6f1d47`, gold `#b88a44`
- Dark: canvas `#18171a`, gold primary `#e2bd72`, ink `#e9e3dc`
- Fonts: Inter + Newsreader (+ Devanagari fallbacks)
- Engineering readability overrides marketing softness where they conflict

Implementation of the theme lands in **WB-002**; vocabulary is frozen here.

---

## 5. Capability matrix (initial)

Status snapshot at SV0-01.01 completion. Almost all product capabilities remain `not_started` pending later tickets.

### 5.1 Power and electrical

| Capability | impl | test | evidence | notes |
| --- | --- | --- | --- | --- |
| USB Nano + Nicla dual feed | not_started | not-run | — | BENCH gate SV0-02.* |
| EXT_5V load rail segregated | not_started | not-run | — | Never join positives |
| Nano 3V3 sensor/mic domain | not_started | not-run | — | |
| battery_percent | deferred | not-run | Gated | **null** on USB baseline; no invented gauge |
| JH2 V+ insulated | not_started | not-run | — | J5.1 is 5V input |

### 5.2 Buses and pins

| Capability | impl | test | evidence | notes |
| --- | --- | --- | --- | --- |
| Main I2C A4/A5 @ 100 kHz | not_started | not-run | — | BMP390 0x77, MAX-M10S 0x42 |
| Private Nicla I2C D4/D3 | not_started | not-run | — | Nicla controller; Nano 0x2A |
| I2S D5–D8 | not_started | not-run | — | Model params ≠ bench timing |
| GPIO SOS D2 / privacy D10 | not_started | not-run | — | |
| Pixels via AHCT125 D9 | not_started | not-run | — | Five logical; 5–19 off |
| Haptic D12 / buzzer A0 | not_started | not-run | — | EXT_5V Grove |

### 5.3 Sensors / audio / actuators

| Capability | impl | test | evidence | notes |
| --- | --- | --- | --- | --- |
| BMI270 motion | not_started | not-run | — | On Nicla; no duplicate purchase |
| BMM150 | deferred | not-run | — | Not required for baseline fall |
| BMP390 pressure | not_started | not-run | — | Not body temperature / direct fall |
| MAX-M10S GNSS | not_started | not-run | — | Null/stale honest |
| Nicla wake pipeline | not_started | not-run | — | Scripted ≠ recognized |
| INMP441 / MAX98357 | not_started | not-run | — | Synthetic first |
| Five-light pendant UX | not_started | not-run | — | Appearance ≠ extra LEDs |

### 5.4 Safety core and delivery

| Capability | impl | test | evidence | notes |
| --- | --- | --- | --- | --- |
| C++ reducer `sos_core` | implemented_sim | **passed** (host re-run) | Host | 31 checks 2026-11-18; see evidence |
| Typed HAL ports (Clock…Transport) | implemented_sim | **passed** | Host | SV0-01.03 mocks + board stubs; not BENCH |
| Manual SOS independent of GPS/AI | not_started | not-run | — | Product path P2 |
| Fall prealert 20 s | not_started | not-run | — | Experimental; not clinical |
| Journal + idempotent upload | not_started | not-run | — | |
| Mock notification provider | not_started | not-run | — | Default forever until approved otherwise |
| Human ACK / resolve | not_started | not-run | — | |
| Authenticated return | not_started | not-run | — | CRC ≠ auth |

### 5.5 Transports and apps

| Capability | impl | test | evidence | notes |
| --- | --- | --- | --- | --- |
| Local FastAPI product APIs | not_started | not-run | — | Schemas incomplete (SC-002) |
| BLE GATT gateway | not_started | not-run | — | Behavioral until Phone evidence |
| Wearer/guardian web previews | not_started | not-run | — | Not native app qualification |
| Drill vs live isolation | not_started | not-run | — | |

### 5.6 Gated extensions

| Capability | impl | test | evidence | notes |
| --- | --- | --- | --- | --- |
| Cellular data SOS | deferred | not-run | Gated | V0-C / S14 |
| Apple Find My | deferred | not-run | Gated | Licensed; no invented coords into SOS |
| Hard mic isolation | deferred | not-run | Gated | V1; S2 is software privacy in V0 |
| Custom PCB / enclosure | deferred | not-run | Gated | V1 |

### 5.7 Workbench

| Capability | impl | test | evidence | notes |
| --- | --- | --- | --- | --- |
| Evidence vocabulary (this doc) | implemented_sim | passed (review) | Review | SV0-01.01 |
| UI theme basis extract | implemented_sim | passed (review) | Review | svaraa.ai |
| Toolchain CLT/Node/Python | implemented_sim | passed | Host | User-local Node+uv; brew blocked without sudo |
| Project Board UI | not_started | not-run | — | WB-003/004 |
| Device Simulator UI | not_started | not-run | — | WB-002/005–010 |
| Trace-driven animations | not_started | not-run | — | Must not be decorative |

---

## 6. Toolchain decision (owner amendment)

Installs are **not** deferred to SV0-01.02.

| Component | Status on this Mac (2026-11-17/18) |
| --- | --- |
| Xcode CLT 27.2 | Installed (`/Library/Developer/CommandLineTools`) |
| Apple clang | 21.0.0 |
| Node.js | v22.21.1 user-local (`~/.local/node-v22.21.1-darwin-arm64`) |
| npm | 10.9.4 |
| Python 3.12.16 | via `uv` user-local |
| Homebrew to `/opt/homebrew` | **Blocked** — requires sudo; not installed |
| PlatformIO / Wokwi | Not installed yet (later tickets) |

Shell helper: `scripts/env.sh`.

Repo scaffold (`apps/`, `services/`, lockfiles) remains **SV0-01.02**.

---

## 7. Open contract decisions (do not silently close)

| ID | Topic | Status |
| --- | --- | --- |
| SC-002 | Incomplete OpenAPI response schemas | open → S09/S12 |
| SC-007 | Nicla health/command-result layouts | open → ADR before full interoperability claim |
| SC-008 | Duplicate idempotent ingest response | open → recommend stable 200 + stored receipt |

---

## 8. What “Done” means for this ticket

SV0-01.01 is complete when the owner accepts that:

1. Profiles and independent status fields are defined as above.
2. Capability matrix covers the groups in §5 with honest statuses.
3. Svaraa.ai light/dark basis is recorded.
4. Toolchain install outcome is recorded honestly (including Homebrew sudo limit).
5. No physical/licensed capability is marked qualified.

Parent story SV0-S01 remains open until 01.02–01.05 (and linked WB work) meet their own acceptance.
