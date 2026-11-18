import { useCallback, useEffect, useState } from "react";

type WearerDash = {
  ok: boolean;
  reason?: string;
  phase?: string;
  mode?: string;
  incident_id?: string | null;
  pixels?: { pattern?: string; logical?: number[] };
  alarm?: { buzzer_on?: boolean; haptic_on?: boolean };
  privacy?: { effective?: boolean; physical?: boolean };
  location?: { valid?: boolean | null; honest?: string };
  copy?: { title?: string; subtitle?: string };
  tickets?: string[];
};

export function WearerPreview({ runId }: { runId: string | null }) {
  const [data, setData] = useState<WearerDash | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const q = runId ? `?run_id=${encodeURIComponent(runId)}` : "";
      const r = await fetch(`/lab/v1/apps/wearer${q}`);
      if (!r.ok) throw new Error(`${r.status}`);
      setData((await r.json()) as WearerDash);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [runId]);

  useEffect(() => {
    void load();
  }, [load]);

  const pixels = data?.pixels?.logical ?? [];
  const alarmOn = Boolean(data?.alarm?.buzzer_on);

  return (
    <section className="sim-card wearer-preview" aria-label="Wearer dashboard wireframe">
      <header className="sim-header" style={{ marginBottom: "0.5rem" }}>
        <div>
          <h3 style={{ margin: 0 }}>{data?.copy?.title ?? "Wearer status"}</h3>
          <p className="muted small" style={{ margin: "0.25rem 0 0" }}>
            {data?.copy?.subtitle ?? "SIM wireframe (WB-039 / SV0-10.01)"}
          </p>
        </div>
        <button type="button" className="btn-secondary" onClick={() => void load()}>
          Refresh
        </button>
      </header>
      {error && <div className="banner-error">{error}</div>}
      {!data?.ok ? (
        <p className="muted">No active run — start Device Simulator run first.</p>
      ) : (
        <>
          <dl className="drawer-dl">
            <dt>Phase</dt>
            <dd>
              <strong>{data.phase}</strong> · {data.mode}
            </dd>
            <dt>Incident</dt>
            <dd className="mono">{data.incident_id ?? "—"}</dd>
            <dt>Privacy</dt>
            <dd>
              effective {data.privacy?.effective ? "on" : "off"}
              {data.privacy?.physical != null
                ? ` · physical ${data.privacy.physical ? "on" : "off"}`
                : ""}
            </dd>
            <dt>Alarm</dt>
            <dd>
              buzzer {data.alarm?.buzzer_on ? "on" : "off"} · haptic{" "}
              {data.alarm?.haptic_on ? "on" : "off"}
            </dd>
            <dt>Location</dt>
            <dd>
              valid={String(data.location?.valid)} · {data.location?.honest}
            </dd>
          </dl>
          <div className="pixel-row" aria-label="Wearer pixels">
            {([0, 1, 2, 3, 4] as const).map((i) => (
              <span
                key={i}
                className={`pixel ${pixels[i] ? (alarmOn ? "pixel-on-alarm" : "pixel-on") : ""}`}
                title={`pixel ${i}${alarmOn ? " · SOS red" : ""}`}
              />
            ))}
          </div>
          <p className="muted small">
            Pattern {data.pixels?.pattern ?? "—"} · tickets{" "}
            {(data.tickets ?? []).join(", ")}
          </p>
        </>
      )}
    </section>
  );
}
