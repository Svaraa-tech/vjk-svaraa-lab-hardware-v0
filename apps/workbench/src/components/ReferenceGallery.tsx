import { useEffect, useMemo, useState } from "react";
import { api, type GalleryItem } from "../api";

export function ReferenceGallery() {
  const [items, setItems] = useState<GalleryItem[]>([]);
  const [q, setQ] = useState("");
  const [kind, setKind] = useState("all");
  const [error, setError] = useState<string | null>(null);
  const [compareA, setCompareA] = useState<string | null>(null);
  const [compareB, setCompareB] = useState<string | null>(null);

  useEffect(() => {
    api
      .gallery()
      .then((r) => setItems(r.items))
      .catch((e: Error) => setError(e.message));
  }, []);

  const filtered = useMemo(() => {
    return items.filter((it) => {
      if (kind !== "all" && it.kind !== kind) return false;
      if (!q) return true;
      const s = q.toLowerCase();
      return (
        it.title.toLowerCase().includes(s) ||
        it.id.toLowerCase().includes(s) ||
        it.path.toLowerCase().includes(s) ||
        (it.sha12 ?? "").toLowerCase().includes(s) ||
        (it.source ?? "").toLowerCase().includes(s)
      );
    });
  }, [items, q, kind]);

  const kinds = useMemo(
    () => Array.from(new Set(items.map((i) => i.kind))).sort(),
    [items],
  );

  const firmware = useMemo(
    () => filtered.filter((it) => it.kind === "firmware"),
    [filtered],
  );
  const others = useMemo(
    () => filtered.filter((it) => it.kind !== "firmware"),
    [filtered],
  );

  const fwById = useMemo(() => {
    const m = new Map<string, GalleryItem>();
    for (const it of items.filter((i) => i.kind === "firmware")) m.set(it.id, it);
    return m;
  }, [items]);

  const left = compareA ? fwById.get(compareA) : undefined;
  const right = compareB ? fwById.get(compareB) : undefined;
  const sameSha =
    left?.sha256 && right?.sha256 ? left.sha256 === right.sha256 : null;

  function toggleCompare(id: string) {
    if (compareA === id) {
      setCompareA(null);
      return;
    }
    if (compareB === id) {
      setCompareB(null);
      return;
    }
    if (!compareA) {
      setCompareA(id);
      return;
    }
    if (!compareB) {
      setCompareB(id);
      return;
    }
    // replace B
    setCompareB(id);
  }

  return (
    <div className="gallery">
      <header className="sim-header">
        <div>
          <h2>References</h2>
          <p className="muted small">
            Pack diagrams/docs + Lab markdown + firmware thumbs · {filtered.length}/
            {items.length}
          </p>
        </div>
        <div className="board-filters">
          <input
            type="search"
            placeholder="Search…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            aria-label="Search gallery"
          />
          <select
            value={kind}
            onChange={(e) => setKind(e.target.value)}
            aria-label="Kind"
          >
            <option value="all">All kinds</option>
            {kinds.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
        </div>
      </header>
      {error && <div className="banner-error">{error}</div>}

      {firmware.length > 0 && (kind === "all" || kind === "firmware") ? (
        <section className="gallery-firmware" aria-label="Firmware artifacts">
          <h3 className="muted small">
            Firmware artifacts · click two thumbs to compare (WB-032)
          </h3>
          <ul className="gallery-fw-grid">
            {firmware.map((it) => {
              const selected = it.id === compareA || it.id === compareB;
              return (
                <li key={it.id}>
                  <button
                    type="button"
                    className={`gallery-fw-card ${selected ? "gallery-fw-selected" : ""}`}
                    onClick={() => toggleCompare(it.id)}
                  >
                    <div className="gallery-fw-thumb" aria-hidden>
                      <span>
                        {it.thumb?.label ?? `FW ${(it.sha12 ?? "····").slice(0, 8)}`}
                      </span>
                    </div>
                    <div className="gallery-title">{it.title}</div>
                    <div className="muted small">
                      <span className="chip">firmware</span>{" "}
                      <code>{it.sha12 ?? it.sha256?.slice(0, 12) ?? "—"}…</code>
                    </div>
                    <div className="muted small">
                      {it.bytes != null ? `${it.bytes} B` : ""}
                      {it.source ? ` · ${it.source}` : ""}
                    </div>
                    <div className="muted small mono">{it.path}</div>
                  </button>
                </li>
              );
            })}
          </ul>

          {(left || right) && (
            <div className="gallery-fw-compare" aria-live="polite">
              <div>
                <strong>A</strong>
                <div className="mono muted small">
                  {left ? `${left.sha12}… · ${left.bytes} B · ${left.source}` : "—"}
                </div>
              </div>
              <div className="gallery-fw-compare-mid">
                {sameSha == null ? (
                  <span className="muted small">Select two</span>
                ) : sameSha ? (
                  <span className="badge-ok">identical sha256</span>
                ) : (
                  <span className="badge-warn">sha mismatch</span>
                )}
                {left && right && left.bytes != null && right.bytes != null ? (
                  <div className="muted small">
                    Δ bytes {right.bytes - left.bytes}
                  </div>
                ) : null}
              </div>
              <div>
                <strong>B</strong>
                <div className="mono muted small">
                  {right ? `${right.sha12}… · ${right.bytes} B · ${right.source}` : "—"}
                </div>
              </div>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => {
                  setCompareA(null);
                  setCompareB(null);
                }}
              >
                Clear compare
              </button>
            </div>
          )}
        </section>
      ) : null}

      <ul className="gallery-list">
        {others.map((it) => (
          <li key={it.id}>
            <div className="gallery-title">{it.title}</div>
            <div className="muted small">
              <span className="chip">{it.kind}</span>{" "}
              <code>{it.path}</code>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
