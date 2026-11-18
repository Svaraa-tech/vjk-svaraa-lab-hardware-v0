import { useEffect, useState } from "react";
import { api, type ProtocolJourney } from "../api";

export function ProtocolPanel({ runId }: { runId: string | null }) {
  const [data, setData] = useState<ProtocolJourney | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    if (!runId) return;
    try {
      const j = await api.protocol.journey(runId);
      setData(j);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId]);

  return (
    <section className="sim-card sim-trace">
      <header className="sim-header" style={{ marginBottom: "0.5rem" }}>
        <h3 style={{ margin: 0 }}>Protocol inspector</h3>
        <div className="move-row">
          <button
            type="button"
            className="btn-secondary"
            disabled={!runId}
            onClick={() => void load()}
          >
            Refresh
          </button>
          <button
            type="button"
            className="btn-secondary"
            disabled={!runId}
            onClick={() =>
              void api.protocol.sample(runId!).then(() => load())
            }
          >
            Inject sample
          </button>
        </div>
      </header>
      {error && <div className="banner-error">{error}</div>}
      <p className="muted small">
        ATT ACK ≠ caregiver ACK ≠ server receipt · MTU 23 · correlated with reducer
        phase {data?.phase ?? "—"}
      </p>
      <ol className="trace-list">
        {(data?.packets ?? [])
          .slice()
          .reverse()
          .slice(0, 40)
          .map((p) => (
            <li key={p.seq}>
              <span className="mono">t={p.sim_ts_ms}</span>{" "}
              <span className="trace-layer">{p.layer}</span> {p.kind}
            </li>
          ))}
        {!data?.packets?.length && (
          <li className="muted">No protocol packets yet — run SOS or inject sample</li>
        )}
      </ol>
    </section>
  );
}
