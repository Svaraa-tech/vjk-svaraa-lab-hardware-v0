export type Ticket = {
  ticket_key: string;
  source_id?: string | null;
  work_type: string;
  summary: string;
  description?: string | null;
  parent_key?: string | null;
  priority?: string | null;
  labels?: string | null;
  workflow_state: string;
  implementation_state?: string | null;
  owner_acceptance?: string | null;
  plan_revision?: string | null;
  profile_default?: string | null;
  source_namespace: string;
  plan_dependencies?: string | null;
  blocked_reason?: string | null;
  updated_at?: string;
  decisions?: Decision[];
  children?: Ticket[];
};

export type Decision = {
  id: number;
  ticket_key?: string | null;
  decision: string;
  plan_revision?: string | null;
  evidence_revision?: string | null;
  actor: string;
  message?: string | null;
  created_at: string;
};

export type BoardSummary = {
  columns: string[];
  counts_by_state: Record<string, number>;
  counts_by_namespace: Record<string, number>;
  total: number;
  done: number;
  profile: string;
  simulated: boolean;
};

export type TicketDossier = {
  ticket_key: string;
  ticket: Ticket;
  sections: {
    task: string;
    plan: string | null;
    execution: string;
    results: string;
    tests: string | null;
    review: string | null;
  };
  docs_present: Record<string, boolean>;
  completeness: {
    has_ticket_md: boolean;
    has_plan_md: boolean;
    has_implementation_md: boolean;
    has_tests_md: boolean;
    has_review_md: boolean;
    evidence_file_count: number;
    has_firmware_evidence?: boolean;
    firmware_pin_count?: number;
  };
  evidence: {
    path: string;
    name: string;
    bytes: number;
    kind?: string;
    sha256?: string;
    sha12?: string;
    pinned?: boolean;
  }[];
  firmware_pins?: {
    path: string;
    name: string;
    bytes: number;
    sha256?: string;
    sha12?: string;
  }[];
  docs_dir: string | null;
  profile: string;
  simulated: boolean;
};

function publicAsset(path: string) {
  const base = import.meta.env.BASE_URL || "/";
  const normalized = base.endsWith("/") ? base : `${base}/`;
  return `${normalized}${path.replace(/^\//, "")}`;
}

function formatHttpError(status: number, text: string) {
  const t = text.trim();
  if (t.startsWith("<!DOCTYPE") || t.startsWith("<html") || t.includes("GitHub Pages")) {
    return `${status}: Lab API unavailable on this host (static Pages). Wokwi Live works here; board/sim APIs need local \`make dev\`.`;
  }
  return `${status}: ${t.slice(0, 280)}`;
}

async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(formatHttpError(r.status, text));
  }
  const ct = r.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    const text = await r.text();
    throw new Error(formatHttpError(r.status || 502, text));
  }
  return r.json() as Promise<T>;
}

type StaticBoardSnapshot = {
  schema_version?: string;
  mode?: string;
  note?: string;
  summary: BoardSummary;
  tickets: Ticket[];
};

let labApiAvailable: boolean | null = null;
let staticBoardCache: StaticBoardSnapshot | null = null;

/** True when local Lab API answers JSON (Vite proxy / make dev). False on GitHub Pages. */
export async function probeLabApi(): Promise<boolean> {
  if (labApiAvailable != null) return labApiAvailable;
  try {
    const r = await fetch("/lab/v1/health", {
      method: "GET",
      headers: { Accept: "application/json" },
    });
    const ct = r.headers.get("content-type") || "";
    labApiAvailable = r.ok && ct.includes("application/json");
  } catch {
    labApiAvailable = false;
  }
  return labApiAvailable;
}

export async function loadStaticBoard(): Promise<StaticBoardSnapshot> {
  if (staticBoardCache) return staticBoardCache;
  const r = await fetch(publicAsset("data/board.json"));
  if (!r.ok) {
    throw new Error(
      "Static board snapshot missing — rebuild workbench or run scripts/export_board_snapshot.py",
    );
  }
  staticBoardCache = (await r.json()) as StaticBoardSnapshot;
  return staticBoardCache;
}

export const api = {
  health: async () => {
    if (await probeLabApi()) {
      return json<{ status: string; profile?: string }>("/lab/v1/health");
    }
    return {
      status: "static",
      profile: "SIM",
      note: "GitHub Pages / no Lab API — using bundled snapshots",
    };
  },
  summary: async () => {
    if (await probeLabApi()) return json<BoardSummary>("/lab/v1/board/summary");
    return (await loadStaticBoard()).summary;
  },
  tickets: async (params?: Record<string, string>) => {
    if (await probeLabApi()) {
      const q = new URLSearchParams(params).toString();
      return json<{ count: number; tickets: Ticket[] }>(
        `/lab/v1/tickets${q ? `?${q}` : ""}`,
      );
    }
    const snap = await loadStaticBoard();
    let tickets = snap.tickets;
    if (params?.namespace) {
      tickets = tickets.filter((t) => t.source_namespace === params.namespace);
    }
    if (params?.work_type) {
      tickets = tickets.filter((t) => t.work_type === params.work_type);
    }
    if (params?.state) {
      tickets = tickets.filter((t) => t.workflow_state === params.state);
    }
    if (params?.q) {
      const q = params.q.toLowerCase();
      tickets = tickets.filter(
        (t) =>
          t.ticket_key.toLowerCase().includes(q) ||
          t.summary.toLowerCase().includes(q) ||
          (t.labels ?? "").toLowerCase().includes(q),
      );
    }
    return { count: tickets.length, tickets };
  },
  ticket: async (key: string) => {
    if (await probeLabApi()) {
      return json<Ticket>(`/lab/v1/tickets/${encodeURIComponent(key)}`);
    }
    const snap = await loadStaticBoard();
    const t = snap.tickets.find((x) => x.ticket_key === key);
    if (!t) throw new Error(`ticket ${key} not found in static snapshot`);
    return t;
  },
  dossier: async (key: string) => {
    if (await probeLabApi()) {
      return json<TicketDossier>(
        `/lab/v1/tickets/${encodeURIComponent(key)}/dossier`,
      );
    }
    const t = await api.ticket(key);
    return {
      ticket_key: key,
      ticket: t,
      sections: {
        task: t.description || t.summary || "_No description in static snapshot._",
        plan: null,
        execution:
          "_Static Pages snapshot — open with local `make dev` for full dossier markdown._",
        results: `workflow_state=${t.workflow_state} · implementation=${t.implementation_state ?? "—"}`,
        tests: null,
        review: null,
      },
      docs_present: {},
      completeness: {
        has_ticket_md: false,
        has_plan_md: false,
        has_implementation_md: false,
        has_tests_md: false,
        has_review_md: false,
        evidence_file_count: 0,
      },
      evidence: [],
      firmware_pins: [],
      docs_dir: null,
      profile: "SIM",
      simulated: true,
    } satisfies TicketDossier;
  },
  transition: async (key: string, to_state: string, message?: string) => {
    if (!(await probeLabApi())) {
      throw new Error(
        "Board transitions require local Lab API (`make dev`). Pages board is read-only.",
      );
    }
    return json<Ticket>(`/lab/v1/tickets/${encodeURIComponent(key)}/transition`, {
      method: "POST",
      body: JSON.stringify({ to_state, actor: "owner", message, force: true }),
    });
  },
  decide: (body: {
    ticket_key?: string;
    decision: string;
    actor?: string;
    message?: string;
    plan_revision?: string;
    evidence_revision?: string;
  }) =>
    json<{ id: number; created_at: string }>("/lab/v1/decisions", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  reimport: (force = false) =>
    json<{ imported: boolean; ticket_count: number }>(
      `/lab/v1/board/import?force=${force ? "true" : "false"}`,
      { method: "POST" },
    ),
  gallery: () =>
    json<{ count: number; items: GalleryItem[] }>("/lab/v1/gallery"),
  sim: {
    create: (scenario_id = "manual_no_gps", seed?: string) =>
      json<SimSnapshot>("/lab/v1/sim/runs", {
        method: "POST",
        body: JSON.stringify({ scenario_id, seed }),
      }),
    get: (runId: string) =>
      json<SimSnapshot>(`/lab/v1/sim/runs/${encodeURIComponent(runId)}`),
    hold: (runId: string, body: { down?: boolean; qualify?: boolean }) =>
      json<SimSnapshot>(`/lab/v1/sim/runs/${encodeURIComponent(runId)}/hold`, {
        method: "POST",
        body: JSON.stringify(body),
      }),
    commit: (runId: string) =>
      json<{ accepted: boolean; event: DeviceEvent; snapshot: SimSnapshot }>(
        `/lab/v1/sim/runs/${encodeURIComponent(runId)}/commit`,
        { method: "POST" },
      ),
    ack: (runId: string, incident_id?: string) =>
      json<SimSnapshot>(`/lab/v1/sim/runs/${encodeURIComponent(runId)}/ack`, {
        method: "POST",
        body: JSON.stringify({ incident_id }),
      }),
    runManualNoGps: (runId: string) =>
      json<{
        expect_ok: boolean;
        snapshot: SimSnapshot;
        event: DeviceEvent;
        trace: TraceEvent[];
      }>(`/lab/v1/sim/runs/${encodeURIComponent(runId)}/scenario/manual_no_gps`, {
        method: "POST",
      }),
    drillE2e: (runId: string) =>
      json<{
        ok: boolean;
        expect_ok?: boolean;
        snapshot: SimSnapshot;
        phases_seen?: string[];
        trace_count?: number;
        wokwi?: { synced: boolean };
      }>(`/lab/v1/sim/runs/${encodeURIComponent(runId)}/drill/e2e`, {
        method: "POST",
      }),
    stress: (runId: string) =>
      json<{
        ok: boolean;
        steps: { id: string; ok: boolean; detail?: unknown }[];
        snapshot: SimSnapshot;
      }>(`/lab/v1/sim/runs/${encodeURIComponent(runId)}/stress`, {
        method: "POST",
      }),
    trace: (runId: string) =>
      json<{ run_id: string; events: TraceEvent[]; read_only: boolean }>(
        `/lab/v1/sim/runs/${encodeURIComponent(runId)}/trace`,
      ),
    fault: (runId: string, name: string, enabled: boolean) =>
      json<SimSnapshot>(`/lab/v1/sim/runs/${encodeURIComponent(runId)}/faults`, {
        method: "POST",
        body: JSON.stringify({ name, enabled }),
      }),
    tracePackUrl: (runId?: string) => {
      const q = runId ? `?run_id=${encodeURIComponent(runId)}` : "";
      return `/lab/v1/evidence/trace-pack${q}`;
    },
    privacy: (
      runId: string,
      body: { physical?: boolean; remote_mute?: boolean },
    ) =>
      json<SimSnapshot>(
        `/lab/v1/sim/runs/${encodeURIComponent(runId)}/privacy`,
        { method: "POST", body: JSON.stringify(body) },
      ),
  },
  product: {
    ingest: (event: DeviceEvent) =>
      json<Record<string, unknown>>("/v1/device-events", {
        method: "POST",
        body: JSON.stringify(event),
      }),
    ack: (incidentId: string) =>
      json<Record<string, unknown>>(
        `/v1/incidents/${encodeURIComponent(incidentId)}/ack`,
        {
          method: "POST",
          body: JSON.stringify({ actor: "guardian", revision: 2 }),
        },
      ),
  },
  hardware: {
    pinmap: () => json<Record<string, unknown>>("/lab/v1/hardware/pinmap"),
    bench: (runId?: string) => {
      const q = runId ? `?run_id=${encodeURIComponent(runId)}` : "";
      return json<HardwareBench>(`/lab/v1/hardware/bench${q}`);
    },
    sensors: (runId?: string) => {
      const q = runId ? `?run_id=${encodeURIComponent(runId)}` : "";
      return json<HardwareSensors>(`/lab/v1/hardware/sensors${q}`);
    },
  },
  protocol: {
    journey: (runId?: string) => {
      const q = runId ? `?run_id=${encodeURIComponent(runId)}` : "";
      return json<ProtocolJourney>(`/lab/v1/protocol/journey${q}`);
    },
    sample: (runId?: string) => {
      const q = runId ? `?run_id=${encodeURIComponent(runId)}` : "";
      return json<Record<string, unknown>>(`/lab/v1/protocol/sample${q}`, {
        method: "POST",
      });
    },
  },
  wokwi: {
    status: () => json<WokwiStatus>("/lab/v1/wokwi/status"),
    diagram: () =>
      json<{
        diagram: Record<string, unknown>;
        gpio_map: Record<string, unknown>;
        simulated: boolean;
      }>("/lab/v1/wokwi/diagram"),
    open: () => json<WokwiOpen>("/lab/v1/wokwi/open"),
    embed: () =>
      json<{
        config: Record<string, unknown>;
        elements_embed: WokwiOpen["elements_embed"];
      }>("/lab/v1/wokwi/embed"),
    serial: (runId?: string, limit = 80) => {
      const q = new URLSearchParams();
      if (runId) q.set("run_id", runId);
      q.set("limit", String(limit));
      return json<{
        run_id: string | null;
        phase: string;
        lines: { ts_ms?: number | null; source?: string; text: string }[];
      }>(`/lab/v1/wokwi/serial?${q}`);
    },
    serialExportUrl: (runId?: string, limit = 500) => {
      const q = new URLSearchParams();
      if (runId) q.set("run_id", runId);
      q.set("limit", String(limit));
      return `/lab/v1/wokwi/serial/export?${q}`;
    },
    phases: () =>
      json<{
        phases: string[];
        steps: {
          index: number;
          phase: string;
          pattern: string;
          annotation: string;
          pixels_on: number[];
        }[];
        count: number;
        note?: string;
      }>("/lab/v1/wokwi/phases"),
    preview: (phase: string, runId?: string) => {
      const q = new URLSearchParams({ phase });
      if (runId) q.set("run_id", runId);
      return json<{
        ok: boolean;
        preview_phase: string;
        engine_phase: string | null;
        visual: WokwiVisual;
        serial_cmd: Record<string, unknown>;
        note?: string;
      }>(`/lab/v1/wokwi/preview?${q}`, { method: "POST" });
    },
    doctor: () => json<WokwiDoctor>("/lab/v1/wokwi/doctor"),
    fidelity: () =>
      json<{ ok: boolean; mismatches: unknown[]; phases: string[] }>(
        "/lab/v1/wokwi/fidelity",
      ),
    smoke: (run_pio = false) =>
      json<{ ok: boolean; steps: unknown[]; firmware: unknown }>(
        `/lab/v1/wokwi/smoke?run_pio=${run_pio ? "true" : "false"}`,
        { method: "POST" },
      ),
    view: (runId?: string) => {
      const q = runId ? `?run_id=${encodeURIComponent(runId)}` : "";
      return json<WokwiView>(`/lab/v1/wokwi/view${q}`);
    },
    sync: (runId: string) =>
      json<{
        ok: boolean;
        visual: WokwiVisual;
        serial_cmd: Record<string, unknown>;
      }>(`/lab/v1/wokwi/sync/${encodeURIComponent(runId)}`, { method: "POST" }),
  },
  scenarios: {
    list: () =>
      json<{
        scenarios: { id: string }[];
        faults_available: string[];
      }>("/lab/v1/scenarios"),
  },
  apps: {
    previews: () =>
      json<{
        previews: {
          role: string;
          title: string;
          copy: string;
          tickets: string[];
        }[];
      }>("/lab/v1/apps/previews"),
  },
};

export type WokwiVisual = {
  phase: string;
  pattern?: string;
  button: { id: string; pressed: boolean; label: string };
  pixels: { id: string; rgb: number[]; on: boolean }[];
  serial_lines: string[];
  preview?: boolean;
  annotation?: string | null;
  limits: {
    ble: boolean;
    i2s: boolean;
    nicla_target: boolean;
    real_notification: boolean;
  };
};

export type WokwiOpen = {
  project_abs: string;
  diagram_abs: string | null;
  vscode_folder_uri: string;
  vscode_hint: string;
  elements_embed: {
    available: boolean;
    project_id?: string | null;
    iframe_src?: string | null;
    height_px?: number;
    config_path?: string;
    reason?: string | null;
    docs?: string;
    publish_hint?: string;
  };
  cli: string;
  web_panel: string;
};

export type WokwiDoctor = {
  ok: boolean;
  checks: { id: string; ok: boolean; detail: string; optional?: boolean }[];
  firmware: { present: boolean; sha256: string | null; bytes: number };
  embed?: WokwiOpen["elements_embed"];
  phases?: { count: number; phases: string[]; note?: string };
  evidence_profile: string;
};

export type WokwiStatus = {
  project_dir: string;
  diagram_present: boolean;
  firmware_built: boolean;
  firmware_path: string | null;
  firmware_sha256?: string | null;
  platformio_ini: boolean;
  wokwi_toml: boolean;
  open?: WokwiOpen;
  open_hints: Record<string, string>;
  profile: string;
  evidence_profile: string;
  note: string;
};

export type WokwiView = {
  run_id: string | null;
  status: WokwiStatus;
  diagram: Record<string, unknown>;
  gpio_map: {
    sos_button?: { wokwi_gpio: number; arduino_product: string };
    pixels?: { wokwi_gpio: number; arduino_product: string };
    unsupported_in_wokwi?: string[];
  };
  visual: WokwiVisual;
  open?: WokwiOpen;
  sync: {
    source_of_truth: string;
    wokwi_role: string;
    mirrored_fields: string[];
  };
  limits_banner?: { text: string };
  profile: string;
  simulated: boolean;
};

export type ProtocolJourney = {
  run_id: string;
  phase: string;
  packets: {
    seq: number;
    sim_ts_ms: number;
    layer: string;
    kind: string;
    detail: Record<string, unknown>;
  }[];
  rules: Record<string, unknown>;
};

export type HardwareBench = {
  phase: string;
  power_domains: { id: string; rails: string[]; rule: string; feeds: string[] }[];
  nets: {
    net: string;
    nano: string;
    domain: string;
    to: string;
    role?: string;
    active?: boolean;
  }[];
  parts: { id: string; name: string; domain?: string; bus?: string; net?: string }[];
  run_id: string | null;
  simulated: boolean;
};

export type HardwareSensors = {
  run_id: string;
  phase: string;
  sensors: {
    latest: Record<string, unknown>;
    history: Record<string, unknown>[];
  };
  pixels: {
    logical: number[];
    pattern: string;
    caption: string;
    forced_off_indices: number[];
  };
  alarm: {
    buzzer_on: boolean;
    haptic_on: boolean;
    independent_of_assistant: boolean;
  };
  simulated: boolean;
  clinical_claim: boolean;
};

export type GalleryItem = {
  id: string;
  title: string;
  kind: string;
  path: string;
  ext: string;
  bytes?: number;
  sha256?: string;
  sha12?: string;
  source?: string;
  thumb?: { label: string; subtitle: string; tone?: string };
};

export type SimSnapshot = {
  run_id: string;
  scenario_id: string;
  seed: string;
  device_id: string;
  clock: { monotonic_ms: number; paused: boolean; speed: number };
  reducer: {
    phase: string;
    mode: string;
    incident_id: string | null;
    deadline_ms: number;
    revision: number;
  };
  journal_count: number;
  outbox_count: number;
  incident_count: number;
  trace_count: number;
  pixels?: {
    logical: number[];
    pattern: string;
    caption: string;
  };
  alarm?: {
    buzzer_on: boolean;
    haptic_on: boolean;
  };
  profile: string;
  simulated: boolean;
};

export type TraceEvent = {
  seq: number;
  sim_ts_ms: number;
  layer: string;
  kind: string;
  detail: Record<string, unknown>;
};

export type DeviceEvent = {
  schema_version: string;
  event_id: string;
  device_id: string;
  boot_id: string;
  seq: number;
  mode: string;
  kind: string;
  occurred_at: string | null;
  uptime_ms: number;
  incident_id: string | null;
  drill_id: string | null;
  payload: Record<string, unknown>;
};
