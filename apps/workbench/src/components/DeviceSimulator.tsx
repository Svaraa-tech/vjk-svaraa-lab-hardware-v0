import { useCallback, useEffect, useState } from "react";
import {
  api,
  type HardwareBench,
  type HardwareSensors,
  type SimSnapshot,
  type TraceEvent,
} from "../api";
import { ProtocolPanel } from "./ProtocolPanel";
import { ScenariosPanel } from "./ScenariosPanel";
import { WearerPreview } from "./WearerPreview";
import { WokwiLimitsBanner } from "./WokwiLimitsBanner";
import { WokwiPanel } from "./WokwiPanel";

export function DeviceSimulator() {
  const [snap, setSnap] = useState<SimSnapshot | null>(null);
  const [trace, setTrace] = useState<TraceEvent[]>([]);
  const [bench, setBench] = useState<HardwareBench | null>(null);
  const [sensors, setSensors] = useState<HardwareSensors | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [holding, setHolding] = useState(false);

  const refresh = useCallback(
    async (runId?: string) => {
      const id = runId ?? snap?.run_id;
      if (!id) return;
      const [s, t, b, sens] = await Promise.all([
        api.sim.get(id),
        api.sim.trace(id),
        api.hardware.bench(id),
        api.hardware.sensors(id),
      ]);
      setSnap(s);
      setTrace(t.events);
      setBench(b);
      setSensors(sens);
    },
    [snap?.run_id],
  );

  async function newRun() {
    setBusy(true);
    setError(null);
    try {
      const s = await api.sim.create("manual_no_gps");
      setSnap(s);
      await refresh(s.run_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void newRun();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function runScenario() {
    if (!snap) return;
    setBusy(true);
    setError(null);
    try {
      const r = await api.sim.runManualNoGps(snap.run_id);
      setSnap(r.snapshot);
      setTrace(r.trace);
      if (r.event) {
        await api.product.ingest(r.event);
        if (r.event.incident_id) {
          await api.product.ack(r.event.incident_id);
        }
      }
      await refresh(snap.run_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onHoldStart() {
    if (!snap || busy) return;
    setHolding(true);
    try {
      await api.sim.hold(snap.run_id, { down: true });
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  async function onHoldEnd() {
    if (!snap) return;
    setHolding(false);
    setBusy(true);
    try {
      await api.sim.hold(snap.run_id, { down: true, qualify: true });
      await api.sim.commit(snap.run_id);
      await refresh(snap.run_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function ack() {
    if (!snap) return;
    setBusy(true);
    try {
      await api.sim.ack(snap.run_id);
      await refresh(snap.run_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const phase = snap?.reducer.phase ?? "—";
  const pixels = sensors?.pixels?.logical ?? snap?.pixels?.logical ?? [];
  const alarmOn = Boolean(
    sensors?.alarm?.buzzer_on || snap?.alarm?.buzzer_on,
  );

  return (
    <div className="sim-panel">
      <header className="sim-header">
        <div>
          <h2>Device Simulator</h2>
          <p className="muted small">
            SIM · mock notifications · pin/sensor panels are model/trace-driven (not
            bench-measured) · Wokwi visual subset in-panel (no BLE / I2S / Nicla
            target)
          </p>
        </div>
        <div className="move-row">
          <button
            type="button"
            className="btn-secondary"
            disabled={busy}
            onClick={() => void newRun()}
          >
            New run
          </button>
          <button
            type="button"
            className="btn-primary"
            disabled={busy || !snap}
            onClick={() => void runScenario()}
          >
            Run full SOS path
          </button>
        </div>
      </header>

      {error && <div className="banner-error">{error}</div>}
      <WokwiLimitsBanner />

      <div className="sim-grid">
        <section className="sim-card">
          <h3>Pendant</h3>
          <p className="muted small">Hold ≥ 2s (virtual) for qualified SOS.</p>
          <button
            type="button"
            className={`sos-btn ${holding ? "sos-btn-active" : ""}`}
            disabled={busy || !snap}
            onMouseDown={() => void onHoldStart()}
            onMouseUp={() => void onHoldEnd()}
            onMouseLeave={() => holding && void onHoldEnd()}
          >
            SOS
          </button>
          <div className="pixel-row" aria-label="Five logical pixels">
            {([0, 1, 2, 3, 4] as const).map((i) => (
              <span
                key={i}
                className={`pixel ${pixels[i] ? (alarmOn ? "pixel-on-alarm" : "pixel-on") : ""}`}
                title={`pixel ${i}${alarmOn ? " · SOS red" : ""}`}
              />
            ))}
          </div>
          <p className="muted small">
            Pattern: {sensors?.pixels?.pattern ?? snap?.pixels?.pattern ?? "—"} ·
            buzzer {alarmOn ? "on" : "off"} ·
            haptic {sensors?.alarm?.haptic_on || snap?.alarm?.haptic_on ? "on" : "off"}
          </p>
          <button
            type="button"
            className="btn-secondary"
            disabled={busy || !snap || phase === "Ready"}
            onClick={() => void ack()}
          >
            Guardian ACK (mock)
          </button>
        </section>

        <section className="sim-card">
          <h3>Reducer state</h3>
          {snap ? (
            <dl className="drawer-dl">
              <dt>Phase</dt>
              <dd>
                <strong>{snap.reducer.phase}</strong>
              </dd>
              <dt>Mode</dt>
              <dd>{snap.reducer.mode}</dd>
              <dt>Incident</dt>
              <dd className="mono">{snap.reducer.incident_id ?? "—"}</dd>
              <dt>Revision</dt>
              <dd>{snap.reducer.revision}</dd>
              <dt>Journal</dt>
              <dd>{snap.journal_count}</dd>
              <dt>Run</dt>
              <dd className="mono">{snap.run_id.slice(0, 8)}…</dd>
            </dl>
          ) : (
            <p className="muted">Starting run…</p>
          )}
        </section>

        <section className="sim-card">
          <h3>Sensors (synthetic)</h3>
          {sensors ? (
            <dl className="drawer-dl">
              <dt>BMP390</dt>
              <dd>
                {(sensors.sensors.latest as { bmp390?: { pressure_hpa?: number } })?.bmp390
                  ?.pressure_hpa ?? "—"}{" "}
                hPa
              </dd>
              <dt>GNSS</dt>
              <dd>null / invalid (honest)</dd>
              <dt>BMI270</dt>
              <dd className="mono">
                {JSON.stringify(
                  (sensors.sensors.latest as { bmi270?: { accel_mg?: number[] } })?.bmi270
                    ?.accel_mg ?? [],
                )}
              </dd>
              <dt>Claim</dt>
              <dd>clinical_claim=false</dd>
            </dl>
          ) : (
            <p className="muted">No sensor sample yet</p>
          )}
        </section>

        <section className="sim-card sim-trace">
          <h3>Hardware bench — nets</h3>
          {bench ? (
            <div className="bench-nets">
              {bench.nets.map((n) => (
                <div
                  key={n.net}
                  className={`net-row ${n.active ? "net-active" : ""}`}
                >
                  <code>{n.nano}</code> <strong>{n.net}</strong>
                  <span className="muted small"> {n.to}</span>
                </div>
              ))}
              <p className="muted small">
                Power domains: {bench.power_domains.map((d) => d.id).join(" · ")} — USB
                positives never joined
              </p>
            </div>
          ) : (
            <p className="muted">Bench model loading…</p>
          )}
        </section>

        <section className="sim-card sim-trace">
          <h3>Trace (read-only)</h3>
          <ol className="trace-list">
            {trace
              .slice()
              .reverse()
              .slice(0, 30)
              .map((t) => (
                <li key={t.seq}>
                  <span className="mono">t={t.sim_ts_ms}</span>{" "}
                  <span className="trace-layer">{t.layer}</span> {t.kind}
                </li>
              ))}
            {!trace.length && <li className="muted">No events yet</li>}
          </ol>
        </section>

        <WokwiPanel
          runId={snap?.run_id ?? null}
          phase={phase}
          onHoldStart={() => void onHoldStart()}
          onHoldEnd={() => void onHoldEnd()}
        />

        <ProtocolPanel runId={snap?.run_id ?? null} />
        <WearerPreview runId={snap?.run_id ?? null} />
        <ScenariosPanel
          runId={snap?.run_id ?? null}
          onChanged={() => void refresh()}
        />

        <section className="sim-card">
          <h3>Privacy (SIM)</h3>
          <p className="muted small">Physical switch dominates remote unmute</p>
          <div className="move-row">
            <button
              type="button"
              className="btn-secondary"
              disabled={!snap || busy}
              onClick={() =>
                void api.sim
                  .privacy(snap!.run_id, { physical: true })
                  .then(() => refresh())
              }
            >
              Physical privacy ON
            </button>
            <button
              type="button"
              className="btn-secondary"
              disabled={!snap || busy}
              onClick={() =>
                void api.sim
                  .privacy(snap!.run_id, { physical: false })
                  .then(() => refresh())
              }
            >
              Physical OFF
            </button>
            <button
              type="button"
              className="btn-secondary"
              disabled={!snap || busy}
              onClick={() =>
                void api.sim
                  .privacy(snap!.run_id, { remote_mute: false })
                  .then(() => refresh())
              }
            >
              Remote unmute
            </button>
          </div>
        </section>

        <section className="sim-card">
          <h3>Link / location / audio</h3>
          <p className="muted small">
            Link: {(snap as { link?: { status?: string } } | null)?.link?.status ?? "—"} ·
            GPS wait in SOS: never · Audio cannot block SOS
          </p>
          <div className="move-row">
            <button
              type="button"
              className="btn-secondary"
              disabled={!snap || busy}
              onClick={() =>
                void fetch(`/lab/v1/sim/runs/${snap!.run_id}/link`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ event: "terminate" }),
                }).then(() => refresh())
              }
            >
              Simulate app terminate
            </button>
            <button
              type="button"
              className="btn-secondary"
              disabled={!snap || busy}
              onClick={() =>
                void fetch(`/lab/v1/sim/runs/${snap!.run_id}/location`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ action: "indoor" }),
                }).then(() => refresh())
              }
            >
              Indoor null GPS
            </button>
            <button
              type="button"
              className="btn-secondary"
              disabled={!snap || busy}
              onClick={() =>
                void fetch(`/lab/v1/sim/runs/${snap!.run_id}/audio`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ action: "flood" }),
                }).then(() => refresh())
              }
            >
              Flood audio queue
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}
