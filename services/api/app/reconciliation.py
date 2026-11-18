"""Incident reconciliation helpers (SV0-09.05) — SIM."""
from __future__ import annotations

import json
import sqlite3
from typing import Any


def reconcile_incident(conn: sqlite3.Connection, incident_id: str) -> dict[str, Any]:
    """Compare events, outbox, human actions, notification stages for one incident."""
    inc = conn.execute(
        "SELECT * FROM incidents WHERE incident_id=?", (incident_id,)
    ).fetchone()
    if not inc:
        return {"ok": False, "error": "missing_incident"}

    events = [
        dict(r)
        for r in conn.execute(
            "SELECT event_id, kind, mode, body_sha256 FROM device_events WHERE incident_id=?",
            (incident_id,),
        )
    ]
    outbox = [
        dict(r)
        for r in conn.execute("SELECT * FROM outbox WHERE incident_id=?", (incident_id,))
    ]
    actions = [
        dict(r)
        for r in conn.execute(
            "SELECT action_id, action, result, expected_revision FROM human_actions WHERE incident_id=?",
            (incident_id,),
        )
    ]
    notes = [
        dict(r)
        for r in conn.execute(
            "SELECT stage, provider, detail FROM notification_jobs WHERE incident_id=? ORDER BY id",
            (incident_id,),
        )
    ]

    issues: list[str] = []
    if len(events) != 1:
        issues.append(f"expected_one_event_got_{len(events)}")
    if len({e["event_id"] for e in events}) != len(events):
        issues.append("duplicate_event_ids")
    if inc["mode"] == "drill":
        if any(n["stage"] == "provider_submit" for n in notes):
            issues.append("drill_dispatched_to_provider")
    if inc["phase"] == "HumanAck":
        if not any(a["action"] == "ack" and a["result"] == "accepted" for a in actions):
            issues.append("human_ack_phase_without_audit")
    # provider submit ≠ human ack
    stages = [n["stage"] for n in notes]
    if "human_ack" in stages and "provider_submit" in stages:
        # healthy distinction
        pass

    return {
        "ok": not issues,
        "incident_id": incident_id,
        "phase": inc["phase"],
        "revision": inc["revision"],
        "mode": inc["mode"],
        "event_count": len(events),
        "outbox": outbox,
        "actions": actions,
        "notification_stages": stages,
        "issues": issues,
        "profile": "SIM",
        "simulated": True,
    }
