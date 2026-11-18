from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from . import board_db
from . import ticket_dossier

router = APIRouter(prefix="/lab/v1", tags=["lab-board"])

_conn = None


def get_conn():
    global _conn
    if _conn is None:
        _conn = board_db.connect()
        board_db.init_schema(_conn)
        board_db.import_bootstrap(_conn, force=False)
    return _conn


class TransitionBody(BaseModel):
    to_state: str
    actor: str = "agent"
    message: str | None = None
    blocked_reason: str | None = None
    force: bool = False


class DecisionBody(BaseModel):
    decision: str
    actor: str = "owner"
    message: str | None = None
    plan_revision: str | None = None
    evidence_revision: str | None = None
    ticket_key: str | None = None


class UpsertBody(BaseModel):
    workflow_state: str | None = None
    implementation_state: str | None = None
    owner_acceptance: str | None = None
    plan_revision: str | None = None
    actor: str = "agent"
    message: str | None = None


@router.post("/board/import")
def board_import(force: bool = False) -> dict[str, Any]:
    return board_db.import_bootstrap(get_conn(), force=force)


@router.get("/board/summary")
def board_summary() -> dict[str, Any]:
    return board_db.summary(get_conn())


@router.get("/tickets")
def tickets(
    namespace: str | None = None,
    work_type: str | None = None,
    state: str | None = None,
    q: str | None = Query(None, description="Search key/summary"),
) -> dict[str, Any]:
    items = board_db.list_tickets(
        get_conn(), namespace=namespace, work_type=work_type, state=state, q=q
    )
    return {"count": len(items), "tickets": items}


@router.get("/tickets/{ticket_key}")
def ticket_detail(ticket_key: str) -> dict[str, Any]:
    t = board_db.get_ticket(get_conn(), ticket_key)
    if not t:
        raise HTTPException(404, f"ticket {ticket_key} not found")
    return t


@router.get("/tickets/{ticket_key}/dossier")
def ticket_dossier_detail(ticket_key: str) -> dict[str, Any]:
    """Full task / execution / results modal payload for any ticket."""
    d = ticket_dossier.build_dossier(get_conn(), ticket_key)
    if not d:
        raise HTTPException(404, f"ticket {ticket_key} not found")
    return d


@router.post("/tickets/{ticket_key}/transition")
def ticket_transition(ticket_key: str, body: TransitionBody) -> dict[str, Any]:
    try:
        return board_db.transition(
            get_conn(),
            ticket_key,
            body.to_state,
            actor=body.actor,
            message=body.message,
            blocked_reason=body.blocked_reason,
            force=body.force,
        )
    except KeyError:
        raise HTTPException(404, f"ticket {ticket_key} not found") from None
    except PermissionError as e:
        raise HTTPException(409, str(e)) from e
    except ValueError as e:
        raise HTTPException(422, str(e)) from e


@router.patch("/tickets/{ticket_key}")
def ticket_upsert(ticket_key: str, body: UpsertBody) -> dict[str, Any]:
    conn = get_conn()
    t = board_db.get_ticket(conn, ticket_key)
    if not t:
        raise HTTPException(404, f"ticket {ticket_key} not found")
    if body.workflow_state and body.workflow_state != t["workflow_state"]:
        try:
            board_db.transition(
                conn,
                ticket_key,
                body.workflow_state,
                actor=body.actor,
                message=body.message,
                force=True,  # agent progress under batch auth
            )
        except Exception as e:
            raise HTTPException(400, str(e)) from e
    fields = []
    args: list[Any] = []
    if body.implementation_state is not None:
        fields.append("implementation_state=?")
        args.append(body.implementation_state)
    if body.owner_acceptance is not None:
        fields.append("owner_acceptance=?")
        args.append(body.owner_acceptance)
    if body.plan_revision is not None:
        fields.append("plan_revision=?")
        args.append(body.plan_revision)
    if fields:
        fields.append("updated_at=?")
        args.append(board_db.utc_now())
        args.append(ticket_key)
        conn.execute(
            f"UPDATE tickets SET {', '.join(fields)} WHERE ticket_key=?",
            args,
        )
        conn.commit()
    return board_db.get_ticket(conn, ticket_key)  # type: ignore


@router.post("/decisions")
def create_decision(body: DecisionBody) -> dict[str, Any]:
    return board_db.record_decision(
        get_conn(),
        ticket_key=body.ticket_key,
        decision=body.decision,
        actor=body.actor,
        message=body.message,
        plan_revision=body.plan_revision,
        evidence_revision=body.evidence_revision,
    )


@router.get("/decisions")
def list_decisions(limit: int = 50) -> dict[str, Any]:
    rows = get_conn().execute(
        "SELECT * FROM decisions ORDER BY id DESC LIMIT ?", (limit,)
    )
    return {"decisions": [dict(r) for r in rows]}


@router.get("/board/provenance")
def board_provenance() -> dict[str, Any]:
    return board_db.provenance(get_conn())


@router.get("/board/export.csv")
def tickets_export_csv():
    from fastapi.responses import PlainTextResponse

    body = board_db.export_csv(get_conn())
    return PlainTextResponse(
        body,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="svaraa_board.csv"'},
    )


@router.get("/gallery")
def reference_gallery() -> dict[str, Any]:
    """Document/diagram gallery for WB-002 (pack references under Lab)."""
    import hashlib
    from pathlib import Path

    root = board_db.project_root()
    pack = root / "references/agent-pack/Svaraa_V0_Engineer_Agent_Pack"
    items: list[dict[str, Any]] = []
    for rel, kind in (
        ("diagrams", "diagram"),
        ("docs", "document"),
        ("jira", "jira"),
        ("contracts", "contract"),
    ):
        base = pack / rel
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {
                ".svg",
                ".pdf",
                ".md",
                ".csv",
                ".json",
                ".yaml",
                ".yml",
                ".dot",
            }:
                continue
            items.append(
                {
                    "id": path.relative_to(pack).as_posix(),
                    "title": path.name,
                    "kind": kind,
                    "path": path.relative_to(root).as_posix(),
                    "ext": path.suffix.lower().lstrip("."),
                }
            )
    # Lab-local docs
    for path in sorted((root / "docs").rglob("*.md")):
        items.append(
            {
                "id": f"lab/{path.relative_to(root / 'docs').as_posix()}",
                "title": path.name,
                "kind": "lab-doc",
                "path": path.relative_to(root).as_posix(),
                "ext": "md",
            }
        )

    # WB-027 — firmware artifacts (build + evidence copies) with hash thumbs
    def _fw_item(path: Path, *, source: str) -> dict[str, Any] | None:
        if not path.is_file():
            return None
        data = path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        rel = path.relative_to(root).as_posix()
        return {
            "id": f"firmware/{rel}",
            "title": path.name,
            "kind": "firmware",
            "path": rel,
            "ext": "bin",
            "bytes": len(data),
            "sha256": sha,
            "sha12": sha[:12],
            "source": source,
            "thumb": {
                "label": f"FW {sha[:8]}",
                "subtitle": f"{len(data)} B · {source}",
                "tone": "firmware",
            },
        }

    # WB-032 — keep distinct paths (same sha OK) so thumbs can compare identical builds
    seen_path: set[str] = set()
    for cand, src in (
        (root / "simulation/wokwi/.pio/build/sim/firmware.bin", "pio-build"),
        (root / "evidence/WB-023/latest/firmware.bin", "evidence-WB-023"),
    ):
        item = _fw_item(cand, source=src)
        if not item or item["path"] in seen_path:
            continue
        seen_path.add(item["path"])
        items.append(item)
    evidence_root = root / "evidence"
    if evidence_root.is_dir():
        for path in sorted(evidence_root.glob("**/firmware.bin")):
            item = _fw_item(
                path, source=f"evidence-{path.relative_to(evidence_root).parts[0]}"
            )
            if not item or item["path"] in seen_path:
                continue
            seen_path.add(item["path"])
            items.append(item)

    return {"count": len(items), "items": items, "profile": "SIM"}
