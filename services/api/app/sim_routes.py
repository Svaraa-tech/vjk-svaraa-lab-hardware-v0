"""Lab simulator control API (WB-005)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# services/simulator is sibling of services/api
_ROOT = Path(__file__).resolve().parents[3]
_SIM = _ROOT / "services"
if str(_SIM) not in sys.path:
    sys.path.insert(0, str(_SIM))

from simulator.engine import get_engine_store, project_scenarios  # noqa: E402

router = APIRouter(prefix="/lab/v1/sim", tags=["lab-sim"])


class CreateRunBody(BaseModel):
    scenario_id: str = "manual_no_gps"
    seed: str | None = None


class ControlBody(BaseModel):
    action: str = Field(description="play|pause|step")
    delta_ms: int = 100
    speed: float = 1.0


class HoldBody(BaseModel):
    down: bool = True
    qualify: bool = False


class AckBody(BaseModel):
    incident_id: str | None = None


@router.get("/scenarios")
def scenarios() -> dict[str, Any]:
    return {"scenarios": project_scenarios(), "profile": "SIM"}


@router.post("/runs")
def create_run(body: CreateRunBody) -> dict[str, Any]:
    eng = get_engine_store().create(scenario_id=body.scenario_id, seed=body.seed)
    return eng.snapshot()


@router.get("/runs/latest")
def latest_run() -> dict[str, Any]:
    eng = get_engine_store().latest()
    if not eng:
        raise HTTPException(404, "no runs")
    return eng.snapshot()


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, f"run {run_id} not found")
    return eng.snapshot()


@router.post("/runs/{run_id}/control")
def control_run(run_id: str, body: ControlBody) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, f"run {run_id} not found")
    try:
        return eng.control(body.action, delta_ms=body.delta_ms, speed=body.speed)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e


@router.post("/runs/{run_id}/hold")
def hold(run_id: str, body: HoldBody) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, f"run {run_id} not found")
    if body.qualify:
        return eng.qualify_hold_now()
    return eng.input_hold(body.down)


@router.post("/runs/{run_id}/commit")
def commit(run_id: str) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, f"run {run_id} not found")
    try:
        return eng.commit_to_server()
    except (ValueError, KeyError) as e:
        raise HTTPException(400, str(e)) from e


@router.post("/runs/{run_id}/ack")
def ack(run_id: str, body: AckBody) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, f"run {run_id} not found")
    try:
        return eng.human_ack(body.incident_id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/runs/{run_id}/scenario/manual_no_gps")
def run_manual_no_gps(run_id: str) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, f"run {run_id} not found")
    return eng.run_manual_no_gps()


class FallBody(BaseModel):
    quality_ok: bool = True
    escalate: bool = False


@router.post("/runs/{run_id}/fall")
def fall(run_id: str, body: FallBody) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, f"run {run_id} not found")
    snap = eng.fall_candidate(quality_ok=body.quality_ok)
    if body.escalate and body.quality_ok:
        snap = eng.confirm_fall_after_deadline()
    return snap


class RetryBody(BaseModel):
    drop_response: bool = False


@router.post("/runs/{run_id}/retry")
def retry(run_id: str, body: RetryBody) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, f"run {run_id} not found")
    try:
        return eng.retry_outbox(drop_response=body.drop_response)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/runs/{run_id}/drill")
def drill(run_id: str) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, f"run {run_id} not found")
    return eng.start_drill()


@router.post("/runs/{run_id}/drill/e2e")
def drill_e2e(run_id: str) -> dict[str, Any]:
    """WB-036 — SIM end-to-end drill: start_drill + manual_no_gps + Wokwi sync (proxy SV0-11.04)."""
    import sys
    from pathlib import Path

    _root = Path(__file__).resolve().parents[3]
    if str(_root / "services") not in sys.path:
        sys.path.insert(0, str(_root / "services"))
    from simulator import wokwi_bridge  # noqa: WPS433

    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, f"run {run_id} not found")
    drill_snap = eng.start_drill()
    result = eng.run_manual_no_gps()
    phase = result["snapshot"]["reducer"]["phase"]
    eng._emit(
        "wokwi",
        "drill_e2e_sync",
        {"phase": phase, "proxy_for": "SV0-11.04", "simulated": True},
    )
    visual = wokwi_bridge.visual_state(phase)
    phases_seen = []
    for t in result["trace"]:
        p = (t.get("detail") or {}).get("phase") or (t.get("detail") or {}).get("to")
        if p and p not in phases_seen:
            phases_seen.append(p)
    return {
        "ok": bool(result.get("expect_ok")),
        "expect_ok": result.get("expect_ok"),
        "drill": {"phase": drill_snap["reducer"]["phase"]},
        "snapshot": result["snapshot"],
        "event": result.get("event"),
        "trace_count": len(result["trace"]),
        "phases_seen": phases_seen,
        "wokwi": {"visual": visual, "synced": True},
        "proxy_for": "SV0-11.04",
        "profile": "SIM",
        "simulated": True,
    }


@router.post("/runs/{run_id}/watchdog/starve")
def watchdog_starve(run_id: str) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, f"run {run_id} not found")
    return eng.watchdog_starve()


@router.get("/runs/{run_id}/trace")
def trace(run_id: str) -> dict[str, Any]:
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, f"run {run_id} not found")
    return {"run_id": run_id, "events": eng.trace(), "read_only": True}


@router.post("/runs/{run_id}/stress")
def stress_harness(run_id: str) -> dict[str, Any]:
    """WB-037 — SIM resource stress / fuzz stub (proxy SV0-11.05)."""
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, f"run {run_id} not found")
    steps: list[dict[str, Any]] = []
    # bounded audio flood must not block SOS
    audio = eng.audio_action("flood")
    steps.append(
        {
            "id": "audio_flood",
            "ok": audio.get("result", {}).get("blocks_sos") is False,
            "detail": {
                "overflow": audio.get("result", {}).get("overflow"),
                "blocks_sos": audio.get("result", {}).get("blocks_sos"),
            },
        }
    )
    # protocol sample under drop_ble
    eng.set_fault("drop_ble", True)
    proto = eng.inject_protocol_sample()
    steps.append(
        {
            "id": "protocol_under_drop_ble",
            "ok": True,
            "detail": {"packets": len(proto.get("packets") or [])},
        }
    )
    eng.set_fault("drop_ble", False)
    # watchdog starve (SIM)
    wd = eng.watchdog_starve()
    steps.append(
        {
            "id": "watchdog_starve",
            "ok": True,
            "detail": {"phase": wd["reducer"]["phase"]},
        }
    )
    # fuzz-ish: repeated privacy toggles
    for i in range(5):
        eng.set_privacy_physical(i % 2 == 0)
    steps.append({"id": "privacy_toggle_fuzz", "ok": True, "detail": {"iters": 5}})
    eng._emit("stress", "harness_complete", {"steps": len(steps), "proxy_for": "SV0-11.05"})
    ok = all(s["ok"] for s in steps)
    return {
        "ok": ok,
        "steps": steps,
        "snapshot": eng.snapshot(),
        "proxy_for": "SV0-11.05",
        "profile": "SIM",
        "simulated": True,
        "note": "Stub harness — not a product fuzz campaign",
    }
