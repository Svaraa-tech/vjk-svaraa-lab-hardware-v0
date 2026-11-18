import { useCallback, useEffect, useRef, useState } from "react";
import { MessagePortTransport } from "../wokwi/messagePortTransport";
import { WokwiClient } from "../wokwi/wokwiClient";

type SimState = "idle" | "connecting" | "ready" | "uploading" | "running" | "paused" | "error";

const PHASES = [
  "Ready",
  "Prealert",
  "Pending",
  "ServerAccepted",
  "HumanAck",
  "Resolved",
] as const;

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

export function WokwiLiveEmbed() {
  const clientRef = useRef<WokwiClient | null>(null);
  const serialEndRef = useRef<HTMLDivElement | null>(null);
  const [state, setState] = useState<SimState>("connecting");
  const [error, setError] = useState<string | null>(null);
  const [serial, setSerial] = useState("");
  const [busy, setBusy] = useState(false);
  const [holding, setHolding] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const holdTimer = useRef<number | null>(null);

  const appendSerial = useCallback((chunk: string) => {
    setSerial((prev) => (prev + chunk).slice(-20_000));
  }, []);

  useEffect(() => {
    function onMessage(event: MessageEvent) {
      if (!event.data?.port) return;
      if (clientRef.current) return;

      const client = new WokwiClient(new MessagePortTransport(event.data.port));
      clientRef.current = client;

      client.addEventListener("wokwi:connected", () => {
        setState("ready");
        setError(null);
        void client.serialMonitorListen().catch(() => undefined);
      });

      client.addEventListener("serial-monitor:data", (ev) => {
        const detail = (ev as CustomEvent).detail as { bytes?: number[] };
        if (!detail?.bytes) return;
        appendSerial(new TextDecoder().decode(new Uint8Array(detail.bytes)));
      });

      client.addEventListener("sim:pause", () => setState("paused"));
      client.addEventListener("sim:resume", () => setState("running"));
    }

    window.addEventListener("message", onMessage);
    return () => {
      window.removeEventListener("message", onMessage);
      if (holdTimer.current) window.clearTimeout(holdTimer.current);
    };
  }, [appendSerial]);

  useEffect(() => {
    if (autoScroll) {
      serialEndRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [serial, autoScroll]);

  async function uploadAndStart() {
    const client = clientRef.current;
    if (!client) {
      setError("Wokwi iframe not connected yet — wait a second and retry");
      return;
    }
    setBusy(true);
    setState("uploading");
    setError(null);
    setSerial("");
    try {
      const [diagram, bin, elf] = await Promise.all([
        fetchText(assetUrl("diagram.json")),
        fetchBytes(assetUrl("firmware.bin")),
        fetchBytes(assetUrl("firmware.elf")),
      ]);
      await client.fileUpload("diagram.json", diagram);
      await client.fileUpload("firmware.bin", bin);
      await client.fileUpload("firmware.elf", elf);
      await client.serialMonitorListen();
      await client.simStart({ firmware: "firmware.bin", elf: "firmware.elf" });
      setState("running");
      appendSerial("\n[lab] simulation started · SOS authority remains product/Lab engine\n");
    } catch (e) {
      setState("error");
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

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
    const bytes = new TextEncoder().encode(line.endsWith("\n") ? line : `${line}\n`);
    await client.serialMonitorWrite(bytes);
  }

  async function injectPhase(phase: string) {
    setBusy(true);
    try {
      await writeSerialLine(JSON.stringify({ cmd: "phase", phase }));
      appendSerial(`[lab] injected phase ${phase}\n`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  /**
   * Drive the SOS visual path the way product FW does over serial bridge:
   * Prealert → wait ≥2s → Pending (all-red + alarm). Canvas S1 remains the
   * physical click path; experimental embed may not expose gpio:write.
   */
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
        // Best-effort physical press; ignore if embed lacks gpio:write.
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
        /* gpio:list optional */
      }

      appendSerial("[lab] SOS sequence: Prealert\n");
      await writeSerialLine(JSON.stringify({ cmd: "phase", phase: "Prealert" }));
      await new Promise((r) => {
        holdTimer.current = window.setTimeout(r, 2100);
      });
      appendSerial("[lab] SOS sequence: Pending (all lights red + buzzer)\n");
      await writeSerialLine(JSON.stringify({ cmd: "phase", phase: "Pending" }));

      try {
        await client.gpioWrite("esp:5", true);
      } catch {
        /* release optional */
      }
      appendSerial("[lab] SOS hold complete — check pixels/buzzer on canvas\n");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setHolding(false);
      setBusy(false);
    }
  }

  const canControl = state === "running" || state === "paused" || state === "ready";

  return (
    <div className="wokwi-live">
      <header className="sim-header">
        <div>
          <h2>Wokwi live simulator</h2>
          <p className="muted small">
            Embedded Wokwi canvas (experimental API) · pendant face firmware from{" "}
            <code>simulation/wokwi</code> · no BLE / I2S / Nicla target · Lab engine
            remains SOS authority for product claims
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

      {error && <div className="banner-error">{error}</div>}

      <div className="move-row wokwi-live-toolbar">
        <button
          type="button"
          className="btn-primary"
          disabled={busy || (state !== "ready" && state !== "error" && state !== "paused" && state !== "running")}
          onClick={() => void uploadAndStart()}
        >
          {state === "running" || state === "paused" ? "Reload + start" : "Start simulator"}
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

      <div className="wokwi-live-grid">
        <div className="wokwi-live-frame-wrap">
          <iframe
            id="wokwi-embed"
            className="wokwi-live-iframe"
            title="Wokwi live simulator"
            src="https://wokwi.com/experimental/embed"
            allow="accelerometer; camera; encrypted-media; geolocation; gyroscope; microphone; midi; clipboard-read; clipboard-write; serial; usb"
            referrerPolicy="strict-origin-when-cross-origin"
          />
          <p className="muted small">
            Click parts inside the canvas (SOS button, privacy switch). Or use{" "}
            <strong>Test SOS hold</strong> / phase inject above. Experimental embed —
            not a substitute for VS Code Wokwi license workflows.
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
            {serial || (canControl ? "Waiting for serial…" : "Connecting to Wokwi embed…")}
            <div ref={serialEndRef} />
          </pre>
        </div>
      </div>
    </div>
  );
}
