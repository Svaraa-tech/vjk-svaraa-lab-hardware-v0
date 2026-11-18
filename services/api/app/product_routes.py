"""Product ingest / human actions / mock notifications (SIM) — SV0-09.01–09.04."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["product-sim"])

_conn: sqlite3.Connection | None = None

# Lab SIM allows only this device tenant unless header matches
ALLOWED_DEVICE_PREFIX = "sv0-lab-"


def _root() -> Path:
    return Path(__file__).resolve().parents[3]


def _db_path() -> Path:
    p = _root() / ".workbench" / "product.db"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def get_product_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(str(_db_path()), check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS device_events (
              event_id TEXT PRIMARY KEY,
              device_id TEXT NOT NULL,
              incident_id TEXT,
              kind TEXT NOT NULL,
              mode TEXT NOT NULL,
              body_json TEXT NOT NULL,
              body_sha256 TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS incidents (
              incident_id TEXT PRIMARY KEY,
              device_id TEXT NOT NULL,
              mode TEXT NOT NULL,
              phase TEXT NOT NULL,
              revision INTEGER NOT NULL DEFAULT 0,
              location_json TEXT,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS outbox (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              event_id TEXT NOT NULL,
              incident_id TEXT,
              status TEXT NOT NULL,
              provider TEXT NOT NULL DEFAULT 'mock',
              attempts INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL,
              UNIQUE(event_id)
            );
            CREATE TABLE IF NOT EXISTS human_actions (
              action_id TEXT PRIMARY KEY,
              incident_id TEXT NOT NULL,
              action TEXT NOT NULL,
              actor TEXT NOT NULL,
              expected_revision INTEGER,
              result TEXT NOT NULL,
              message TEXT,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS notification_jobs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              incident_id TEXT NOT NULL,
              stage TEXT NOT NULL,
              provider TEXT NOT NULL,
              detail TEXT,
              created_at TEXT NOT NULL
            );
            """
        )
        _conn.commit()
    return _conn


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _audit(
    conn: sqlite3.Connection,
    *,
    action_id: str,
    incident_id: str,
    action: str,
    actor: str,
    expected_revision: int | None,
    result: str,
    message: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO human_actions(action_id, incident_id, action, actor, expected_revision, result, message, created_at)
        VALUES (?,?,?,?,?,?,?,?)
        """,
        (
            action_id,
            incident_id,
            action,
            actor,
            expected_revision,
            result,
            message,
            _utc(),
        ),
    )


def _validate_sos_created(body: dict[str, Any]) -> None:
    required = [
        "schema_version",
        "event_id",
        "device_id",
        "boot_id",
        "seq",
        "mode",
        "kind",
        "uptime_ms",
        "incident_id",
        "payload",
    ]
    for k in required:
        if k not in body:
            raise ValueError(f"missing {k}")
    if body.get("schema_version") != "1.0":
        raise ValueError("schema_version must be 1.0")
    if body.get("kind") != "sos.created":
        raise ValueError("only sos.created supported in this slice")
    if body.get("mode") not in ("live", "drill"):
        raise ValueError("invalid mode")
    if body.get("mode") == "live" and body.get("drill_id") is not None:
        raise ValueError("live events must have drill_id null")
    if body.get("mode") == "drill" and not body.get("drill_id"):
        raise ValueError("drill events require drill_id")
    payload = body.get("payload") or {}
    loc = payload.get("location") or {}
    if "trigger" not in payload:
        raise ValueError("payload.trigger required")
    if loc.get("source") == "none":
        if loc.get("valid") is not False:
            raise ValueError("source=none requires valid=false")
        if loc.get("latitude") is not None or loc.get("longitude") is not None:
            raise ValueError("source=none requires null lat/lon")
    # size bound
    if len(json.dumps(body)) > 32_000:
        raise ValueError("payload too large")


@router.post("/v1/device-events")
def ingest_device_event(
    body: dict[str, Any],
    x_svaraa_tenant: str | None = Header(default=None, alias="X-Svaraa-Tenant"),
) -> dict[str, Any]:
    try:
        _validate_sos_created(body)
    except ValueError as e:
        raise HTTPException(422, {"error": str(e), "side_effects": False}) from e

    device_id = body["device_id"]
    if x_svaraa_tenant and x_svaraa_tenant != device_id:
        raise HTTPException(
            403,
            {"error": "wrong_tenant", "side_effects": False},
        )
    if not str(device_id).startswith(ALLOWED_DEVICE_PREFIX):
        raise HTTPException(
            403,
            {"error": "device_not_authorized_for_lab", "side_effects": False},
        )

    conn = get_product_conn()
    event_id = body["event_id"]
    existing = conn.execute(
        "SELECT event_id, body_sha256 FROM device_events WHERE event_id=?",
        (event_id,),
    ).fetchone()
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(raw.encode()).hexdigest()
    if existing:
        if existing["body_sha256"] == digest:
            return {
                "status": "duplicate",
                "event_id": event_id,
                "idempotent": True,
                "profile": "SIM",
                "notification_provider": "mock",
            }
        raise HTTPException(409, {"error": "event_id_conflict", "side_effects": False})

    now = _utc()
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            """
            INSERT INTO device_events(event_id, device_id, incident_id, kind, mode, body_json, body_sha256, created_at)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                event_id,
                device_id,
                body.get("incident_id"),
                body["kind"],
                body["mode"],
                raw,
                digest,
                now,
            ),
        )
        loc = (body.get("payload") or {}).get("location")
        conn.execute(
            """
            INSERT OR REPLACE INTO incidents(incident_id, device_id, mode, phase, revision, location_json, updated_at)
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                body["incident_id"],
                device_id,
                body["mode"],
                "ServerAccepted",
                1,
                json.dumps(loc),
                now,
            ),
        )
        conn.execute(
            """
            INSERT INTO outbox(event_id, incident_id, status, provider, attempts, created_at)
            VALUES (?,?,?,?,?,?)
            """,
            (event_id, body["incident_id"], "queued", "mock", 0, now),
        )
        # Drill must never dispatch to live provider (SV0-09.04 / 07.05)
        if body["mode"] == "drill":
            stage = "drill_suppressed"
            detail = "drill cannot dispatch to live provider"
        else:
            stage = "provider_submit"
            detail = "mock provider accepted submission (not human ACK)"
            conn.execute(
                "UPDATE outbox SET status='submitted', attempts=1 WHERE event_id=?",
                (event_id,),
            )
        conn.execute(
            """
            INSERT INTO notification_jobs(incident_id, stage, provider, detail, created_at)
            VALUES (?,?,?,?,?)
            """,
            (body["incident_id"], stage, "mock", detail, now),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise

    return {
        "status": "accepted",
        "event_id": event_id,
        "incident_id": body["incident_id"],
        "phase": "ServerAccepted",
        "revision": 1,
        "notification_provider": "mock",
        "notification_stage": stage,
        "profile": "SIM",
        "simulated": True,
        "note": "Provider submit ≠ human ACK.",
    }


class AckBody(BaseModel):
    actor: str = "guardian"
    message: str | None = None
    revision: int = Field(default=2, ge=2)
    action_id: str | None = None


@router.post("/v1/incidents/{incident_id}/ack")
def ack_incident(incident_id: str, body: AckBody) -> dict[str, Any]:
    conn = get_product_conn()
    action_id = body.action_id or str(uuid.uuid4())
    row = conn.execute(
        "SELECT * FROM incidents WHERE incident_id=?", (incident_id,)
    ).fetchone()
    if not row:
        _audit(
            conn,
            action_id=action_id,
            incident_id=incident_id,
            action="ack",
            actor=body.actor,
            expected_revision=body.revision,
            result="rejected_missing",
        )
        conn.commit()
        raise HTTPException(404, {"error": "incident not found", "optimistic_success": False})

    # Duplicate action_id
    prior = conn.execute(
        "SELECT * FROM human_actions WHERE action_id=?", (action_id,)
    ).fetchone()
    if prior:
        return {
            "incident_id": incident_id,
            "phase": row["phase"],
            "revision": row["revision"],
            "action_id": action_id,
            "idempotent": True,
            "result": prior["result"],
            "optimistic_success": False,
            "profile": "SIM",
        }

    if body.revision <= row["revision"]:
        _audit(
            conn,
            action_id=action_id,
            incident_id=incident_id,
            action="ack",
            actor=body.actor,
            expected_revision=body.revision,
            result="rejected_stale_revision",
            message="no optimistic false success",
        )
        conn.commit()
        raise HTTPException(
            409,
            {
                "error": "stale_revision",
                "optimistic_success": False,
                "action_id": action_id,
            },
        )

    now = _utc()
    conn.execute(
        "UPDATE incidents SET phase=?, revision=?, updated_at=? WHERE incident_id=?",
        ("HumanAck", body.revision, now, incident_id),
    )
    _audit(
        conn,
        action_id=action_id,
        incident_id=incident_id,
        action="ack",
        actor=body.actor,
        expected_revision=body.revision,
        result="accepted",
        message=body.message,
    )
    conn.execute(
        """
        INSERT INTO notification_jobs(incident_id, stage, provider, detail, created_at)
        VALUES (?,?,?,?,?)
        """,
        (
            incident_id,
            "human_ack",
            "mock",
            "human ACK distinct from provider submit",
            now,
        ),
    )
    conn.commit()
    return {
        "incident_id": incident_id,
        "phase": "HumanAck",
        "revision": body.revision,
        "actor": body.actor,
        "action_id": action_id,
        "message": body.message,
        "notification_provider": "mock",
        "profile": "SIM",
        "simulated": True,
        "optimistic_success": False,
        "note": "Human ACK is independent of provider submission.",
    }


class ResolveBody(BaseModel):
    actor: str = "guardian"
    revision: int = Field(ge=3)
    action_id: str | None = None
    message: str | None = None


@router.post("/v1/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: str, body: ResolveBody) -> dict[str, Any]:
    conn = get_product_conn()
    action_id = body.action_id or str(uuid.uuid4())
    row = conn.execute(
        "SELECT * FROM incidents WHERE incident_id=?", (incident_id,)
    ).fetchone()
    if not row:
        raise HTTPException(404, {"error": "incident not found", "optimistic_success": False})
    if body.revision <= row["revision"]:
        _audit(
            conn,
            action_id=action_id,
            incident_id=incident_id,
            action="resolve",
            actor=body.actor,
            expected_revision=body.revision,
            result="rejected_stale_revision",
        )
        conn.commit()
        raise HTTPException(409, {"error": "stale_revision", "optimistic_success": False})
    if row["phase"] not in ("HumanAck", "ServerAccepted"):
        _audit(
            conn,
            action_id=action_id,
            incident_id=incident_id,
            action="resolve",
            actor=body.actor,
            expected_revision=body.revision,
            result="rejected_phase",
        )
        conn.commit()
        raise HTTPException(409, {"error": "invalid_phase", "optimistic_success": False})
    now = _utc()
    conn.execute(
        "UPDATE incidents SET phase=?, revision=?, updated_at=? WHERE incident_id=?",
        ("Resolved", body.revision, now, incident_id),
    )
    _audit(
        conn,
        action_id=action_id,
        incident_id=incident_id,
        action="resolve",
        actor=body.actor,
        expected_revision=body.revision,
        result="accepted",
        message=body.message,
    )
    conn.commit()
    return {
        "incident_id": incident_id,
        "phase": "Resolved",
        "revision": body.revision,
        "action_id": action_id,
        "optimistic_success": False,
        "profile": "SIM",
        "simulated": True,
    }


@router.get("/v1/incidents/{incident_id}")
def get_incident(incident_id: str) -> dict[str, Any]:
    conn = get_product_conn()
    row = conn.execute(
        "SELECT * FROM incidents WHERE incident_id=?", (incident_id,)
    ).fetchone()
    if not row:
        raise HTTPException(404, "incident not found")
    d = dict(row)
    d["location"] = json.loads(d.pop("location_json") or "null")
    d["simulated"] = True
    return d


@router.get("/v1/incidents/{incident_id}/actions")
def list_actions(incident_id: str) -> dict[str, Any]:
    conn = get_product_conn()
    rows = conn.execute(
        "SELECT * FROM human_actions WHERE incident_id=? ORDER BY created_at",
        (incident_id,),
    ).fetchall()
    return {"actions": [dict(r) for r in rows], "profile": "SIM"}


@router.get("/v1/notifications")
def list_notifications(limit: int = 50) -> dict[str, Any]:
    conn = get_product_conn()
    rows = conn.execute(
        "SELECT * FROM notification_jobs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    return {
        "jobs": [dict(r) for r in rows],
        "provider": "mock",
        "note": "submit/delivery/human_ack stages remain distinct",
        "profile": "SIM",
    }


@router.get("/v1/incidents/{incident_id}/reconcile")
def reconcile(incident_id: str) -> dict[str, Any]:
    from .reconciliation import reconcile_incident

    return reconcile_incident(get_product_conn(), incident_id)


class ConsentBody(BaseModel):
    subject_id: str
    purpose: str
    granted: bool = True
    actor: str = "owner"


@router.post("/v1/consent")
def consent(body: ConsentBody) -> dict[str, Any]:
    from . import consent_audit

    conn = get_product_conn()
    result = consent_audit.set_consent(
        conn,
        subject_id=body.subject_id,
        purpose=body.purpose,
        granted=body.granted,
        actor=body.actor,
    )
    if not result.get("ok"):
        raise HTTPException(422, result)
    return {**result, "profile": "SIM"}


@router.post("/v1/consent/{subject_id}/revoke")
def consent_revoke(subject_id: str, actor: str = "owner") -> dict[str, Any]:
    from . import consent_audit

    return {
        **consent_audit.revoke_all(
            get_product_conn(), subject_id=subject_id, actor=actor
        ),
        "profile": "SIM",
    }


@router.get("/v1/consent/{subject_id}")
def consent_get(subject_id: str) -> dict[str, Any]:
    from . import consent_audit

    grants = consent_audit.latest_grants(get_product_conn(), subject_id)
    return {
        "subject_id": subject_id,
        "grants": grants,
        "ambient_audio_upload": False,
        "profile": "SIM",
    }
