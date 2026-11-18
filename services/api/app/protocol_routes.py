"""Protocol inspector + scenarios + app previews (WB-008/009/010)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

_ROOT = Path(__file__).resolve().parents[3]
_SIM = _ROOT / "services"
if str(_SIM) not in sys.path:
    sys.path.insert(0, str(_SIM))

from simulator.engine import get_engine_store, project_scenarios  # noqa: E402
from simulator.protocol import (  # noqa: E402
    BleAssembler,
    decode_frame,
    decode_mailbox,
    encode_imu,
    mailbox_frame,
)

router = APIRouter(prefix="/lab/v1", tags=["lab-protocol"])


@router.get("/protocol/journey")
def protocol_journey(run_id: str | None = None) -> dict[str, Any]:
    eng = get_engine_store().get(run_id) if run_id else get_engine_store().latest()
    if not eng:
        raise HTTPException(404, "no run")
    # correlate with reducer trace
    return {
        "run_id": eng.run_id,
        "phase": eng.snapshot()["reducer"]["phase"],
        "packets": eng.protocol.journey(),
        "engine_trace": eng.trace()[-40:],
        "rules": {
            "att_ack_is_not_caregiver_ack": True,
            "att_ack_is_not_server_receipt": True,
            "mtu": 23,
        },
        "profile": "SIM",
        "simulated": True,
    }


@router.post("/protocol/sample")
def protocol_sample(run_id: str | None = None) -> dict[str, Any]:
    eng = get_engine_store().get(run_id) if run_id else get_engine_store().latest()
    if not eng:
        raise HTTPException(404, "no run")
    return eng.inject_protocol_sample()


class PrivacyBody(BaseModel):
    physical: bool | None = None
    remote_mute: bool | None = None


@router.post("/sim/runs/{run_id}/privacy")
def privacy(run_id: str, body: PrivacyBody) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, "run not found")
    if body.physical is not None:
        return eng.set_privacy_physical(body.physical)
    if body.remote_mute is not None:
        return eng.set_privacy_remote(body.remote_mute)
    raise HTTPException(422, "physical or remote_mute required")


class GestureBody(BaseModel):
    action: str
    voice_only: bool = False


@router.post("/sim/runs/{run_id}/gesture")
def gesture(run_id: str, body: GestureBody) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, "run not found")
    return eng.gesture(body.action, voice_only=body.voice_only)


class FaultBody(BaseModel):
    name: str
    enabled: bool = True


@router.post("/sim/runs/{run_id}/faults")
def faults(run_id: str, body: FaultBody) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, "run not found")
    snap = eng.set_fault(body.name, body.enabled)
    # WB-035 — annotate Wokwi serial when comm faults flip
    if body.name in {"drop_ble", "drop_response"}:
        eng._emit(
            "wokwi",
            "comm_fault",
            {
                "fault": body.name,
                "enabled": body.enabled,
                "proxy_for": "SV0-11.03",
                "simulated": True,
            },
        )
    return {
        **snap,
        "faults": snap.get("faults") or eng.snapshot().get("faults"),
        "proxy_for": "SV0-11.03",
    }


@router.get("/scenarios")
def scenarios() -> dict[str, Any]:
    return {
        "scenarios": project_scenarios(),
        "faults_available": ["drop_ble", "drop_response", "assistant_audio_fail"],
        "profile": "SIM",
    }


@router.get("/evidence/export")
def evidence_export(run_id: str | None = None) -> PlainTextResponse:
    eng = get_engine_store().get(run_id) if run_id else get_engine_store().latest()
    if not eng:
        raise HTTPException(404, "no run")
    payload = {
        "run": eng.snapshot(),
        "trace": eng.trace(),
        "protocol": eng.protocol.journey(),
        "profile": "SIM",
        "notification_provider": "mock",
    }
    return PlainTextResponse(
        json.dumps(payload, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="svaraa_run_evidence.json"'},
    )


@router.get("/evidence/trace-pack")
def evidence_trace_pack(run_id: str | None = None) -> PlainTextResponse:
    """WB-034 — deterministic JSONL trace pack (proxy SV0-11.02)."""
    eng = get_engine_store().get(run_id) if run_id else get_engine_store().latest()
    if not eng:
        raise HTTPException(404, "no run")
    snap = eng.snapshot()
    events = sorted(
        eng.trace(),
        key=lambda e: (e.get("sim_ts_ms", 0), e.get("seq", 0), e.get("layer", ""), e.get("kind", "")),
    )
    meta = {
        "type": "svaraa_trace_pack",
        "schema_version": "1",
        "run_id": eng.run_id,
        "scenario_id": snap.get("scenario_id"),
        "seed": snap.get("seed"),
        "phase": snap["reducer"]["phase"],
        "event_count": len(events),
        "profile": "SIM",
        "proxy_for": "SV0-11.02",
        "deterministic": True,
    }
    lines = [json.dumps(meta, sort_keys=True, separators=(",", ":"))]
    for ev in events:
        lines.append(json.dumps(ev, sort_keys=True, separators=(",", ":")))
    body = "\n".join(lines) + "\n"
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    # trailer with pack hash (excluded from prior lines so clients can verify body[:-1])
    body_with_hash = body + json.dumps(
        {"type": "pack_sha256", "sha256": digest, "bytes": len(body.encode("utf-8"))},
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"
    fname = f"svaraa-trace-{eng.run_id[:8]}-{digest[:8]}.jsonl"
    return PlainTextResponse(
        body_with_hash,
        media_type="application/x-ndjson",
        headers={
            "Content-Disposition": f'attachment; filename="{fname}"',
            "X-Svaraa-Trace-Pack-Sha256": digest,
        },
    )


@router.get("/apps/previews")
def app_previews() -> dict[str, Any]:
    """Wearer/guardian web previews with ticket cross-links (WB-009)."""
    return {
        "profile": "SIM",
        "simulated": True,
        "previews": [
            {
                "role": "wearer",
                "title": "Wearer status",
                "copy": "Shows phase, privacy pending/applied, and local alarm — never invents GPS.",
                "tickets": ["SV0-S10", "SV0-05.02", "SV0-05.04", "WB-009", "WB-039"],
                "fields": ["phase", "pixels.pattern", "privacy.effective", "alarm.buzzer_on"],
            },
            {
                "role": "guardian",
                "title": "Guardian inbox (mock)",
                "copy": "Provider submit ≠ human ACK. ACK is an explicit action.",
                "tickets": ["SV0-S10", "SV0-09.03", "SV0-09.04", "WB-009"],
                "fields": ["incident_id", "phase", "notification_stage"],
            },
        ],
        "latest_run": (
            get_engine_store().latest().snapshot() if get_engine_store().latest() else None
        ),
    }


@router.get("/apps/wearer")
def wearer_dashboard(run_id: str | None = None) -> dict[str, Any]:
    """WB-039 — live wearer dashboard wireframe payload (proxy SV0-10.01)."""
    eng = get_engine_store().get(run_id) if run_id else get_engine_store().latest()
    if not eng:
        return {
            "ok": False,
            "reason": "no_run",
            "wireframe": True,
            "profile": "SIM",
            "proxy_for": "SV0-10.01",
        }
    snap = eng.snapshot()
    loc = snap.get("location") or {}
    return {
        "ok": True,
        "wireframe": True,
        "run_id": eng.run_id,
        "phase": snap["reducer"]["phase"],
        "mode": snap["reducer"]["mode"],
        "incident_id": snap["reducer"].get("incident_id"),
        "pixels": snap.get("pixels"),
        "alarm": snap.get("alarm"),
        "privacy": snap.get("privacy"),
        "location": {
            "valid": (loc.get("fix") or loc).get("valid")
            if isinstance(loc, dict)
            else None,
            "honest": "never invent GPS — null/invalid shown as-is",
        },
        "copy": {
            "title": "Wearer status",
            "subtitle": "SIM wireframe · local alarm independent of assistant",
        },
        "tickets": ["SV0-10.01", "WB-039", "WB-009"],
        "profile": "SIM",
        "simulated": True,
        "proxy_for": "SV0-10.01",
    }


@router.get("/evidence/report.md")
def evidence_report_md(run_id: str | None = None) -> PlainTextResponse:
    """WB-038 — markdown evidence report aggregator (proxy SV0-11.06)."""
    from . import board_db
    from .board_routes import get_conn

    eng = get_engine_store().get(run_id) if run_id else get_engine_store().latest()
    root = board_db.project_root()
    lines = [
        "# Svaraa V0 Lab — evidence report",
        "",
        "_Generated SIM report · proxy SV0-11.06 · profile=SIM_",
        "",
    ]
    if eng:
        snap = eng.snapshot()
        lines.extend(
            [
                "## Active run",
                "",
                f"- **run_id:** `{eng.run_id}`",
                f"- **scenario:** `{snap.get('scenario_id')}`",
                f"- **seed:** `{snap.get('seed')}`",
                f"- **phase:** {snap['reducer']['phase']}",
                f"- **trace events:** {len(eng.trace())}",
                f"- **journal:** {snap.get('journal_count')}",
                "",
            ]
        )
    else:
        lines.extend(["## Active run", "", "_No run in memory._", ""])

    # firmware pins
    fw_paths = (
        list((root / "evidence").glob("**/firmware.bin"))
        if (root / "evidence").is_dir()
        else []
    )
    lines.extend(["## Firmware artifacts", ""])
    if fw_paths:
        for p in sorted(fw_paths)[:20]:
            data = p.read_bytes()
            sha = hashlib.sha256(data).hexdigest()[:12]
            lines.append(
                f"- `{p.relative_to(root).as_posix()}` · sha `{sha}…` · {len(data)} B"
            )
    else:
        lines.append("_No firmware.bin under evidence/._")
    lines.append("")

    # workbench ticket evidence counts
    conn = get_conn()
    cur = conn.execute(
        "SELECT ticket_key, workflow_state FROM tickets WHERE source_namespace='workbench' ORDER BY ticket_key"
    )
    rows = cur.fetchall()
    lines.extend(
        [
            "## Workbench tickets",
            "",
            "| Ticket | State | Evidence files |",
            "| --- | --- | ---: |",
        ]
    )
    for key, state in rows:
        ev_dir = root / "evidence" / key
        count = 0
        if ev_dir.is_dir():
            count = sum(1 for _ in ev_dir.rglob("*") if _.is_file())
        lines.append(f"| {key} | {state} | {count} |")
    lines.extend(
        [
            "",
            "---",
            "",
            "_Lab engine remains SOS authority · Wokwi visual subset only._",
            "",
        ]
    )
    body = "\n".join(lines)
    return PlainTextResponse(
        body,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="svaraa_evidence_report.md"'
        },
    )


@router.get("/protocol/codecs/selftest")
def codec_selftest() -> dict[str, Any]:
    raw = encode_imu(1, 100, [1, 2, 3, 4, 5, 6])
    decoded = decode_frame(raw)
    mb = mailbox_frame(1, 1, 1)
    mbd = decode_mailbox(mb)
    ble = BleAssembler()
    frags = ble.fragment(7, 1, b"hello-svaraa")
    result = None
    for f in frags:
        result = ble.accept(f)
    # malformed
    errors = []
    try:
        decode_frame(b"\x00" * 16)
    except ValueError as e:
        errors.append(str(e))
    try:
        BleAssembler().accept(b"short")
    except ValueError as e:
        errors.append(str(e))
    return {
        "imu": decoded,
        "mailbox": mbd,
        "ble": result,
        "malformed_caught": errors,
        "mute_silently_disables_motion": False,
        "profile": "SIM",
    }
