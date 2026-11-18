import { useCallback, useEffect, useRef, useState } from "react";
import { api, type WokwiOpen, type WokwiView, type WokwiVisual } from "../api";

type SerialLine = { ts_ms?: number | null; source?: string; text: string };

export function WokwiPanel({
  runId,
  phase,
  onHoldStart,
  onHoldEnd,
}: {
  runId: string | null;
  phase?: string;
  onHoldStart?: () => void;
  onHoldEnd?: () => void;
}) {
  const [view, setView] = useState<WokwiView | null>(null);
  const [open, setOpen] = useState<WokwiOpen | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [serialLog, setSerialLog] = useState<SerialLine[]>([]);
  const [copied, setCopied] = useState(false);
  const [paused, setPaused] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const [phases, setPhases] = useState<string[]>([]);
  const [stepIdx, setStepIdx] = useState(0);
  const [previewVisual, setPreviewVisual] = useState<WokwiVisual | null>(null);
  const [previewNote, setPreviewNote] = useState<string | null>(null);
  const [autoplay, setAutoplay] = useState(false);
  const serialEndRef = useRef<HTMLDivElement | null>(null);
  const seenRef = useRef<Set<string>>(new Set());
  const autoplayRef = useRef(false);

  const appendLines = useCallback((incoming: SerialLine[]) => {
    if (paused || !incoming.length) return;
    setSerialLog((prev) => {
      const next = [...prev];
      for (const line of incoming) {
        const key = `${line.ts_ms ?? ""}|${line.text}`;
        if (seenRef.current.has(key)) continue;
        seenRef.current.add(key);
        next.push(line);
      }
      return next.slice(-120);
    });
  }, [paused]);

  const load = useCallback(async () => {
    try {
      const [v, o, ser, cat] = await Promise.all([
        api.wokwi.view(runId ?? undefined),
        api.wokwi.open(),
        api.wokwi.serial(runId ?? undefined),
        api.wokwi.phases(),
      ]);
      setView(v);
      setOpen(o);
      setPhases(cat.phases);
      const enginePhase = v.visual?.phase ?? phase ?? "Ready";
      const idx = cat.phases.indexOf(enginePhase);
      if (idx >= 0 && !previewVisual) setStepIdx(idx);
      appendLines(ser.lines ?? []);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [runId, appendLines, phase, previewVisual]);

  useEffect(() => {
    void load();
  }, [load, phase]);

  useEffect(() => {
    if (!runId) return;
    const id = window.setInterval(() => {
      if (paused) return;
      void api.wokwi
        .serial(runId)
        .then((ser) => appendLines(ser.lines ?? []))
        .catch(() => undefined);
    }, 1500);
    return () => window.clearInterval(id);
  }, [runId, paused, appendLines]);

  useEffect(() => {
    if (autoScroll && !paused) {
      serialEndRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [serialLog, autoScroll, paused]);

  async function sync() {
    if (!runId) return;
    setBusy(true);
    try {
      await api.wokwi.sync(runId);
      setPreviewVisual(null);
      setPreviewNote(null);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function previewAt(index: number) {
    if (!phases.length) return;
    const wrapped = ((index % phases.length) + phases.length) % phases.length;
    const target = phases[wrapped];
    setBusy(true);
    try {
      const r = await api.wokwi.preview(target, runId ?? undefined);
      setStepIdx(wrapped);
      setPreviewVisual(r.visual);
      setPreviewNote(r.note ?? null);
      appendLines([
        {
          ts_ms: Date.now() % 1_000_000,
          source: "preview",
          text: JSON.stringify(r.serial_cmd),
        },
      ]);
      setError(null);
      return wrapped;
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      return stepIdx;
    } finally {
      setBusy(false);
    }
  }

  async function stopAutoplayAndRestore() {
    autoplayRef.current = false;
    setAutoplay(false);
    if (runId) {
      setBusy(true);
      try {
        await api.wokwi.sync(runId);
        setPreviewVisual(null);
        setPreviewNote("Autoplay stopped — restored from Lab engine");
        await load();
        appendLines([
          {
            ts_ms: Date.now() % 1_000_000,
            source: "autoplay",
            text: JSON.stringify({
              type: "autoplay_stop",
              restored_from: "lab_engine",
            }),
          },
        ]);
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setBusy(false);
      }
    } else {
      setPreviewVisual(null);
      setPreviewNote(null);
    }
  }

  useEffect(() => {
    autoplayRef.current = autoplay;
    if (!autoplay || !phases.length) return;
    let cancelled = false;
    let idx = stepIdx;
    let visited = 0;
    let inFlight = false;
    const id = window.setInterval(() => {
      if (cancelled || !autoplayRef.current || inFlight) return;
      inFlight = true;
      void (async () => {
        try {
          const next = (idx + 1) % phases.length;
          const landed = await previewAt(next);
          if (typeof landed === "number") idx = landed;
          visited += 1;
          if (visited >= phases.length) {
            await stopAutoplayAndRestore();
          }
        } finally {
          inFlight = false;
        }
      })();
    }, 1100);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoplay, phases.length]);

  async function copyPath() {
    const path = open?.project_abs ?? view?.open?.project_abs;
    if (!path) return;
    try {
      await navigator.clipboard.writeText(path);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setError("Clipboard unavailable — copy path from meta panel");
    }
  }

  function clearSerial() {
    seenRef.current.clear();
    setSerialLog([]);
  }

  const visual = previewVisual ?? view?.visual;
  const pixels = visual?.pixels ?? [];
  const pressed = visual?.button?.pressed ?? false;
  const status = view?.status;
  const gpio = view?.gpio_map;
  const links = open ?? view?.open;
  const vscodeUri = links?.vscode_folder_uri;
  const embed = links?.elements_embed;
  const previewing = Boolean(previewVisual);

  return (
    <section className="sim-card sim-trace wokwi-panel" aria-label="Wokwi visual subset">
      <header className="sim-header" style={{ marginBottom: "0.5rem" }}>
        <div>
          <h3 style={{ margin: 0 }}>Wokwi · full visual hardware harness</h3>
          <p className="muted small" style={{ margin: "0.25rem 0 0" }}>
            Open <code>simulation/wokwi</code> in VS Code → Wokwi Start Simulator for
            the live canvas (SOS, privacy, pixels, buzzer, sensors). Lab engine stays
            SOS authority · no BLE / I2S / Nicla target
          </p>
        </div>
        <div className="move-row">
          <button
            type="button"
            className="btn-secondary"
            disabled={busy}
            onClick={() => void load()}
          >
            Refresh
          </button>
          <button
            type="button"
            className="btn-primary"
            disabled={busy || !runId}
            onClick={() => void sync()}
          >
            Sync from engine
          </button>
        </div>
      </header>

      {error && <div className="banner-error">{error}</div>}

      <div className="wokwi-open-row move-row">
        {vscodeUri ? (
          <a className="btn-secondary" href={vscodeUri}>
            Open folder in VS Code
          </a>
        ) : null}
        <button type="button" className="btn-secondary" onClick={() => void copyPath()}>
          {copied ? "Path copied" : "Copy project path"}
        </button>
        <a
          className="btn-secondary"
          href="https://docs.wokwi.com/vscode/getting-started"
          target="_blank"
          rel="noreferrer"
        >
          Wokwi VS Code docs
        </a>
      </div>

      {embed?.available && embed.iframe_src ? (
        <div className="wokwi-embed-frame">
          <iframe
            title="Wokwi elements embed"
            src={embed.iframe_src}
            height={embed.height_px ?? 360}
            loading="lazy"
            referrerPolicy="no-referrer"
          />
          <p className="muted small">
            Published project {embed.project_id} — Lab engine remains SOS authority
          </p>
        </div>
      ) : (
        <p className="muted small wokwi-embed-hint">
          Elements embed: not configured. {embed?.publish_hint ?? embed?.reason}
          {" "}
          See <code>docs/wokwi/EMBED_PUBLISH.md</code> (
          <code>simulation/wokwi/embed.json</code>)
        </p>
      )}

      <div className="wokwi-stepper move-row" aria-label="Phase stepper">
        <button
          type="button"
          className="btn-secondary"
          disabled={busy || !phases.length || autoplay}
          onClick={() => void previewAt(stepIdx - 1)}
        >
          ◀ Prev
        </button>
        <div className="wokwi-stepper-meta">
          <span className="muted small">
            Phase stepper {phases.length ? `${stepIdx + 1}/${phases.length}` : "—"}
            {autoplay ? " · autoplay" : ""}
          </span>
          <strong>{visual?.phase ?? "—"}</strong>
          {visual?.annotation ? (
            <span className="muted small">{visual.annotation}</span>
          ) : null}
          {previewing ? (
            <span className="badge-warn">preview only</span>
          ) : (
            <span className="badge-ok">engine-synced</span>
          )}
        </div>
        <button
          type="button"
          className="btn-secondary"
          disabled={busy || !phases.length || autoplay}
          onClick={() => void previewAt(stepIdx + 1)}
        >
          Next ▶
        </button>
        <button
          type="button"
          className="btn-secondary"
          disabled={!phases.length || busy}
          onClick={() => {
            if (autoplay) void stopAutoplayAndRestore();
            else setAutoplay(true);
          }}
        >
          {autoplay ? "Stop + restore" : "Autoplay"}
        </button>
      </div>
      {previewNote ? <p className="muted small">{previewNote}</p> : null}

      <div className="wokwi-layout">
        <div className="wokwi-board" aria-hidden={!view}>
          <div className="wokwi-esp">
            <span className="wokwi-chip-label">ESP32-S3</span>
            <span className="muted small">DevKitC-1 · sim</span>
          </div>
          <button
            type="button"
            className={`wokwi-sos ${pressed ? "wokwi-sos-down" : ""}`}
            disabled={!onHoldStart || busy || !runId}
            title="Hold to qualify SOS (drives Lab engine + Wokwi visual)"
            onMouseDown={() => onHoldStart?.()}
            onMouseUp={() => onHoldEnd?.()}
            onMouseLeave={() => pressed && onHoldEnd?.()}
          >
            {visual?.button?.label ?? "SIM SOS"}
          </button>
          <div className="wokwi-pendant-face" aria-label="Pendant face pixel layout">
            <div className="wokwi-status-row">
              <span className="muted small">status</span>
              {(() => {
                const px = pixels[0];
                const rgb = px?.rgb ?? [0, 0, 0];
                const on = px?.on ?? false;
                return (
                  <span
                    className={`wokwi-pixel ${on ? "wokwi-pixel-on" : ""}`}
                    style={
                      on
                        ? {
                            background: `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`,
                            boxShadow: `0 0 12px rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.55)`,
                          }
                        : undefined
                    }
                    title={`px0 status rgb(${rgb.join(",")})`}
                  />
                );
              })()}
            </div>
            <div className="wokwi-pixels wokwi-pixels-arc" aria-label="Programmable NeoPixels">
              {([1, 2, 3, 4] as const).map((i) => {
                const px = pixels[i];
                const rgb = px?.rgb ?? [0, 0, 0];
                const on = px?.on ?? false;
                return (
                  <span
                    key={i}
                    className={`wokwi-pixel ${on ? "wokwi-pixel-on" : ""}`}
                    style={
                      on
                        ? {
                            background: `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`,
                            boxShadow: `0 0 12px rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.55)`,
                          }
                        : undefined
                    }
                    title={`px${i} programmable rgb(${rgb.join(",")})`}
                  />
                );
              })}
            </div>
            <p className="muted small" style={{ margin: 0 }}>
              programmable px1–px4
            </p>
          </div>
          <p className="muted small">
            Phase <strong>{visual?.phase ?? "—"}</strong>
            {visual?.pattern ? ` · ${visual.pattern}` : ""} · GPIO SOS{" "}
            {gpio?.sos_button?.wokwi_gpio ?? "—"} · pixels{" "}
            {gpio?.pixels?.wokwi_gpio ?? "—"}
          </p>
        </div>

        <div className="wokwi-meta">
          <dl className="drawer-dl">
            <dt>Project</dt>
            <dd className="mono">{status?.project_dir ?? "simulation/wokwi"}</dd>
            <dt>Firmware</dt>
            <dd>
              {status?.firmware_built ? (
                <span className="badge-ok">built</span>
              ) : (
                <span className="badge-warn">not built</span>
              )}{" "}
              <span className="mono muted small">
                {status?.firmware_sha256
                  ? status.firmware_sha256.slice(0, 12) + "…"
                  : status?.firmware_path ?? "pio run -e sim"}
              </span>
            </dd>
            <dt>Diagram</dt>
            <dd>{status?.diagram_present ? "diagram.json ✓" : "missing"}</dd>
            <dt>Sync</dt>
            <dd className="muted small">
              {view?.sync?.source_of_truth ?? "lab_engine"} →{" "}
              {view?.sync?.wokwi_role ?? "visual_subset"}
            </dd>
          </dl>

          <div className="wokwi-serial">
            <div className="wokwi-serial-toolbar move-row">
              <h4 className="muted small" style={{ margin: 0, flex: 1 }}>
                Serial console ({serialLog.length})
              </h4>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setPaused((p) => !p)}
              >
                {paused ? "Resume" : "Pause"}
              </button>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setAutoScroll((v) => !v)}
              >
                {autoScroll ? "Auto-scroll on" : "Auto-scroll off"}
              </button>
              <button type="button" className="btn-secondary" onClick={clearSerial}>
                Clear
              </button>
              <a
                className="btn-secondary"
                href={api.wokwi.serialExportUrl(runId ?? undefined)}
                download
              >
                Export JSONL
              </a>
            </div>
            <pre className="wokwi-serial-pre wokwi-serial-live">
              {serialLog.length
                ? serialLog.map((l, i) => (
                    <div key={`${l.ts_ms}-${i}`}>
                      <span className="mono muted">
                        t={l.ts_ms ?? "—"} {l.source ? `[${l.source}] ` : ""}
                      </span>
                      {l.text}
                    </div>
                  ))
                : "—"}
              <div ref={serialEndRef} />
            </pre>
          </div>
        </div>
      </div>
    </section>
  );
}
