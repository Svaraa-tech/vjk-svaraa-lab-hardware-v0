import { useMemo, useState } from "react";
import {
  ACTOR_LABEL,
  FEATURE_LIST,
  MATURITY_BADGE,
  MATURITY_LABEL,
  PILLAR_META,
  PILLAR_ORDER,
  PRIORITY_BADGE,
  PRIORITY_LABEL,
  PRIORITY_ORDER,
  compareFeaturePriority,
  featureActors,
  featureSvaraas,
  type CareActor,
  type FeatureItem,
  type FeatureMaturity,
  type FeaturePriority,
  type SvaraaPillar,
} from "../data/featureList";
import { featureMcuEquivalent } from "../data/mcuEquivalents";
import { parsePendantPcb } from "../data/pcbParts";
import { CatalogPdfButton } from "./CatalogPdfButton";

const MATURITY_FILTERS: Array<FeatureMaturity | "all"> = [
  "all",
  "v0_bench",
  "product_path",
  "needs_phone",
  "needs_cloud",
  "later_gated",
];

const PRIORITY_FILTERS: Array<FeaturePriority | "all"> = [
  "all",
  ...PRIORITY_ORDER,
];

const ACTOR_FILTERS: Array<CareActor | "all" | "m2m"> = [
  "all",
  "wearer",
  "guardian",
  "care_circle",
  "both_ends",
  "m2m",
];

function maturityClass(m: FeatureMaturity) {
  switch (m) {
    case "v0_bench":
      return "feat-mat feat-mat-bench";
    case "product_path":
      return "feat-mat feat-mat-path";
    case "needs_phone":
      return "feat-mat feat-mat-phone";
    case "needs_cloud":
      return "feat-mat feat-mat-cloud";
    default:
      return "feat-mat feat-mat-later";
  }
}

function priorityClass(p: FeaturePriority) {
  return `feat-pri feat-pri-${p.toLowerCase()}`;
}

function SvaraaBadges({ feature }: { feature: FeatureItem }) {
  const svaraas = featureSvaraas(feature);
  return (
    <ul className="feat-svaraa-row" aria-label="Associated Svaraas">
      {svaraas.map((p) => {
        const primary = p === feature.pillar;
        return (
          <li
            key={p}
            className={`feat-svaraa-badge feat-pillar-${PILLAR_META[p].color}${
              primary ? " is-primary" : " is-also"
            }`}
            title={
              primary ? `Primary Svaraa: ${p}` : `Also associated with ${p}`
            }
          >
            <span className="mono">{PILLAR_META[p].num}</span>
            <span>{p}</span>
            {primary ? <span className="feat-svaraa-prim">primary</span> : null}
          </li>
        );
      })}
    </ul>
  );
}

function ActorChips({ feature }: { feature: FeatureItem }) {
  const list = featureActors(feature);
  return (
    <ul className="feat-actor-row" aria-label="Care relationship">
      {list.map((a) => (
        <li key={a} className={`feat-actor feat-actor-${a}`}>
          {ACTOR_LABEL[a]}
        </li>
      ))}
    </ul>
  );
}

function FeatureCard({
  feature,
  onOpenHardware,
}: {
  feature: FeatureItem;
  onOpenHardware?: (partId: string) => void;
}) {
  const subs = feature.subFeatures ?? [];
  const mcuRaw =
    feature.mcuEquivalent?.trim() || featureMcuEquivalent(feature.id);
  const pcb = mcuRaw ? parsePendantPcb(mcuRaw) : null;
  return (
    <article className="feat-card" id={feature.id}>
      <div className="feat-card-top">
        <SvaraaBadges feature={feature} />
        <div className="feat-card-badges">
          <span
            className={priorityClass(feature.priority)}
            title={PRIORITY_LABEL[feature.priority]}
          >
            {PRIORITY_BADGE[feature.priority]}
          </span>
          <span
            className={maturityClass(feature.maturity)}
            title={MATURITY_LABEL[feature.maturity]}
          >
            {MATURITY_BADGE[feature.maturity]}
          </span>
        </div>
      </div>
      <header className="feat-card-head">
        <p className="feat-id mono">{feature.id}</p>
        <h3 className="feat-name">{feature.name}</h3>
      </header>
      <ActorChips feature={feature} />
      <p className="feat-summary">{feature.summary}</p>
      <dl className="feat-meta">
        <dt>Why for elders</dt>
        <dd>{feature.elderWhy}</dd>
        <dt>How</dt>
        <dd>{feature.how}</dd>
        <dt>Hardware</dt>
        <dd className="feat-hw">
          {feature.hardware.map((h) =>
            onOpenHardware ? (
              <button
                key={h}
                type="button"
                className="feat-hw-chip feat-hw-link mono"
                title={`Open ${h} in Hardware tab`}
                onClick={() => onOpenHardware(h)}
              >
                {h}
              </button>
            ) : (
              <span key={h} className="feat-hw-chip mono">
                {h}
              </span>
            ),
          )}
        </dd>
        {pcb && pcb.capsules.length ? (
          <>
            <dt>Pendant PCB</dt>
            <dd className="feat-mcu">
              <ul className="feat-mcu-capsules" aria-label="Production PCB parts">
                {pcb.capsules.map((c) => (
                  <li
                    key={`${feature.id}-${c.id}`}
                    className={`feat-mcu-capsule${
                      c.primary ? " is-primary" : ""
                    }${c.later ? " is-later" : ""}`}
                    title={c.detail}
                  >
                    <span className="feat-mcu-id mono">{c.id}</span>
                    <span className="feat-mcu-title">{c.title}</span>
                  </li>
                ))}
              </ul>
              {pcb.note ? <p className="feat-mcu-note">{pcb.note}</p> : null}
            </dd>
          </>
        ) : null}
      </dl>
      {subs.length ? (
        <div className="feat-subs">
          <p className="feat-subs-label">Sub-features</p>
          <ul>
            {subs.map((s) => (
              <li key={s.id}>
                <span className="feat-sub-id mono">{s.id}</span>
                <strong>{s.name}</strong>
                <span className="feat-sub-sum">{s.summary}</span>
                {s.actors?.length ? (
                  <span className="feat-sub-actors">
                    {s.actors.map((a) => ACTOR_LABEL[a]).join(" · ")}
                  </span>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {feature.tags?.length ? (
        <ul className="feat-tags">
          {feature.tags.map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}

export function FeatureList({
  onOpenHardware,
}: {
  onOpenHardware?: (partId: string) => void;
}) {
  const [q, setQ] = useState("");
  const [pillar, setPillar] = useState<SvaraaPillar | "all">("all");
  const [maturity, setMaturity] = useState<FeatureMaturity | "all">("all");
  const [priority, setPriority] = useState<FeaturePriority | "all">("all");
  const [actor, setActor] = useState<(typeof ACTOR_FILTERS)[number]>("all");

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return FEATURE_LIST.filter((f) => {
      const svaraas = featureSvaraas(f);
      if (pillar !== "all" && !svaraas.includes(pillar)) return false;
      if (maturity !== "all" && f.maturity !== maturity) return false;
      if (priority !== "all" && f.priority !== priority) return false;
      const acts = featureActors(f);
      if (actor === "m2m") {
        if (!(f.tags?.includes("m2m") || acts.includes("both_ends"))) {
          return false;
        }
      } else if (actor !== "all" && !acts.includes(actor)) {
        return false;
      }
      if (!needle) return true;
      const mcu = f.mcuEquivalent || featureMcuEquivalent(f.id) || "";
      const hay = [
        f.id,
        f.name,
        f.summary,
        f.elderWhy,
        f.how,
        f.priority,
        PRIORITY_LABEL[f.priority],
        mcu,
        ...svaraas,
        ...acts,
        ...(f.hardware ?? []),
        ...(f.tags ?? []),
        ...(f.subFeatures ?? []).flatMap((s) => [s.id, s.name, s.summary]),
      ]
        .join(" ")
        .toLowerCase();
      return hay.includes(needle);
    });
  }, [q, pillar, maturity, priority, actor]);

  const byPillar = useMemo(() => {
    return PILLAR_ORDER.map((p) => {
      const features = filtered
        .filter((f) => f.pillar === p)
        .slice()
        .sort(compareFeaturePriority);
      const counts = { P1: 0, P2: 0, P3: 0 };
      for (const f of features) counts[f.priority] += 1;
      return {
        pillar: p,
        meta: PILLAR_META[p],
        features,
        counts,
      };
    }).filter((g) => g.features.length > 0);
  }, [filtered]);

  const priorityCounts = useMemo(() => {
    const c: Record<string, number> = { all: FEATURE_LIST.length };
    for (const f of FEATURE_LIST) {
      c[f.priority] = (c[f.priority] ?? 0) + 1;
    }
    return c;
  }, []);

  const pillarCounts = useMemo(() => {
    const c: Record<string, number> = { all: FEATURE_LIST.length };
    for (const f of FEATURE_LIST) {
      for (const p of featureSvaraas(f)) {
        c[p] = (c[p] ?? 0) + 1;
      }
    }
    return c;
  }, []);

  const subCount = useMemo(
    () => FEATURE_LIST.reduce((n, f) => n + (f.subFeatures?.length ?? 0), 0),
    [],
  );

  return (
    <div className="feat">
      <header className="integ-hero">
        <p className="integ-kicker">
          Product ·{" "}
          <a
            className="integ-link"
            href="https://www.svaraa.ai/"
            target="_blank"
            rel="noreferrer"
          >
            svaraa.ai
          </a>{" "}
          · 7 Svaraas · M:N care graph
        </p>
        <h2 className="integ-title">Feature list</h2>
        <p className="integ-lead">
          Elder wearers and caretakers/guardians are many-to-many: one pendant
          links many guardians; one guardian cares for many elders. Every card
          shows its primary Svaraa (and any cross-links), who it serves, and
          sub-features where the relationship splits.
        </p>
        <div className="integ-actions">
          <CatalogPdfButton />
        </div>
      </header>

      <p className="integ-callout" role="note">
        {FEATURE_LIST.length} features · {subCount} sub-features · ordered{" "}
        <strong>P1 Must → P2 Need → P3 Nice</strong> within each Svaraa. P1 =
        safety, trust, and Free-tier promises elders/families cannot ship
        without; P2 = daily companion value; P3 = polish / later tiers. Filter
        by Svaraa, priority, actor, or maturity. Non-clinical: no vital-sign
        claims.
      </p>

      <div className="feat-controls">
        <div className="feat-pillars" aria-label="Seven Svaraas">
          <button
            type="button"
            className={`feat-pillar-chip${pillar === "all" ? " is-active" : ""}`}
            onClick={() => setPillar("all")}
          >
            <span className="feat-pillar-name">All</span>
            <span className="feat-pillar-count">{pillarCounts.all}</span>
          </button>
          {PILLAR_ORDER.filter((p) => p !== "Platform").map((p) => (
            <button
              key={p}
              type="button"
              className={`feat-pillar-chip feat-pillar-${PILLAR_META[p].color}${
                pillar === p ? " is-active" : ""
              }`}
              onClick={() => setPillar((cur) => (cur === p ? "all" : p))}
            >
              <span className="feat-pillar-num mono">{PILLAR_META[p].num}</span>
              <span className="feat-pillar-name">{p}</span>
              <span className="feat-pillar-count">{pillarCounts[p] ?? 0}</span>
            </button>
          ))}
          <button
            type="button"
            className={`feat-pillar-chip feat-pillar-platform${
              pillar === "Platform" ? " is-active" : ""
            }`}
            onClick={() =>
              setPillar((cur) => (cur === "Platform" ? "all" : "Platform"))
            }
          >
            <span className="feat-pillar-num mono">··</span>
            <span className="feat-pillar-name">Platform</span>
            <span className="feat-pillar-count">
              {pillarCounts.Platform ?? 0}
            </span>
          </button>
        </div>

        <div className="feat-toolbar">
          <input
            type="search"
            className="feat-search"
            placeholder="Search features, hardware, MCU, tags…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            aria-label="Search features"
          />
          <select
            value={priority}
            onChange={(e) =>
              setPriority(e.target.value as FeaturePriority | "all")
            }
            aria-label="Priority"
          >
            {PRIORITY_FILTERS.map((p) => (
              <option key={p} value={p}>
                {p === "all"
                  ? `All priorities (${priorityCounts.all})`
                  : `${PRIORITY_LABEL[p]} (${priorityCounts[p] ?? 0})`}
              </option>
            ))}
          </select>
          <select
            value={actor}
            onChange={(e) =>
              setActor(e.target.value as (typeof ACTOR_FILTERS)[number])
            }
            aria-label="Care actor"
          >
            {ACTOR_FILTERS.map((a) => (
              <option key={a} value={a}>
                {a === "all"
                  ? "All actors"
                  : a === "m2m"
                    ? "M:N / both-ends only"
                    : ACTOR_LABEL[a]}
              </option>
            ))}
          </select>
          <select
            value={maturity}
            onChange={(e) =>
              setMaturity(e.target.value as FeatureMaturity | "all")
            }
            aria-label="Maturity"
          >
            {MATURITY_FILTERS.map((m) => (
              <option key={m} value={m}>
                {m === "all" ? "All maturities" : MATURITY_LABEL[m]}
              </option>
            ))}
          </select>
          <span className="feat-showing muted small">
            {filtered.length}/{FEATURE_LIST.length}
          </span>
        </div>
      </div>

      {byPillar.map((g) => (
        <section key={g.pillar} className="feat-section" id={`feat-${g.pillar}`}>
          <header className="feat-section-head">
            <p className="feat-section-kicker mono">
              {g.meta.num} · Svaraa · {g.pillar}
            </p>
            <h3 className="feat-section-title">{g.pillar}</h3>
            <p className="feat-section-tagline">{g.meta.tagline}</p>
            <p className="feat-section-pri mono">
              Ordered P1→P3 · Must {g.counts.P1} · Need {g.counts.P2} · Nice{" "}
              {g.counts.P3}
            </p>
          </header>
          <div className="feat-grid">
            {g.features.map((f) => (
              <FeatureCard
                key={f.id}
                feature={f}
                onOpenHardware={onOpenHardware}
              />
            ))}
          </div>
        </section>
      ))}

      {!filtered.length ? (
        <p className="muted">No features match those filters.</p>
      ) : null}
    </div>
  );
}
