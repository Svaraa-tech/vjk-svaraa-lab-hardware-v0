import { useMemo, useState } from "react";
import {
  HARDWARE_CATEGORIES,
  HARDWARE_PARTS,
  STATUS_LABEL,
  type HardwarePart,
  type PartStatus,
} from "../data/hardwareParts";
import { CatalogPdfButton } from "./CatalogPdfButton";

const STATUS_FILTERS: Array<PartStatus | "all"> = [
  "all",
  "product",
  "sim_standin",
  "not_in_wokwi",
  "later",
];

function statusClass(status: PartStatus) {
  switch (status) {
    case "sim_standin":
      return "hw-status hw-status-sim";
    case "not_in_wokwi":
      return "hw-status hw-status-mock";
    case "later":
      return "hw-status hw-status-later";
    default:
      return "hw-status hw-status-product";
  }
}

function partImageSrc(id: string) {
  const base = import.meta.env.BASE_URL || "/";
  return `${base}hardware/${id.toLowerCase()}.jpg`;
}

function PartCard({ part }: { part: HardwarePart }) {
  const [imgOk, setImgOk] = useState(true);
  return (
    <article className="hw-card" id={part.id}>
      <div className="hw-card-media">
        {imgOk ? (
          <img
            className="hw-card-img"
            src={partImageSrc(part.id)}
            alt={part.name}
            loading="lazy"
            decoding="async"
            onError={() => setImgOk(false)}
          />
        ) : (
          <div className="hw-card-img-fallback" aria-hidden>
            {part.id}
          </div>
        )}
      </div>
      <header className="hw-card-head">
        <div>
          <p className="hw-id mono">{part.id}</p>
          <h3 className="hw-name">{part.name}</h3>
          <p className="hw-role">{part.role}</p>
        </div>
        <span className={statusClass(part.status)}>
          {STATUS_LABEL[part.status]}
        </span>
      </header>
      <p className="hw-does">{part.does}</p>
      <dl className="hw-meta">
        {part.interface ? (
          <>
            <dt>Interface</dt>
            <dd>{part.interface}</dd>
          </>
        ) : null}
        {part.domain ? (
          <>
            <dt>Domain</dt>
            <dd>{part.domain}</dd>
          </>
        ) : null}
        {part.wokwi ? (
          <>
            <dt>Wokwi / SIM</dt>
            <dd>{part.wokwi}</dd>
          </>
        ) : null}
      </dl>
    </article>
  );
}

export function HardwareParts() {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState<PartStatus | "all">("all");
  const [category, setCategory] = useState<string>("all");

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return HARDWARE_PARTS.filter((p) => {
      if (status !== "all" && p.status !== status) return false;
      if (category !== "all" && p.category !== category) return false;
      if (!needle) return true;
      const hay = [
        p.id,
        p.name,
        p.role,
        p.does,
        p.interface,
        p.domain,
        p.wokwi,
        p.category,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return hay.includes(needle);
    });
  }, [q, status, category]);

  const byCategory = useMemo(() => {
    const map = new Map<string, HardwarePart[]>();
    for (const c of HARDWARE_CATEGORIES) map.set(c, []);
    for (const p of filtered) {
      map.get(p.category)?.push(p);
    }
    return HARDWARE_CATEGORIES.map((c) => ({
      category: c,
      parts: map.get(c) ?? [],
    })).filter((g) => g.parts.length > 0);
  }, [filtered]);

  const counts = useMemo(() => {
    const c: Record<string, number> = { all: HARDWARE_PARTS.length };
    for (const p of HARDWARE_PARTS) {
      c[p.status] = (c[p.status] ?? 0) + 1;
    }
    return c;
  }, []);

  return (
    <div className="hw">
      <header className="integ-hero">
        <p className="integ-kicker">PCB · sensors · bench BOM</p>
        <h2 className="integ-title">Hardware parts</h2>
        <p className="integ-lead">
          Everything considered for Svaraa V0 solder-free bring-up: controllers,
          sensors, audio, pendant UI, power domains, and interconnect — with what
          each part does. Sourced from the engineer BOM / pinmap; Wokwi status is
          called out honestly.
        </p>
        <div className="integ-actions">
          <CatalogPdfButton />
        </div>
      </header>

      <p className="integ-callout" role="note">
        Positives stay segregated (Nano USB / Nicla USB / EXT 5 V). Grounds are
        common. Lab/Wokwi never claims BLE, I2S, Nicla target, GNSS, or AHCT125
        are fully simulated. Product photos are vendor catalog stills (see{" "}
        <span className="mono">public/hardware/ATTRIBUTION.json</span>).
      </p>

      <div className="hw-toolbar board-filters">
        <input
          type="search"
          placeholder="Search parts, roles, buses…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          aria-label="Search hardware parts"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          aria-label="Category"
        >
          <option value="all">All categories</option>
          {HARDWARE_CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value as PartStatus | "all")}
          aria-label="SIM status"
        >
          {STATUS_FILTERS.map((s) => (
            <option key={s} value={s}>
              {s === "all"
                ? `All statuses (${counts.all})`
                : `${STATUS_LABEL[s]} (${counts[s] ?? 0})`}
            </option>
          ))}
        </select>
        <span className="muted small">
          Showing {filtered.length}/{HARDWARE_PARTS.length}
        </span>
      </div>

      <nav className="hw-toc" aria-label="Jump to category">
        {byCategory.map((g) => (
          <a key={g.category} href={`#hw-${g.category.replace(/\s+/g, "-")}`}>
            {g.category} · {g.parts.length}
          </a>
        ))}
      </nav>

      {byCategory.map((g) => (
        <section
          key={g.category}
          className="hw-section"
          id={`hw-${g.category.replace(/\s+/g, "-")}`}
        >
          <h3 className="hw-section-title">{g.category}</h3>
          <div className="hw-grid">
            {g.parts.map((p) => (
              <PartCard key={p.id} part={p} />
            ))}
          </div>
        </section>
      ))}

      {!filtered.length ? (
        <p className="muted">No parts match those filters.</p>
      ) : null}
    </div>
  );
}
