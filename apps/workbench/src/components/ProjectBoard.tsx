import { useCallback, useEffect, useMemo, useState } from "react";
import { api, type BoardSummary, type Ticket } from "../api";
import { TicketDrawer } from "./TicketDrawer";

const COLUMN_ORDER = [
  "Backlog",
  "Planning",
  "Awaiting Plan Approval",
  "Ready",
  "In Progress",
  "Testing",
  "Awaiting Acceptance",
  "Done",
  "Blocked",
];

type Filters = {
  namespace: "all" | "original" | "workbench";
  workType: "all" | "Epic" | "Story" | "Sub-task" | "Workbench";
  q: string;
  hideDone: boolean;
  /** WB-033 — label contains wokwi (case-insensitive) */
  wokwiOnly: boolean;
  /** WB-033 — Ready column only */
  readyOnly: boolean;
};

export function ProjectBoard() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [summary, setSummary] = useState<BoardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);
  const [filters, setFilters] = useState<Filters>({
    namespace: "all",
    workType: "all",
    q: "",
    hideDone: false,
    wokwiOnly: false,
    readyOnly: false,
  });

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, t] = await Promise.all([api.summary(), api.tickets()]);
      setSummary(s);
      setTickets(t.tickets);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
    const id = window.setInterval(() => void load(), 5000);
    return () => window.clearInterval(id);
  }, [load]);

  const filtered = useMemo(() => {
    return tickets.filter((t) => {
      if (filters.namespace !== "all" && t.source_namespace !== filters.namespace)
        return false;
      if (filters.workType !== "all" && t.work_type !== filters.workType) return false;
      if (filters.hideDone && t.workflow_state === "Done") return false;
      if (filters.readyOnly && t.workflow_state !== "Ready") return false;
      if (filters.wokwiOnly) {
        const labels = (t.labels ?? "").toLowerCase();
        const hay = `${t.ticket_key} ${t.summary} ${labels}`.toLowerCase();
        if (!labels.includes("wokwi") && !hay.includes("wokwi")) return false;
      }
      if (filters.q) {
        const q = filters.q.toLowerCase();
        if (
          !t.ticket_key.toLowerCase().includes(q) &&
          !t.summary.toLowerCase().includes(q) &&
          !(t.labels ?? "").toLowerCase().includes(q)
        )
          return false;
      }
      return true;
    });
  }, [tickets, filters]);

  const byColumn = useMemo(() => {
    const map: Record<string, Ticket[]> = {};
    for (const c of COLUMN_ORDER) map[c] = [];
    for (const t of filtered) {
      const col = COLUMN_ORDER.includes(t.workflow_state)
        ? t.workflow_state
        : "Backlog";
      map[col].push(t);
    }
    return map;
  }, [filtered]);

  return (
    <div className="board">
      <div className="board-toolbar">
        <div className="board-progress">
          {summary ? (
            <>
              <strong>
                {summary.done}/{summary.total} Done
              </strong>
              <span className="muted">
                · original {summary.counts_by_namespace.original ?? 0} · workbench{" "}
                {summary.counts_by_namespace.workbench ?? 0}
              </span>
              <div className="progress-bar" aria-hidden>
                <div
                  className="progress-fill"
                  style={{
                    width: `${summary.total ? (100 * summary.done) / summary.total : 0}%`,
                  }}
                />
              </div>
            </>
          ) : (
            <span className="muted">Loading board…</span>
          )}
        </div>
        <div className="board-filters">
          <input
            type="search"
            placeholder="Search tickets…"
            value={filters.q}
            onChange={(e) => setFilters((f) => ({ ...f, q: e.target.value }))}
            aria-label="Search tickets"
          />
          <select
            value={filters.namespace}
            onChange={(e) =>
              setFilters((f) => ({
                ...f,
                namespace: e.target.value as Filters["namespace"],
              }))
            }
            aria-label="Namespace"
          >
            <option value="all">All sources</option>
            <option value="original">Original backlog</option>
            <option value="workbench">Workbench (WB-*)</option>
          </select>
          <select
            value={filters.workType}
            onChange={(e) =>
              setFilters((f) => ({
                ...f,
                workType: e.target.value as Filters["workType"],
              }))
            }
            aria-label="Work type"
          >
            <option value="all">All types</option>
            <option value="Epic">Epic</option>
            <option value="Story">Story</option>
            <option value="Sub-task">Sub-task</option>
            <option value="Workbench">Workbench</option>
          </select>
          <label className="check">
            <input
              type="checkbox"
              checked={filters.hideDone}
              onChange={(e) =>
                setFilters((f) => ({ ...f, hideDone: e.target.checked }))
              }
            />
            Hide Done
          </label>
          <label className="check">
            <input
              type="checkbox"
              checked={filters.wokwiOnly}
              onChange={(e) =>
                setFilters((f) => ({ ...f, wokwiOnly: e.target.checked }))
              }
            />
            Wokwi
          </label>
          <label className="check">
            <input
              type="checkbox"
              checked={filters.readyOnly}
              onChange={(e) =>
                setFilters((f) => ({ ...f, readyOnly: e.target.checked }))
              }
            />
            Ready only
          </label>
          <button
            type="button"
            className="btn-secondary"
            title="WB-033 preset: wokwi label + Ready column"
            onClick={() =>
              setFilters((f) => ({
                ...f,
                wokwiOnly: true,
                readyOnly: true,
                hideDone: true,
                namespace: "workbench",
              }))
            }
          >
            Wokwi · Ready
          </button>
          <button type="button" className="btn-secondary" onClick={() => void load()}>
            Refresh
          </button>
          <a className="btn-secondary" href="/lab/v1/board/export.csv" download>
            Export CSV
          </a>
        </div>
      </div>

      {error && <div className="banner-error">Board API error: {error}</div>}
      {loading && !tickets.length && <p className="muted">Loading tickets…</p>}

      <div className="kanban" role="list">
        {COLUMN_ORDER.map((col) => (
          <section key={col} className="kanban-col" aria-label={col}>
            <header>
              <h3>{col}</h3>
              <span className="count">{byColumn[col]?.length ?? 0}</span>
            </header>
            <div className="kanban-cards">
              {(byColumn[col] || []).map((t) => (
                <button
                  key={t.ticket_key}
                  type="button"
                  className={`card ns-${t.source_namespace} type-${t.work_type.replace(/\s/g, "")}`}
                  onClick={() => setSelected(t.ticket_key)}
                >
                  <div className="card-key">{t.ticket_key}</div>
                  <div className="card-summary">{t.summary}</div>
                  <div className="card-meta">
                    <span>{t.work_type}</span>
                    {t.priority && <span>{t.priority}</span>}
                    {t.plan_revision && <span>plan {t.plan_revision}</span>}
                  </div>
                </button>
              ))}
            </div>
          </section>
        ))}
      </div>

      {selected && (
        <TicketDrawer
          ticketKey={selected}
          onClose={() => setSelected(null)}
          onChanged={() => void load()}
        />
      )}
    </div>
  );
}
