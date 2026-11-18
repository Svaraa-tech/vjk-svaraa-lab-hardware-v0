const GATT = [
  {
    role: "Service",
    uuid: "b7e40000-6b6d-4f2d-9f42-8a645f6c1000",
    props: "Primary",
  },
  {
    role: "event_tx",
    uuid: "b7e40001-6b6d-4f2d-9f42-8a645f6c1000",
    props: "Indicate · device → phone",
  },
  {
    role: "command_rx",
    uuid: "b7e40002-6b6d-4f2d-9f42-8a645f6c1000",
    props: "Write with response · phone → device",
  },
  {
    role: "status",
    uuid: "b7e40003-6b6d-4f2d-9f42-8a645f6c1000",
    props: "Read / notify",
  },
] as const;

const HEADER = [
  ["0", "u8", "version = 1"],
  ["1", "u8", "kind (1 event · 2 authenticated_return · 3 status)"],
  ["2", "u16", "msg_id"],
  ["4", "u8", "index (0-based)"],
  ["5", "u8", "count"],
  ["6", "u16", "total_length"],
  ["8", "u16", "complete_payload CRC16 CCITT-FALSE"],
] as const;

const APIS = [
  ["POST /v1/device-events", "Ingest reassembled DeviceEvent JSON from BLE"],
  ["GET /v1/incidents/{id}", "Authoritative snapshot + revision"],
  ["POST /v1/incidents/{id}/ack", "Authorized human ACK (not ATT ACK)"],
  ["POST /v1/incidents/{id}/resolve", "Authorized resolve"],
  ["POST /v1/incidents/{id}/cancel-request", "Cancel overlay — never deletes delivered incident"],
  ["GET /v1/devices/{id}/commands", "Bounded unexpired commands (read ≠ execute)"],
  [
    "POST /v1/devices/{id}/commands/{cid}/acks",
    "received / executed / rejected / expired",
  ],
  ["POST /v1/pairing-sessions", "Ownership / physical-presence pairing"],
] as const;

const PHASES = [
  ["Ready", "Dim status", "off", "Idle"],
  ["Prealert", "Amber subset", "off", "Hold / fall prealert"],
  ["Pending", "All 5 solid red", "on", "Local SOS · awaiting durable server"],
  ["ServerAccepted", "All 5 solid red", "on", "Verified backend receipt"],
  ["HumanAck", "All green", "off", "Guardian ACK applied"],
  ["Resolved", "Blue status", "off", "Explicit disposition"],
] as const;

const CHECKLIST = [
  "Request BT permission; handle revoke mid-incident",
  "Filter by service UUID; bond after pairing-session success",
  "Remain correct at ATT_MTU 23; negotiate higher when available",
  "Enable CCCD for event_tx + status",
  "Reassemble with 5s timeout, CRC, conflict rejection",
  "Validate DeviceEvent schema before upload",
  "POST with identical-byte retries + Idempotency-Key = event_id",
  "Map 401/403/409/422 separately from timeout/5xx",
  "Queue offline; replay without creating duplicate incidents",
  "Write authenticated_return fragments to command_rx",
  "Never treat ATT ACK as caregiver ACK or server receipt",
  "Physical privacy-on overrides every remote unmute",
] as const;

const EXAMPLE_EVENT = `{
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
      "longitude": null
    }
  }
}`;

export function IntegrationGuide() {
  return (
    <div className="integ">
      <header className="integ-hero">
        <p className="integ-kicker">Software platform · BLE</p>
        <h2 className="integ-title">Bluetooth integration guide</h2>
        <p className="integ-lead">
          Wire the pendant into the product stack: GATT gateway on the phone,
          durable APIs on the platform, authenticated return back to the device.
          Contracts in <code>contracts/</code> are source of truth.
        </p>
        <div className="integ-actions">
          <a
            className="btn-primary integ-link"
            href="https://github.com/Svaraa-tech/vjk-svaraa-lab-hardware-v0/blob/main/docs/integration/BLE_SOFTWARE_PLATFORM.md"
            target="_blank"
            rel="noreferrer"
          >
            Full markdown on GitHub
          </a>
          <a
            className="btn-secondary integ-link"
            href="https://github.com/Svaraa-tech/vjk-svaraa-lab-hardware-v0/blob/main/contracts/ble_profile.yaml"
            target="_blank"
            rel="noreferrer"
          >
            ble_profile.yaml
          </a>
        </div>
      </header>

      <p className="integ-callout" role="note">
        Wokwi and this Pages UI do <strong>not</strong> emulate a phone radio.
        Use the Lab for reducer / pixels / API semantics. Native scan, connect,
        and reconnect remain a phone + board gate.
      </p>

      <section className="integ-section">
        <h3>Architecture</h3>
        <pre className="integ-pre" aria-label="Architecture diagram">{`Pendant ──BLE GATT──▶ Phone app (gateway)
                              │
                              │  HTTPS  POST /v1/device-events
                              ▼
                     Software platform
                              │
                              │  authenticated_return → command_rx
                              ▼
                           Pendant UX`}</pre>
        <ul className="integ-list">
          <li>
            <strong>Pendant</strong> qualifies SOS, journals events, fragments
            over BLE, drives local feedback.
          </li>
          <li>
            <strong>Phone</strong> reconnects, reassembles, uploads, pulls
            commands, writes authenticated returns.
          </li>
          <li>
            <strong>Platform</strong> durable commits, receipts, guardian
            actions, notification outbox.
          </li>
        </ul>
      </section>

      <section className="integ-section">
        <h3>GATT profile</h3>
        <div className="integ-table-wrap">
          <table className="integ-table">
            <thead>
              <tr>
                <th>Role</th>
                <th>UUID</th>
                <th>Properties</th>
              </tr>
            </thead>
            <tbody>
              {GATT.map((row) => (
                <tr key={row.uuid}>
                  <td>{row.role}</td>
                  <td>
                    <code>{row.uuid}</code>
                  </td>
                  <td>{row.props}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="integ-section">
        <h3>Fragment header (10 bytes, LE)</h3>
        <p className="muted small">
          Payload per fragment = ATT_MTU − 3 − 10 (MTU 23 → 10 bytes). Max
          message 2048 B · max 255 fragments · 5000 ms reassembly timeout. CRC
          is integrity, not authentication. No PCM on this channel.
        </p>
        <div className="integ-table-wrap">
          <table className="integ-table">
            <thead>
              <tr>
                <th>Off</th>
                <th>Type</th>
                <th>Field</th>
              </tr>
            </thead>
            <tbody>
              {HEADER.map(([off, type, field]) => (
                <tr key={off + field}>
                  <td className="mono">{off}</td>
                  <td className="mono">{type}</td>
                  <td>{field}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="integ-section">
        <h3>DeviceEvent after reassembly</h3>
        <p className="muted small">
          Parse UTF-8 JSON · validate{" "}
          <code>contracts/device_event.schema.json</code> ·{" "}
          <code>POST /v1/device-events</code> with Idempotency-Key = event_id.
          Retries must resend identical bytes. Device upload cannot assert
          caregiver ACK.
        </p>
        <pre className="integ-pre">{EXAMPLE_EVENT}</pre>
      </section>

      <section className="integ-section">
        <h3>Platform APIs</h3>
        <div className="integ-table-wrap">
          <table className="integ-table">
            <thead>
              <tr>
                <th>Endpoint</th>
                <th>Use</th>
              </tr>
            </thead>
            <tbody>
              {APIS.map(([ep, use]) => (
                <tr key={ep}>
                  <td>
                    <code>{ep}</code>
                  </td>
                  <td>{use}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="integ-section">
        <h3>Authenticated return</h3>
        <p>
          After durable commit / human action, fragment{" "}
          <code>kind=authenticated_return</code> onto <code>command_rx</code>.
          Envelope fields: <code>auth_version</code>, <code>key_id</code>,{" "}
          <code>audience_device_id</code>, <code>request_nonce</code>,{" "}
          <code>issued_at</code>, <code>expires_at</code>,{" "}
          <code>payload_b64</code>, <code>signature_b64</code> (Ed25519 · RFC
          8785). Server private key never on device. Physical privacy-on
          overrides every remote unmute.
        </p>
        <p className="integ-warn">
          ATT ACK ≠ caregiver ACK ≠ server receipt. Instrument all three
          separately.
        </p>
      </section>

      <section className="integ-section">
        <h3>SOS phases the app must mirror</h3>
        <p className="muted small">
          While alarm sound is on, all five face lights are solid red.
        </p>
        <div className="integ-table-wrap">
          <table className="integ-table">
            <thead>
              <tr>
                <th>Phase</th>
                <th>Pendant UX</th>
                <th>Alarm</th>
                <th>Meaning</th>
              </tr>
            </thead>
            <tbody>
              {PHASES.map(([phase, ux, alarm, meaning]) => (
                <tr key={phase}>
                  <td>
                    <code>{phase}</code>
                  </td>
                  <td>{ux}</td>
                  <td>{alarm}</td>
                  <td>{meaning}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="integ-section">
        <h3>Mobile checklist</h3>
        <ol className="integ-checklist">
          {CHECKLIST.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ol>
      </section>

      <section className="integ-section">
        <h3>Contract files</h3>
        <ul className="integ-list">
          <li>
            <code>contracts/ble_profile.yaml</code>
          </li>
          <li>
            <code>contracts/device_event.schema.json</code>
          </li>
          <li>
            <code>contracts/example_event.json</code>
          </li>
          <li>
            <code>contracts/authenticated_relay.yaml</code>
          </li>
          <li>
            <code>services/simulator/protocol.py</code> — Lab{" "}
            <code>BleAssembler</code>
          </li>
          <li>
            <code>docs/integration/BLE_SOFTWARE_PLATFORM.md</code> — full guide
          </li>
        </ul>
      </section>
    </div>
  );
}
