"""SQLite board authority — import bootstrap once, then own workflow state."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

COLUMNS = [
    "Backlog",
    "Planning",
    "Awaiting Plan Approval",
    "Ready",
    "In Progress",
    "Testing",
    "Awaiting Acceptance",
    "Done",
    "Blocked",
]

# Allowed transitions for SIM lab board (simplified; approvals still logged).
ALLOWED: dict[str, set[str]] = {
    "Backlog": {"Planning", "Ready", "In Progress", "Blocked"},
    "Planning": {"Awaiting Plan Approval", "Backlog", "Blocked"},
    "Awaiting Plan Approval": {"Ready", "Planning", "Blocked"},
    "Ready": {"In Progress", "Backlog", "Blocked"},
    "In Progress": {"Testing", "Blocked", "Awaiting Acceptance"},
    "Testing": {"Awaiting Acceptance", "In Progress", "Blocked"},
    "Awaiting Acceptance": {"Done", "In Progress", "Blocked"},
    "Done": {"Backlog", "In Progress"},  # reopen
    "Blocked": {"Backlog", "Planning", "Ready", "In Progress"},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def project_root() -> Path:
    # services/api/app/board_db.py -> Lab root
    return Path(__file__).resolve().parents[3]


def db_path() -> Path:
    root = project_root()
    path = root / ".workbench" / "lab.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path()), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tickets (
          ticket_key TEXT PRIMARY KEY,
          source_id TEXT,
          work_type TEXT NOT NULL,
          summary TEXT NOT NULL,
          description TEXT,
          parent_key TEXT,
          parent_source_id TEXT,
          priority TEXT,
          labels TEXT,
          workflow_state TEXT NOT NULL,
          implementation_state TEXT,
          owner_acceptance TEXT,
          plan_revision TEXT,
          profile_default TEXT DEFAULT 'SIM',
          source_namespace TEXT NOT NULL,
          plan_title TEXT,
          plan_acceptance TEXT,
          plan_dependencies TEXT,
          blocked_reason TEXT,
          updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS decisions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ticket_key TEXT,
          decision TEXT NOT NULL,
          plan_revision TEXT,
          evidence_revision TEXT,
          actor TEXT NOT NULL,
          message TEXT,
          created_at TEXT NOT NULL
        );
        """
    )
    conn.commit()


def _ticket_key_from_row(row: dict[str, Any]) -> str:
    if row.get("display_key"):
        return str(row["display_key"])
    if row.get("ticket_id"):
        return str(row["ticket_id"])
    return str(row.get("source_id") or "UNKNOWN")


def import_bootstrap(conn: sqlite3.Connection, force: bool = False) -> dict[str, Any]:
    init_schema(conn)
    imported = conn.execute("SELECT value FROM meta WHERE key='bootstrap_imported'").fetchone()
    if imported and not force:
        count = conn.execute("SELECT COUNT(*) AS c FROM tickets").fetchone()["c"]
        return {"imported": False, "ticket_count": count, "reason": "already_imported"}

    bootstrap_path = project_root() / "data/seeds/board_bootstrap_v0.1.json"
    data = json.loads(bootstrap_path.read_text())
    now = utc_now()

    if force:
        conn.execute("DELETE FROM tickets")
        conn.execute("DELETE FROM decisions")

    rows = []
    for t in data.get("original_tickets", []):
        rows.append(
            (
                _ticket_key_from_row(t),
                t.get("source_id"),
                t.get("work_type") or "Sub-task",
                t.get("summary") or "",
                t.get("description_source"),
                None,  # parent_key filled below
                t.get("parent_source_id"),
                t.get("priority"),
                t.get("labels"),
                t.get("workflow_state") or "Backlog",
                t.get("implementation_state") or "not_started",
                t.get("owner_acceptance"),
                t.get("plan_revision"),
                t.get("profile_default") or "SIM",
                t.get("source_namespace") or "original",
                t.get("plan_title"),
                t.get("plan_acceptance"),
                t.get("plan_dependencies"),
                None,
                now,
            )
        )
    for t in data.get("proposed_workbench_tickets", []):
        rows.append(
            (
                _ticket_key_from_row(t),
                None,
                "Workbench",
                t.get("summary") or t.get("ticket_id") or "",
                "Workbench addition; links " + ",".join(t.get("links") or []),
                None,
                None,
                "High",
                "workbench",
                t.get("workflow_state") or "Backlog",
                t.get("implementation_state") or "not_started",
                None,
                None,
                "SIM",
                t.get("source_namespace") or "workbench",
                None,
                None,
                ",".join(t.get("links") or []),
                None,
                now,
            )
        )

    conn.executemany(
        """
        INSERT OR REPLACE INTO tickets (
          ticket_key, source_id, work_type, summary, description,
          parent_key, parent_source_id, priority, labels,
          workflow_state, implementation_state, owner_acceptance, plan_revision,
          profile_default, source_namespace, plan_title, plan_acceptance,
          plan_dependencies, blocked_reason, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        rows,
    )

    # Resolve parent_key from parent_source_id
    by_source = {
        r["source_id"]: r["ticket_key"]
        for r in conn.execute(
            "SELECT source_id, ticket_key FROM tickets WHERE source_id IS NOT NULL"
        )
    }
    for r in conn.execute(
        "SELECT ticket_key, parent_source_id FROM tickets WHERE parent_source_id IS NOT NULL"
    ):
        pk = by_source.get(r["parent_source_id"])
        if pk:
            conn.execute(
                "UPDATE tickets SET parent_key=? WHERE ticket_key=?",
                (pk, r["ticket_key"]),
            )

    for a in data.get("approvals", []):
        conn.execute(
            """
            INSERT INTO decisions (ticket_key, decision, plan_revision, evidence_revision, actor, message, created_at)
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                a.get("ticket_id"),
                a.get("decision") or "NOTE",
                a.get("plan_revision") or a.get("revision"),
                a.get("evidence_revision"),
                a.get("actor") or "system",
                a.get("message") or a.get("scope"),
                a.get("timestamp") or now,
            ),
        )

    # Batch auth
    batch = data.get("batch_authorization")
    if batch:
        conn.execute(
            """
            INSERT INTO decisions (ticket_key, decision, plan_revision, evidence_revision, actor, message, created_at)
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                None,
                "BATCH_AUTHORIZATION",
                batch.get("id"),
                None,
                batch.get("actor") or "owner",
                batch.get("message"),
                batch.get("timestamp") or now,
            ),
        )

    conn.execute(
        "INSERT OR REPLACE INTO meta(key,value) VALUES ('bootstrap_imported', ?)",
        (now,),
    )
    conn.execute(
        "INSERT OR REPLACE INTO meta(key,value) VALUES ('schema_version', '1.0')",
    )
    src = data.get("source") or {}
    conn.execute(
        "INSERT OR REPLACE INTO meta(key,value) VALUES ('source_json', ?)",
        (json.dumps(src),),
    )
    conn.commit()
    count = conn.execute("SELECT COUNT(*) AS c FROM tickets").fetchone()["c"]
    return {"imported": True, "ticket_count": count, "at": now}


def list_tickets(
    conn: sqlite3.Connection,
    *,
    namespace: str | None = None,
    work_type: str | None = None,
    state: str | None = None,
    q: str | None = None,
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM tickets WHERE 1=1"
    args: list[Any] = []
    if namespace:
        sql += " AND source_namespace=?"
        args.append(namespace)
    if work_type:
        sql += " AND work_type=?"
        args.append(work_type)
    if state:
        sql += " AND workflow_state=?"
        args.append(state)
    if q:
        sql += " AND (ticket_key LIKE ? OR summary LIKE ?)"
        args.extend([f"%{q}%", f"%{q}%"])
    sql += " ORDER BY source_namespace DESC, work_type, ticket_key"
    return [dict(r) for r in conn.execute(sql, args)]


def get_ticket(conn: sqlite3.Connection, key: str) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM tickets WHERE ticket_key=?", (key,)).fetchone()
    if not row:
        return None
    ticket = dict(row)
    ticket["decisions"] = [
        dict(r)
        for r in conn.execute(
            "SELECT * FROM decisions WHERE ticket_key=? ORDER BY id DESC", (key,)
        )
    ]
    ticket["children"] = [
        dict(r)
        for r in conn.execute(
            "SELECT ticket_key, work_type, summary, workflow_state, priority FROM tickets WHERE parent_key=? ORDER BY ticket_key",
            (key,),
        )
    ]
    return ticket


def summary(conn: sqlite3.Connection) -> dict[str, Any]:
    by_state = {
        r["workflow_state"]: r["c"]
        for r in conn.execute(
            "SELECT workflow_state, COUNT(*) AS c FROM tickets GROUP BY workflow_state"
        )
    }
    by_ns = {
        r["source_namespace"]: r["c"]
        for r in conn.execute(
            "SELECT source_namespace, COUNT(*) AS c FROM tickets GROUP BY source_namespace"
        )
    }
    return {
        "columns": COLUMNS,
        "counts_by_state": {c: by_state.get(c, 0) for c in COLUMNS},
        "counts_by_namespace": by_ns,
        "total": sum(by_state.values()),
        "done": by_state.get("Done", 0),
        "profile": "SIM",
        "simulated": True,
    }


def transition(
    conn: sqlite3.Connection,
    key: str,
    to_state: str,
    *,
    actor: str = "agent",
    message: str | None = None,
    blocked_reason: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    if to_state not in COLUMNS:
        raise ValueError(f"unknown state {to_state}")
    row = conn.execute("SELECT * FROM tickets WHERE ticket_key=?", (key,)).fetchone()
    if not row:
        raise KeyError(key)
    current = row["workflow_state"]
    if not force and to_state not in ALLOWED.get(current, set()):
        raise PermissionError(f"transition {current} -> {to_state} not allowed")
    now = utc_now()
    conn.execute(
        """
        UPDATE tickets
        SET workflow_state=?, blocked_reason=?, updated_at=?
        WHERE ticket_key=?
        """,
        (
            to_state,
            blocked_reason if to_state == "Blocked" else None,
            now,
            key,
        ),
    )
    conn.execute(
        """
        INSERT INTO decisions (ticket_key, decision, plan_revision, evidence_revision, actor, message, created_at)
        VALUES (?,?,?,?,?,?,?)
        """,
        (key, f"TRANSITION:{current}->{to_state}", None, None, actor, message, now),
    )
    conn.commit()
    return get_ticket(conn, key)  # type: ignore


def record_decision(
    conn: sqlite3.Connection,
    *,
    ticket_key: str | None,
    decision: str,
    actor: str,
    message: str | None = None,
    plan_revision: str | None = None,
    evidence_revision: str | None = None,
) -> dict[str, Any]:
    now = utc_now()
    cur = conn.execute(
        """
        INSERT INTO decisions (ticket_key, decision, plan_revision, evidence_revision, actor, message, created_at)
        VALUES (?,?,?,?,?,?,?)
        """,
        (ticket_key, decision, plan_revision, evidence_revision, actor, message, now),
    )
    if ticket_key and decision.startswith("ACCEPT"):
        conn.execute(
            """
            UPDATE tickets SET owner_acceptance='accepted_sim_scope', workflow_state='Done',
              implementation_state=COALESCE(implementation_state,'implemented_sim'), updated_at=?
            WHERE ticket_key=?
            """,
            (now, ticket_key),
        )
    conn.commit()
    return {"id": cur.lastrowid, "created_at": now}


def provenance(conn: sqlite3.Connection) -> dict[str, Any]:
    """Re-hash pack CSV/plan and compare to bootstrap seed hashes (WB-001)."""
    import hashlib

    root = project_root()
    bootstrap_path = root / "data/seeds/board_bootstrap_v0.1.json"
    data = json.loads(bootstrap_path.read_text())
    src = data.get("source") or {}
    checks = []
    for label, rel, expected_key in (
        ("csv", src.get("csv_path"), "csv_sha256"),
        ("plan_json", src.get("plan_json_path"), "plan_json_sha256"),
    ):
        expected = src.get(expected_key)
        path = root / rel if rel else None
        actual = None
        exists = False
        if path and path.is_file():
            exists = True
            h = hashlib.sha256()
            h.update(path.read_bytes())
            actual = h.hexdigest()
        checks.append(
            {
                "label": label,
                "path": rel,
                "exists": exists,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "match": bool(expected and actual and expected == actual),
            }
        )
    meta_src = conn.execute("SELECT value FROM meta WHERE key='source_json'").fetchone()
    return {
        "profile": "SIM",
        "bootstrap": str(bootstrap_path.relative_to(root)),
        "stored_source": json.loads(meta_src["value"]) if meta_src else None,
        "checks": checks,
        "ok": all(c["match"] for c in checks),
        "ticket_count": conn.execute("SELECT COUNT(*) AS c FROM tickets").fetchone()["c"],
    }


def export_csv(conn: sqlite3.Connection) -> str:
    """CSV export of current board authority (WB-003)."""
    import csv
    import io

    fields = [
        "ticket_key",
        "work_type",
        "summary",
        "workflow_state",
        "implementation_state",
        "owner_acceptance",
        "parent_key",
        "priority",
        "source_namespace",
        "plan_dependencies",
        "plan_revision",
        "blocked_reason",
        "updated_at",
    ]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    for r in conn.execute(
        "SELECT * FROM tickets ORDER BY source_namespace, ticket_key"
    ):
        w.writerow(dict(r))
    return buf.getvalue()
