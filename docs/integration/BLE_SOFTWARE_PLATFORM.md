# BLE software-platform integration guide

Audience: mobile / backend engineers wiring the **Svaraa V0 pendant** into the product software platform over **Bluetooth Low Energy**.

Contracts in this repo are the source of truth:

| Contract | Path |
| --- | --- |
| GATT + fragment rules | `contracts/ble_profile.yaml` |
| Device event JSON | `contracts/device_event.schema.json` |
| Example SOS payload | `contracts/example_event.json` |
| Authenticated return envelope | `contracts/authenticated_relay.yaml` |
| Lab SIM assembler | `services/simulator/protocol.py` (`BleAssembler`) |

**Honest scope:** Wokwi / Device Simulator do **not** emulate a phone radio. Use them for SOS reducer, pixels, and API behavior. Native BLE scan/connect/reconnect is a phone + board gate.

---

## 1. Architecture

```
Pendant (Nano / ESP32-S3 product FW)
    │  BLE GATT (event_tx / command_rx / status)
    ▼
Phone app (BLE gateway + ownership holder)
    │  HTTPS  POST /v1/device-events …
    ▼
Software platform (API + incidents + outbox + guardians)
    │  authenticated_return over BLE command_rx
    ▼
Pendant feedback (pixels / buzzer phase)
```

Roles:

| Layer | Owns |
| --- | --- |
| Pendant | Qualify SOS, journal events, fragment over BLE, local feedback |
| Phone app | Scan/connect, reassemble fragments, upload events, pull commands, write authenticated returns |
| Platform | Durable commit, receipts, guardian ACK/resolve, notification outbox |

Manual SOS must work even if the app UI is backgrounded — treat BLE as a **gateway**, not as the SOS authority UI.

---

## 2. GATT profile (`contracts/ble_profile.yaml`)

| Item | Value |
| --- | --- |
| Service UUID | `b7e40000-6b6d-4f2d-9f42-8a645f6c1000` |
| `event_tx` | `b7e40001-…1000` — **indicate** (device → phone) |
| `command_rx` | `b7e40002-…1000` — **write with response** (phone → device) |
| `status` | `b7e40003-…1000` — **read / notify** |

Suggested flow:

1. Scan for service UUID (or product name once frozen).
2. Connect + request MTU (expect **23** worst-case; negotiate higher when available).
3. Subscribe to `event_tx` indications and `status` notifications.
4. On complete reassembly of an **event** message → `POST /v1/device-events`.
5. After verified server receipt / guardian command → write **authenticated_return** fragments to `command_rx`.

---

## 3. Fragment framing

Every BLE indication/write value is:

```
[10-byte header][payload chunk]
```

Header (little-endian), 10 bytes:

| Offset | Type | Field |
| --- | --- | --- |
| 0 | u8 | `version` = **1** |
| 1 | u8 | `kind` (see below) |
| 2 | u16 | `msg_id` |
| 4 | u8 | `index` (0-based) |
| 5 | u8 | `count` |
| 6 | u16 | `total_length` (full payload bytes) |
| 8 | u16 | `complete_payload_CRC16` (CCITT-FALSE) |

Limits:

| Rule | Value |
| --- | --- |
| Payload per fragment | `ATT_MTU − 3 − 10` (MTU 23 → **10** bytes) |
| Max reassembled message | **2048** bytes |
| Max fragments | **255** |
| Reassembly timeout | **5000** ms |
| Index base | 0 |

Kinds:

| `kind` | Name | Direction | Body |
| --- | --- | --- | --- |
| 1 | `event` | device → phone | UTF-8 JSON `DeviceEvent` |
| 2 | `authenticated_return` | phone → device | Signed relay envelope (see §6) |
| 3 | `status` | either | Compact status / capability snapshot |

Assembler rules (must match Lab `BleAssembler`):

- Reject short fragments (`< 10` bytes).
- Reject `version ≠ 1`, oversize `total_length`, conflicting duplicates (same `msg_id` with mismatched count/total/crc).
- Verify CRC16 over the **full** reassembled payload before accepting.
- **CRC is integrity, not authentication.**
- Do **not** stream PCM / raw audio on this channel.

### Pseudocode (phone)

```text
onIndication(bytes):
  hdr = parseHeader(bytes[0:10])
  slot = buffers[hdr.msg_id] or create(hdr)
  reject if conflict(slot, hdr)
  slot.parts[hdr.index] = bytes[10:]
  if len(slot.parts) == hdr.count:
    payload = join(parts 0..count-1)
    assert len(payload) == hdr.total_length
    assert crc16(payload) == hdr.crc
    dispatch(hdr.kind, payload)
    delete buffers[hdr.msg_id]
  else if now - slot.t > 5000ms:
    drop slot
```

---

## 4. Device event payload (platform ingest)

After reassembly of `kind=event`, parse JSON against `contracts/device_event.schema.json`.

Minimum SOS upload (`sos.created`) — see `contracts/example_event.json`:

```json
{
  "schema_version": "1.0",
  "event_id": "<uuid>",
  "device_id": "sv0-…",
  "boot_id": "<uuid>",
  "seq": 1,
  "mode": "live",
  "kind": "sos.created",
  "occurred_at": null,
  "uptime_ms": 12345,
  "incident_id": "<uuid>",
  "drill_id": null,
  "payload": {
    "trigger": "manual_button",
    "location": {
      "source": "none",
      "valid": false,
      "latitude": null,
      "longitude": null,
      "accuracy_m": null,
      "fix_at": null,
      "age_ms": null
    },
    "battery_percent": null,
    "model_version": null
  }
}
```

Ingest:

```http
POST /v1/device-events
Content-Type: application/json
Idempotency-Key: <same as event_id>
X-Svaraa-Tenant: <device_id>   # lab check; product auth TBD
```

Reliability:

- One immutable `event_id` per observation. Retries resend **identical** bytes + same Idempotency-Key.
- Duplicate identical body → converge on stored receipt.
- Conflicting body under same `event_id` → **409**.
- Later location / cancel = **new** `event_id` on the **same** `incident_id`.
- Device upload **cannot** assert caregiver ACK.

Event kinds (schema): `sos.created`, `sos.cancel_requested`, `device.heartbeat`, `location.updated`, `location.tagged`, `drill.step`.

---

## 5. Platform APIs the phone / backend must use

| API | Purpose |
| --- | --- |
| `POST /v1/device-events` | Accept device observations (BLE → platform) |
| `GET /v1/incidents/{id}` | Authoritative incident snapshot / revision |
| `POST /v1/incidents/{id}/ack` | Authorized **human** ACK |
| `POST /v1/incidents/{id}/resolve` | Authorized resolve |
| `POST /v1/incidents/{id}/cancel-request` | Cancel overlay (not delete) |
| `GET /v1/devices/{id}/commands` | Bounded unexpired commands (read ≠ execute) |
| `POST /v1/devices/{id}/commands/{cid}/acks` | received / executed / rejected / expired |
| `GET /v1/devices/{id}/snapshot` | Capability / freshness aware state |
| `POST /v1/pairing-sessions` | Ownership / physical-presence pairing (reviewed) |
| `GET /v1/health` | Service liveness only |

Lab workbench extras live under `/lab/v1/*` and are **not** product phone contracts.

---

## 6. Authenticated return (phone → pendant)

After durable server commit / human action, the phone writes `kind=authenticated_return` fragments to `command_rx`.

Envelope fields (`contracts/authenticated_relay.yaml`):

`auth_version`, `key_id`, `audience_device_id`, `request_nonce`, `issued_at`, `expires_at`, `payload_b64`, `signature_b64`

Rules:

- Ed25519; **server private key never on device**.
- Canonicalize unsigned outer fields (RFC 8785) before verify.
- Bind audience device, nonce, incident/mode; enforce expiry + replay protection.
- Never regress human acknowledgment.
- Physical privacy switch **overrides** every remote privacy-off.
- **ATT write response ≠ caregiver ACK ≠ server receipt.** Treat them as three different events in UI and telemetry.

---

## 7. SOS phases the app must mirror

| Phase | Pendant UX (SIM) | Alarm sound | App meaning |
| --- | --- | --- | --- |
| Ready | dim status | off | Idle |
| Prealert | amber subset | off | Hold in progress / fall prealert |
| Pending | **all 5 lights red** | **on** | SOS committed locally; awaiting durable server |
| ServerAccepted | **all 5 lights red** | **on** | Verified backend receipt |
| HumanAck | green all | off | Authorized guardian ACK applied |
| Resolved | blue status | off | Explicit disposition |

Invariant: **while buzzer/haptic alarm is on, all face lights are solid red.**

Do not show “Help is coming” solely because a BLE indication was sent or a provider accepted a job.

---

## 8. Mobile integration checklist

### Connect

- [ ] Request Bluetooth permission; handle revoke mid-incident (`link_status` / OS denial).
- [ ] Filter by service UUID; store bonded device after pairing-session success.
- [ ] Negotiate MTU; always remain correct at MTU **23**.
- [ ] Enable CCCD for `event_tx` + `status`.

### Ingress (device → cloud)

- [ ] Reassemble with timeout / CRC / conflict rejection.
- [ ] Validate JSON schema before upload.
- [ ] POST with idempotent retries (2/4/8/16/30s + jitter).
- [ ] Map 401/403/409/422 separately from timeout/5xx.
- [ ] Queue offline; replay canonical bytes after reconnect.

### Egress (cloud → device)

- [ ] Poll or push commands; wrap as authenticated_return.
- [ ] Write fragmented to `command_rx`; wait write response.
- [ ] ACK command lifecycle distinctly from incident HumanAck.
- [ ] Never send remote unmute when privacy switch is physically on.

### Ownership

- [ ] Pairing requires reviewed physical-presence proof.
- [ ] Only the ownership holder may upload live SOS for that device.
- [ ] Revocation stops live gateway use immediately.

### Fault tests (must pass before claiming BLE ready)

- [ ] MTU 23 only
- [ ] Reordered / missing / conflicting fragments
- [ ] Oversize (>2048) rejected
- [ ] CRC failure dropped
- [ ] 5s reassembly timeout
- [ ] Reconnect + replay queued SOS without duplicate incidents
- [ ] ATT ACK never flips caregiver UI to acknowledged

---

## 9. Local Lab vs product

| Surface | Use for |
| --- | --- |
| Device Simulator + Protocol inspector | Reducer phases, mock BLE fragment journey, API semantics |
| Wokwi canvas | Visual GPIO / pixels / buzzer — **no BLE radio** |
| This Pages workbench | Docs + static UI; live `/v1` needs local `make dev` |
| Real phone + board | Native BLE evidence gate |

SIM profile always labels `notification_provider=mock`. Do not treat Lab mock notifications as live dispatch.

---

## 10. Quick references

- Repo: https://github.com/Svaraa-tech/vjk-svaraa-lab-hardware-v0
- Workbench: https://svaraa-tech.github.io/vjk-svaraa-lab-hardware-v0/
- Stories: SV0-S08 (BLE gateway/ownership), SV0-08.01–08.04
- Lab ticket: WB-008 (protocol inspector)

Questions / contract freezes: keep changes in `contracts/*` with reviewed revision — do not invent UUIDs or fragment layouts in app code.
