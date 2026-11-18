"""Consent / retention audit stubs (SV0-09.06 / aligns SV0-12.04 SIM)."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any


def ensure_consent_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS consent_grants (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          subject_id TEXT NOT NULL,
          purpose TEXT NOT NULL,
          granted INTEGER NOT NULL,
          actor TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS retention_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          subject_id TEXT NOT NULL,
          action TEXT NOT NULL,
          detail TEXT,
          created_at TEXT NOT NULL
        );
        """
    )
    conn.commit()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


ALLOWED_PURPOSES = {"sos_delivery", "location_incident", "guardian_notify"}
# Ambient audio upload is forbidden in V0 SIM policy
FORBIDDEN_PURPOSES = {"ambient_audio_upload"}


def set_consent(
    conn: sqlite3.Connection,
    *,
    subject_id: str,
    purpose: str,
    granted: bool,
    actor: str,
) -> dict[str, Any]:
    ensure_consent_schema(conn)
    if purpose in FORBIDDEN_PURPOSES:
        return {
            "ok": False,
            "error": "forbidden_purpose",
            "purpose": purpose,
            "note": "No ambient audio upload",
        }
    if purpose not in ALLOWED_PURPOSES:
        return {"ok": False, "error": "unknown_purpose", "purpose": purpose}
    conn.execute(
        """
        INSERT INTO consent_grants(subject_id, purpose, granted, actor, created_at)
        VALUES (?,?,?,?,?)
        """,
        (subject_id, purpose, 1 if granted else 0, actor, _utc()),
    )
    conn.commit()
    return {"ok": True, "subject_id": subject_id, "purpose": purpose, "granted": granted}


def revoke_all(conn: sqlite3.Connection, *, subject_id: str, actor: str) -> dict[str, Any]:
    ensure_consent_schema(conn)
    conn.execute(
        """
        INSERT INTO consent_grants(subject_id, purpose, granted, actor, created_at)
        VALUES (?,?,?,?,?)
        """,
        (subject_id, "ALL", 0, actor, _utc()),
    )
    conn.execute(
        """
        INSERT INTO retention_events(subject_id, action, detail, created_at)
        VALUES (?,?,?,?)
        """,
        (subject_id, "access_revoked", "role revocation recorded", _utc()),
    )
    conn.commit()
    return {"ok": True, "subject_id": subject_id, "revoked": True}


def latest_grants(conn: sqlite3.Connection, subject_id: str) -> dict[str, bool]:
    ensure_consent_schema(conn)
    rows = conn.execute(
        """
        SELECT purpose, granted FROM consent_grants
        WHERE subject_id=? ORDER BY id DESC
        """,
        (subject_id,),
    ).fetchall()
    out: dict[str, bool] = {}
    for r in rows:
        if r["purpose"] == "ALL" and not r["granted"]:
            return {p: False for p in ALLOWED_PURPOSES}
        if r["purpose"] not in out:
            out[r["purpose"]] = bool(r["granted"])
    return out
