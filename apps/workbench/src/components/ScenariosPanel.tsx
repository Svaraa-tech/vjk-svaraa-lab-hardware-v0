import { useEffect, useState } from "react";
import { api } from "../api";

export function ScenariosPanel({
  runId,
  onChanged,
}: {
  runId: string | null;
  onChanged: () => void;
}) {
  const [scenarios, setScenarios] = useState<{ id: string }[]>([]);
  const [faults, setFaults] = useState<string[]>([]);
  const [activeFaults, setActiveFaults] = useState<Record<string, boolean>>({});
  const [previews, setPreviews] = useState<
    { role: string; title: string; copy: string; tickets: string[] }[]
  >([]);
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void api.scenarios.list().then((r) => {
      setScenarios(r.scenarios.map((s) => ({ id: s.id })));
      setFaults(r.faults_available);
    });
    void api.apps.previews().then((r) => setPreviews(r.previews));
  }, []);

  async function toggleFault(name: string, enabled: boolean) {
    if (!runId) return;
    setBusy(true);
    try {
      await api.sim.fault(runId, name, enabled);
      setActiveFaults((prev) => ({ ...prev, [name]: enabled }));
      setMsg(`${name}=${enabled}`);
      onChanged();
    } finally {
      setBusy(false);
    }
  }

  async function clearFaults() {
    if (!runId) return;
    setBusy(true);
    try {
      for (const f of faults) {
        await api.sim.fault(runId, f, false);
      }
      setActiveFaults({});
      setMsg("all faults cleared");
      onChanged();
    } finally {
      setBusy(false);
    }
  }

  async function runE2eDrill() {
    if (!runId) return;
    setBusy(true);
    try {
      const r = await api.sim.drillE2e(runId);
      setMsg(
        `e2e drill ok=${r.ok} phase=${r.snapshot.reducer.phase} phases=${(r.phases_seen || []).join("→")}`,
      );
      try {
        await api.wokwi.sync(runId);
      } catch {
        /* optional */
      }
      onChanged();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function runStress() {
    if (!runId) return;
    setBusy(true);
    try {
      const r = await api.sim.stress(runId);
      setMsg(`stress ok=${r.ok} steps=${r.steps?.length ?? 0}`);
      onChanged();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const commFaults = faults.filter((f) => f.startsWith("drop_"));

  return (
    <section className="sim-card">
      <h3>Scenarios & faults</h3>
      <p className="muted small">
        WB-010 · SIM proxies SV0-11.02–11.04 · export evidence / deterministic trace pack
      </p>
      <ul className="child-list">
        {scenarios.map((s) => (
          <li key={s.id}>
            <code>{s.id}</code>
          </li>
        ))}
      </ul>

      <h4 className="muted small">Comm fault inject (WB-035)</h4>
      <div className="move-row" style={{ marginBottom: "0.55rem" }}>
        {commFaults.map((f) => (
          <button
            key={f}
            type="button"
            className={activeFaults[f] ? "btn-primary" : "btn-secondary"}
            disabled={!runId || busy}
            onClick={() => void toggleFault(f, !activeFaults[f])}
          >
            {activeFaults[f] ? "Clear" : "Inject"} {f}
          </button>
        ))}
        <button
          type="button"
          className="btn-secondary"
          disabled={!runId || busy}
          onClick={() => void clearFaults()}
        >
          Clear all faults
        </button>
      </div>

      <h4 className="muted small">Other faults</h4>
      <div className="move-row" style={{ marginBottom: "0.55rem" }}>
        {faults
          .filter((f) => !f.startsWith("drop_"))
          .map((f) => (
            <button
              key={f}
              type="button"
              className="btn-secondary"
              disabled={!runId || busy}
              onClick={() => void toggleFault(f, true)}
            >
              Fault {f}
            </button>
          ))}
      </div>

      <div className="move-row" style={{ marginBottom: "0.75rem" }}>
        <button
          type="button"
          className="btn-primary"
          disabled={!runId || busy}
          onClick={() => void runE2eDrill()}
        >
          Run E2E drill (SIM)
        </button>
        <button
          type="button"
          className="btn-secondary"
          disabled={!runId || busy}
          onClick={() => void runStress()}
        >
          Stress / fuzz stub
        </button>
        <a
          className="btn-secondary"
          href={
            runId
              ? `/lab/v1/evidence/export?run_id=${encodeURIComponent(runId)}`
              : "/lab/v1/evidence/export"
          }
          download
        >
          Export evidence
        </a>
        <a
          className="btn-secondary"
          href={
            runId
              ? `/lab/v1/evidence/trace-pack?run_id=${encodeURIComponent(runId)}`
              : "/lab/v1/evidence/trace-pack"
          }
          download
        >
          Trace pack JSONL
        </a>
        <a
          className="btn-secondary"
          href={
            runId
              ? `/lab/v1/evidence/report.md?run_id=${encodeURIComponent(runId)}`
              : "/lab/v1/evidence/report.md"
          }
          download
        >
          Evidence report.md
        </a>
      </div>
      {msg && <p className="muted small">{msg}</p>}
      <h3>App previews</h3>
      {previews.map((p) => (
        <div key={p.role} style={{ marginBottom: "0.65rem" }}>
          <strong>{p.title}</strong>
          <p className="muted small">{p.copy}</p>
          <p className="muted small">
            Tickets: {p.tickets.map((t) => t).join(", ")}
          </p>
        </div>
      ))}
    </section>
  );
}
