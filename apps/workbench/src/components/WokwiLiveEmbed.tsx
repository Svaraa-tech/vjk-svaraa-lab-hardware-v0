import { useCallback, useEffect, useRef, useState } from "react";
import { MessagePortTransport } from "../wokwi/messagePortTransport";
import { WokwiClient } from "../wokwi/wokwiClient";

type SimState =
  | "connecting"
  | "ready"
  | "uploading"
  | "running"
  | "paused"
  | "error";

const PHASES = [
  "Ready",
  "Prealert",
  "Pending",
  "ServerAccepted",
  "HumanAck",
  "Resolved",
] as const;

const PHASE_RGB: Record<string, [number, number, number]> = {
  Ready: [0, 8, 3],
  Prealert: [40, 25, 0],
  Pending: [50, 0, 0],
  ServerAccepted: [50, 0, 0],
  HumanAck: [0, 40, 0],
  Resolved: [0, 0, 30],
};

const PHASE_LIT: Record<string, number> = {
  Ready: 1,
  Prealert: 2,
  Pending: 5,
  ServerAccepted: 5,
  HumanAck: 5,
  Resolved: 1,
};

function assetUrl(name: string) {
  const base = import.meta.env.BASE_URL || "/";
  const normalized = base.endsWith("/") ? base : `${base}/`;
  return `${normalized}wokwi/${name}`;
}

async function fetchText(url: string) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);
  return res.text();
}

async function fetchBytes(url: string) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);
  return new Uint8Array(await res.arrayBuffer());
}

function parsePhaseFromSerial(chunk: string, prev: string): string {
  const matches = [...chunk.matchAll(/"phase"\s*:\s*"([A-Za-z]+)"/g)];
  if (!matches.length) return prev;
  return matches[matches.length - 1][1] || prev;
}

export function WokwiLiveEmbed() {
  const clientRef = useRef<WokwiClient | null>(null);
  const serialEndRef = useRef<HTMLDivElement | null>(null);
  const startingRef = useRef(false);
  const autoStartedRef = useRef(false);
  const [state, setState] = useState<SimState>("connecting");
  const [error, setError] = useState<string | null>(null);
  const [statusLine, setStatusLine] = useState(
    "Waiting for Wokwi iframe handshake…",
  );
  const [serial, setSerial] = useState("");
  const [busy, setBusy] = useState(false);
  const [holding, setHolding] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const [phase, setPhase] = useState("Ready");
  const [iframeKey, setIframeKey] = useState(0);
  const holdTimer = useRef<number | null>(null);

  const appendSerial = useCallback((chunk: string) => {
    setSerial((prev) => (prev + chunk).slice(-20_000));
    setPhase((p) => parsePhaseFromSerial(chunk, p));
  }, []);

  const uploadAndStart = useCallback(async () => {
    const client = clientRef.current;
    if (!client) {
      setError("Wokwi iframe not connected yet — wait a second and retry");
      setState("connecting");
      return;
    }
    if (startingRef.current) return;
    startingRef.current = true;
    setBusy(true);
    setState("uploading");
    setError(null);
    setSerial("");
    setPhase("Ready");
    try {
      setStatusLine("Fetching diagram.json…");
      const diagram = await fetchText(assetUrl("diagram.json"));
      setStatusLine("Fetching firmware.bin…");
      const bin = await fetchBytes(assetUrl("firmware.bin"));
      setStatusLine(
        `Uploading diagram + firmware.bin (${Math.round(bin.byteLength / 1024)} KB)…`,
      );
      await client.fileUpload("diagram.json", diagram);
      await client.fileUpload("firmware.bin", bin);

      // ELF is large (~7MB); required for some ESP32 debug paths. Retry without if it fails.
      try {
        setStatusLine("Fetching firmware.elf (large — may take a bit)…");
        const elf = await fetchBytes(assetUrl("firmware.elf"));
        setStatusLine(
          `Uploading firmware.elf (${Math.round(elf.byteLength / 1024)} KB)…`,
        );
        await client.fileUpload("firmware.elf", elf);
        await client.serialMonitorListen();
        setStatusLine("Starting simulation…");
        await client.simStart({
          firmware: "firmware.bin",
          elf: "firmware.elf",
        });
      } catch (elfErr) {
        appendSerial(
          `\n[lab] elf upload/start failed (${elfErr instanceof Error ? elfErr.message : String(elfErr)}); retrying bin-only\n`,
        );
        await client.serialMonitorListen();
        setStatusLine("Starting simulation (firmware.bin only)…");
        await client.simStart({
          firmware: "firmware.bin",
          elf: "firmware.bin",
        });
      }

      setState("running");
      setStatusLine("Running — use canvas SOS or Test SOS hold / phase inject");
      appendSerial(
        "\n[lab] simulation started · SOS authority remains product/Lab engine\n",
      );
    } catch (e) {
      setState("error");
      setError(e instanceof Error ? e.message : String(e));
      setStatusLine("Start failed — see error banner");
    } finally {
      startingRef.current = false;
      setBusy(false);
    }
  }, [appendSerial]);

  useEffect(() => {
    function onMessage(event: MessageEvent) {
      // Wokwi posts a MessagePort when the experimental embed is ready.
      if (!event.data?.port) return;
      if (event.origin && !event.origin.includes("wokwi.com")) return;
      if (clientRef.current) return;

      const client = new WokwiClient(new MessagePortTransport(event.data.port));
      clientRef.current = client;

      client.addEventListener("wokwi:connected", () => {
        setState("ready");
        setError(null);
        setStatusLine("Connected — starting simulation…");
        void client.serialMonitorListen().catch(() => undefined);
        if (!autoStartedRef.current) {
          autoStartedRef.current = true;
          void uploadAndStart();
        }
      });

      client.addEventListener("serial-monitor:data", (ev) => {
        const detail = (ev as CustomEvent).detail as { bytes?: number[] };
        if (!detail?.bytes) return;
        appendSerial(new TextDecoder().decode(new Uint8Array(detail.bytes)));
      });

      client.addEventListener("sim:pause", () => {
        setState("paused");
        setStatusLine("Paused");
      });
      client.addEventListener("sim:resume", () => {
        setState("running");
        setStatusLine("Running");
      });
    }

    window.addEventListener("message", onMessage);
    return () => {
      window.removeEventListener("message", onMessage);
      if (holdTimer.current) window.clearTimeout(holdTimer.current);
    };
  }, [appendSerial, uploadAndStart]);

  // Handshake timeout — blank iframe with no port
  useEffect(() => {
    if (state !== "connecting") return;
    const id = window.setTimeout(() => {
      if (clientRef.current) return;
      setState("error");
      setError(
        "Wokwi embed did not connect (no MessagePort). Hard-refresh, allow third-party content for wokwi.com, or click Retry iframe.",
      );
      setStatusLine("Embed handshake timed out");
    }, 12_000);
    return () => window.clearTimeout(id);
  }, [state, iframeKey]);

  useEffect(() => {
    if (autoScroll) {
      serialEndRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    }
  }, [serial, autoScroll]);

  async function pause() {
    const client = clientRef.current;
    if (!client) return;
    setBusy(true);
    try {
      await client.simPause();
      setState("paused");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function resume() {
    const client = clientRef.current;
    if (!client) return;
    setBusy(true);
    try {
      await client.simResume();
      setState("running");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function restart() {
    const client = clientRef.current;
    if (!client) return;
    setBusy(true);
    try {
      await client.simRestart();
      setState("running");
      appendSerial("\n[lab] sim restarted\n");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function writeSerialLine(line: string) {
    const client = clientRef.current;
    if (!client) return;
    const bytes = new TextEncoder().encode(
      line.endsWith("\n") ? line : `${line}\n`,
    );
    await client.serialMonitorWrite(bytes);
  }

  async function injectPhase(target: string) {
    setBusy(true);
    try {
      await writeSerialLine(JSON.stringify({ cmd: "phase", phase: target }));
      setPhase(target);
      appendSerial(`[lab] injected phase ${target}\n`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function runQualifiedSos() {
    const client = clientRef.current;
    if (!client || holding) return;
    setHolding(true);
    setBusy(true);
    setError(null);
    try {
      try {
        const listed = await client.gpioList();
        appendSerial(
          `[lab] gpio pins available: ${listed.pins.slice(0, 16).join(", ")}\n`,
        );
        const pin =
          listed.pins.find((p) => p === "esp:5" || p === "esp:_mcu$GPIO5") ??
          listed.pins.find((p) => /GPIO5|:5$/.test(p));
        if (pin) {
          try {
            await client.gpioWrite(pin, false);
            appendSerial(`[lab] gpioWrite ${pin}=LOW (pressed)\n`);
          } catch {
            appendSerial(
              "[lab] gpio:write unsupported in this embed — using serial phases\n",
            );
          }
        }
      } catch {
        /* optional */
      }

      appendSerial("[lab] SOS sequence: Prealert\n");
      await writeSerialLine(JSON.stringify({ cmd: "phase", phase: "Prealert" }));
      setPhase("Prealert");
      await new Promise((r) => {
        holdTimer.current = window.setTimeout(r, 2100);
      });
      appendSerial("[lab] SOS sequence: Pending (all lights red + buzzer)\n");
      await writeSerialLine(JSON.stringify({ cmd: "phase", phase: "Pending" }));
      setPhase("Pending");
      try {
        await client.gpioWrite("esp:5", true);
      } catch {
        /* optional */
      }
      appendSerial("[lab] SOS hold complete — check pixels/buzzer on canvas\n");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setHolding(false);
      setBusy(false);
    }
  }

  function retryIframe() {
    clientRef.current = null;
    autoStartedRef.current = false;
    startingRef.current = false;
    setSerial("");
    setError(null);
    setPhase("Ready");
    setState("connecting");
    setStatusLine("Reloading Wokwi iframe…");
    setIframeKey((k) => k + 1);
  }

  const lit = PHASE_LIT[phase] ?? 1;
  const rgb = PHASE_RGB[phase] ?? PHASE_RGB.Ready;
  const showOverlay =
    state === "connecting" || state === "uploading" || state === "ready";

  return (
    <div className="wokwi-live">
      <header className="sim-header">
        <div>
          <h2>Wokwi live simulator</h2>
          <p className="muted small">
            Auto-starts when the embed connects · uploads pendant{" "}
            <code>diagram.json</code> + firmware · no BLE / I2S / Nicla target
          </p>
        </div>
        <span
          className={
            state === "running"
              ? "badge-ok"
              : state === "error"
                ? "badge-warn"
                : "chip"
          }
        >
          {state}
        </span>
      </header>

      <p className="integ-callout" role="status">
        {statusLine}
        {state === "connecting"
          ? " — blank canvas is normal until Start finishes."
          : null}
      </p>

      {error && <div className="banner-error">{error}</div>}

      <div className="move-row wokwi-live-toolbar">
        <button
          type="button"
          className="btn-primary"
          disabled={
            busy ||
            (state !== "ready" &&
              state !== "error" &&
              state !== "paused" &&
              state !== "running")
          }
          onClick={() => void uploadAndStart()}
        >
          {state === "running" || state === "paused"
            ? "Reload + start"
            : state === "uploading"
              ? "Starting…"
              : "Start simulator"}
        </button>
        <button
          type="button"
          className="btn-secondary"
          disabled={busy || state !== "running"}
          onClick={() => void pause()}
        >
          Pause
        </button>
        <button
          type="button"
          className="btn-secondary"
          disabled={busy || state !== "paused"}
          onClick={() => void resume()}
        >
          Resume
        </button>
        <button
          type="button"
          className="btn-secondary"
          disabled={busy || (state !== "running" && state !== "paused")}
          onClick={() => void restart()}
        >
          Restart
        </button>
        <button
          type="button"
          className="btn-primary"
          disabled={busy || state !== "running" || holding}
          onClick={() => void runQualifiedSos()}
        >
          {holding ? "Holding SOS…" : "Test SOS hold (≥2s)"}
        </button>
        <button
          type="button"
          className="btn-secondary"
          disabled={busy}
          onClick={retryIframe}
        >
          Retry iframe
        </button>
      </div>

      <div className="move-row wokwi-live-phases" aria-label="Inject phase over serial">
        <span className="muted small">Inject phase:</span>
        {PHASES.map((p) => (
          <button
            key={p}
            type="button"
            className="btn-secondary"
            disabled={busy || state !== "running"}
            onClick={() => void injectPhase(p)}
          >
            {p}
          </button>
        ))}
      </div>

      <div className="wokwi-live-preview" aria-label="Pendant face mirror">
        <span className="muted small">
          Face mirror (from serial phase) · <strong>{phase}</strong>
        </span>
        <div className="wokwi-pendant-face">
          <div className="wokwi-status-row">
            <span className="muted small">status</span>
            <span
              className={`wokwi-pixel ${lit >= 1 ? "wokwi-pixel-on" : ""}`}
              style={
                lit >= 1
                  ? {
                      background: `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`,
                      boxShadow: `0 0 12px rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.55)`,
                    }
                  : undefined
              }
            />
          </div>
          <div className="wokwi-pixels wokwi-pixels-arc">
            {([1, 2, 3, 4] as const).map((i) => (
              <span
                key={i}
                className={`wokwi-pixel ${i < lit ? "wokwi-pixel-on" : ""}`}
                style={
                  i < lit
                    ? {
                        background: `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`,
                        boxShadow: `0 0 12px rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.55)`,
                      }
                    : undefined
                }
              />
            ))}
          </div>
        </div>
      </div>

      <div className="wokwi-live-grid">
        <div className="wokwi-live-frame-wrap">
          <div className="wokwi-live-frame-shell">
            {showOverlay ? (
              <div className="wokwi-live-overlay" aria-live="polite">
                <strong>
                  {state === "uploading"
                    ? "Loading circuit into Wokwi…"
                    : state === "ready"
                      ? "Connected — starting…"
                      : "Connecting to Wokwi…"}
                </strong>
                <span>{statusLine}</span>
                <span className="muted small">
                  Visualization + serial appear after firmware upload finishes.
                </span>
              </div>
            ) : null}
            <iframe
              key={iframeKey}
              id="wokwi-embed"
              className="wokwi-live-iframe"
              title="Wokwi live simulator"
              src="https://wokwi.com/experimental/embed"
              allow="accelerometer; camera; encrypted-media; geolocation; gyroscope; microphone; midi; clipboard-read; clipboard-write; serial; usb"
              referrerPolicy="no-referrer-when-downgrade"
            />
          </div>
          <p className="muted small">
            After start: click <strong>S1 SOS</strong> on the canvas (≥2s) or use{" "}
            <strong>Test SOS hold</strong>. Alarm phases light all pixels red.
          </p>
        </div>

        <div className="wokwi-live-serial">
          <div className="wokwi-serial-toolbar move-row">
            <h3 className="muted small" style={{ margin: 0, flex: 1 }}>
              Serial monitor
            </h3>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => setAutoScroll((v) => !v)}
            >
              {autoScroll ? "Auto-scroll on" : "Auto-scroll off"}
            </button>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => setSerial("")}
            >
              Clear
            </button>
          </div>
          <pre className="wokwi-serial-pre wokwi-live-serial-pre">
            {serial ||
              (state === "running"
                ? "Waiting for serial…"
                : state === "uploading"
                  ? "Uploading firmware — serial starts after boot…"
                  : state === "connecting"
                    ? "Connecting to Wokwi embed…"
                    : "Click Start simulator if auto-start did not run.")}
            <div ref={serialEndRef} />
          </pre>
        </div>
      </div>
    </div>
  );
}
