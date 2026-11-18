import { useEffect, useState } from "react";
import { api, type Decision, type Ticket, type TicketDossier } from "../api";

const STATES = [
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

type SectionId = "task" | "plan" | "execution" | "results" | "activity";

function MarkdownBlock({ text }: { text: string }) {
  return <pre className="dossier-md">{text}</pre>;
}

export function TicketDrawer({
  ticketKey,
  onClose,
  onChanged,
}: {
  ticketKey: string;
  onClose: () => void;
  onChanged: () => void;
}) {
  const [dossier, setDossier] = useState<TicketDossier | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [section, setSection] = useState<SectionId>("task");

  useEffect(() => {
    let cancelled = false;
    setDossier(null);
    setError(null);
    setSection("task");
    api
      .dossier(ticketKey)
      .then((d) => {
        if (!cancelled) setDossier(d);
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      });
    return () => {
      cancelled = true;
    };
  }, [ticketKey]);

  const ticket: Ticket | undefined = dossier?.ticket;
  const decisions: Decision[] = ticket?.decisions ?? [];

  async function move(to: string) {
    setBusy(true);
    setError(null);
    try {
      await api.transition(ticketKey, to, `UI move to ${to}`);
      const d = await api.dossier(ticketKey);
      setDossier(d);
      onChanged();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function decide(decision: string, message: string) {
    setBusy(true);
    setError(null);
    try {
      await api.decide({
        ticket_key: ticketKey,
        decision,
        actor: "owner",
        message,
        plan_revision: ticket?.plan_revision ?? undefined,
      });
      const d = await api.dossier(ticketKey);
      setDossier(d);
      onChanged();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const body =
    section === "task"
      ? dossier?.sections.task
      : section === "plan"
        ? dossier?.sections.plan ||
          "_No plan.md yet. Plans appear under docs/tickets/<id>/plan.md when written._"
        : section === "execution"
          ? dossier?.sections.execution
          : section === "results"
            ? dossier?.sections.results
            : null;

  return (
    <div className="drawer-backdrop" role="presentation" onClick={onClose}>
      <aside
        className="drawer drawer-dossier"
        role="dialog"
        aria-modal="true"
        aria-label={`Ticket ${ticketKey}`}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="drawer-header">
          <div>
            <div className="card-key">{ticketKey}</div>
            <h2>{ticket?.summary ?? "Loading…"}</h2>
            {ticket && (
              <p className="muted small drawer-sub">
                {ticket.workflow_state} · {ticket.work_type} ·{" "}
                {ticket.source_namespace}
                {ticket.implementation_state
                  ? ` · ${ticket.implementation_state}`
                  : ""}
              </p>
            )}
          </div>
          <button type="button" className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </header>

        {error && <div className="banner-error">{error}</div>}

        {!dossier && !error && <p className="muted">Loading dossier…</p>}

        {dossier && ticket && (
          <>
            <div className="dossier-completeness" aria-label="Documentation coverage">
              {(
                [
                  ["ticket", "Task"],
                  ["plan", "Plan"],
                  ["implementation", "Execution"],
                  ["tests", "Tests"],
                  ["review", "Review"],
                ] as const
              ).map(([k, label]) => (
                <span
                  key={k}
                  className={
                    dossier.docs_present[k] ? "chip chip-ok" : "chip chip-miss"
                  }
                  title={
                    dossier.docs_present[k]
                      ? `${label} doc present`
                      : `${label} doc not written yet`
                  }
                >
                  {label}
                </span>
              ))}
              <span className="chip">
                evidence {dossier.completeness.evidence_file_count}
              </span>
              <span
                className={
                  dossier.completeness.has_firmware_evidence
                    ? "chip chip-ok"
                    : "chip chip-miss"
                }
                title={
                  dossier.completeness.has_firmware_evidence
                    ? "firmware.bin pinned in evidence"
                    : "No firmware.bin in evidence/"
                }
              >
                firmware{" "}
                {dossier.completeness.has_firmware_evidence
                  ? dossier.firmware_pins?.[0]?.sha12?.slice(0, 8) ?? "pin"
                  : "—"}
              </span>
            </div>

            <nav className="dossier-tabs" aria-label="Dossier sections">
              {(
                [
                  ["task", "Task"],
                  ["plan", "Plan"],
                  ["execution", "Execution"],
                  ["results", "Results"],
                  ["activity", "Activity"],
                ] as const
              ).map(([id, label]) => (
                <button
                  key={id}
                  type="button"
                  className="tab"
                  aria-current={section === id ? "page" : undefined}
                  onClick={() => setSection(id)}
                >
                  {label}
                </button>
              ))}
            </nav>

            <div className="dossier-body">
              {section !== "activity" && body != null && (
                <MarkdownBlock text={body} />
              )}

              {section === "activity" && (
                <>
                  <dl className="drawer-dl">
                    <dt>State</dt>
                    <dd>{ticket.workflow_state}</dd>
                    <dt>Implementation</dt>
                    <dd>{ticket.implementation_state ?? "—"}</dd>
                    <dt>Acceptance</dt>
                    <dd>{ticket.owner_acceptance ?? "—"}</dd>
                    <dt>Plan rev</dt>
                    <dd>{ticket.plan_revision ?? "—"}</dd>
                    <dt>Parent</dt>
                    <dd>{ticket.parent_key ?? "—"}</dd>
                    <dt>Deps</dt>
                    <dd>{ticket.plan_dependencies ?? "—"}</dd>
                    <dt>Docs path</dt>
                    <dd>{dossier.docs_dir ?? "(none yet)"}</dd>
                    <dt>Updated</dt>
                    <dd>{ticket.updated_at ?? "—"}</dd>
                  </dl>

                  {!!ticket.children?.length && (
                    <section>
                      <h3>Children</h3>
                      <ul className="child-list">
                        {ticket.children.map((c) => (
                          <li key={c.ticket_key}>
                            <strong>{c.ticket_key}</strong> · {c.workflow_state} —{" "}
                            {c.summary}
                          </li>
                        ))}
                      </ul>
                    </section>
                  )}

                  <section>
                    <h3>Move</h3>
                    <div className="move-row">
                      {STATES.filter((s) => s !== ticket.workflow_state).map(
                        (s) => (
                          <button
                            key={s}
                            type="button"
                            className="btn-secondary"
                            disabled={busy}
                            onClick={() => void move(s)}
                          >
                            {s}
                          </button>
                        ),
                      )}
                    </div>
                  </section>

                  <section>
                    <h3>Approvals</h3>
                    <div className="move-row">
                      <button
                        type="button"
                        className="btn-secondary"
                        disabled={busy}
                        onClick={() =>
                          void decide(
                            "APPROVE_PLAN",
                            "Owner approved plan (SIM scope)",
                          )
                        }
                      >
                        Approve plan
                      </button>
                      <button
                        type="button"
                        className="btn-secondary"
                        disabled={busy}
                        onClick={() =>
                          void decide(
                            "ACCEPT_SIM",
                            "Owner accepted SIM-scope delivery",
                          )
                        }
                      >
                        Accept (SIM)
                      </button>
                    </div>
                  </section>

                  {!!decisions.length && (
                    <section>
                      <h3>Decision log</h3>
                      <ul className="decision-list">
                        {decisions.map((d) => (
                          <li key={d.id}>
                            <strong>{d.decision}</strong> · {d.actor}
                            <div className="muted small">{d.created_at}</div>
                            {d.message && <div>{d.message}</div>}
                          </li>
                        ))}
                      </ul>
                    </section>
                  )}

                  {!!dossier.firmware_pins?.length && (
                    <section>
                      <h3>Firmware pins</h3>
                      <ul className="decision-list">
                        {dossier.firmware_pins.map((e) => (
                          <li key={e.path}>
                            <code>{e.path}</code>
                            <div className="muted small mono">
                              sha256 {e.sha12 ?? e.sha256?.slice(0, 12)}… · {e.bytes} B
                            </div>
                          </li>
                        ))}
                      </ul>
                    </section>
                  )}

                  {!!dossier.evidence.length && (
                    <section>
                      <h3>Evidence index</h3>
                      <ul className="decision-list">
                        {dossier.evidence.slice(0, 40).map((e) => (
                          <li key={e.path}>
                            <code>{e.path}</code>
                            {e.sha12 ? (
                              <div className="muted small mono">fw {e.sha12}…</div>
                            ) : null}
                          </li>
                        ))}
                      </ul>
                    </section>
                  )}
                </>
              )}
            </div>
          </>
        )}
      </aside>
    </div>
  );
}
