"""Wokwi project + visual sync API (SV0-11.01 / WB-011–024)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT / "services") not in sys.path:
    sys.path.insert(0, str(_ROOT / "services"))

from simulator.engine import get_engine_store  # noqa: E402
from simulator import wokwi_bridge  # noqa: E402

router = APIRouter(prefix="/lab/v1/wokwi", tags=["lab-wokwi"])


@router.get("/status")
def wokwi_status() -> dict[str, Any]:
    return wokwi_bridge.project_status()


@router.get("/diagram")
def wokwi_diagram() -> dict[str, Any]:
    try:
        diagram = wokwi_bridge.load_diagram()
    except FileNotFoundError as e:
        raise HTTPException(404, "diagram.json missing") from e
    return {
        "diagram": diagram,
        "gpio_map": wokwi_bridge.gpio_map(),
        "open": wokwi_bridge.open_links(),
        "simulated": True,
        "evidence_profile": "Wokwi",
    }


@router.get("/open")
def wokwi_open() -> dict[str, Any]:
    """WB-015/022 — open-in-Wokwi / VS Code / optional elements embed."""
    return {
        **wokwi_bridge.open_links(),
        "profile": "SIM",
        "simulated": True,
        "evidence_profile": "Wokwi",
    }


@router.get("/embed")
def wokwi_embed() -> dict[str, Any]:
    """WB-022 — embed readiness from embed.json (null project_id = local only)."""
    cfg = wokwi_bridge.load_embed_config()
    links = wokwi_bridge.open_links()["elements_embed"]
    return {
        "config": cfg,
        "elements_embed": links,
        "profile": "SIM",
        "simulated": True,
        "evidence_profile": "Wokwi",
    }


def _serial_payload(run_id: str | None = None, limit: int = 80) -> dict[str, Any]:
    eng = get_engine_store().get(run_id) if run_id else get_engine_store().latest()
    lines: list[dict[str, Any]] = []
    phase = "Ready"
    run = None
    if eng:
        snap = eng.snapshot()
        phase = snap["reducer"]["phase"]
        run = eng.run_id
        visual = wokwi_bridge.visual_state(
            phase, hold_down=bool(snap.get("hold", {}).get("down"))
        )
        for raw in visual["serial_lines"]:
            lines.append(
                {
                    "ts_ms": snap["clock"]["monotonic_ms"],
                    "source": "bridge",
                    "text": raw,
                }
            )
        for t in eng.traces:
            if t.layer == "wokwi" or str(t.kind).startswith("sync"):
                lines.append(
                    {
                        "ts_ms": t.sim_ts_ms,
                        "source": t.layer,
                        "text": json.dumps({"type": t.kind, **(t.detail or {})}),
                    }
                )
    else:
        for raw in wokwi_bridge.visual_state(phase)["serial_lines"]:
            lines.append({"ts_ms": 0, "source": "bridge", "text": raw})
    return {
        "run_id": run,
        "phase": phase,
        "lines": lines[-max(1, min(limit, 500)) :],
        "profile": "SIM",
        "simulated": True,
        "evidence_profile": "Wokwi",
    }


@router.get("/serial")
def wokwi_serial(run_id: str | None = None, limit: int = 80) -> dict[str, Any]:
    """WB-024 — serial-style lines from engine phase + wokwi sync traces."""
    return _serial_payload(run_id, limit)


@router.get("/serial/export")
def wokwi_serial_export(run_id: str | None = None, limit: int = 500):
    """WB-031 — downloadable JSONL of serial console lines."""
    from fastapi.responses import PlainTextResponse

    payload = _serial_payload(run_id, limit)
    meta = {
        "type": "wokwi_serial_export",
        "run_id": payload["run_id"],
        "phase": payload["phase"],
        "profile": "SIM",
        "evidence_profile": "Wokwi",
        "line_count": len(payload["lines"]),
    }
    body_lines = [json.dumps(meta, separators=(",", ":"))]
    for line in payload["lines"]:
        body_lines.append(json.dumps(line, separators=(",", ":")))
    fname = f"wokwi-serial-{(payload['run_id'] or 'norun')[:8]}.jsonl"
    return PlainTextResponse(
        "\n".join(body_lines) + "\n",
        media_type="application/x-ndjson",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@router.get("/phases")
def wokwi_phases() -> dict[str, Any]:
    """WB-025 — scenario phase catalog for Wokwi panel stepper."""
    return {
        **wokwi_bridge.phase_catalog(),
        "profile": "SIM",
        "simulated": True,
    }


@router.post("/preview")
def wokwi_preview(
    phase: str = Query("Ready"),
    run_id: str | None = None,
) -> dict[str, Any]:
    """WB-025 — visual-only phase preview (does not mutate Lab SOS reducer)."""
    catalog = wokwi_bridge.phase_catalog()
    if phase not in catalog["phases"]:
        raise HTTPException(400, f"unknown phase; choose one of {catalog['phases']}")
    eng = get_engine_store().get(run_id) if run_id else get_engine_store().latest()
    engine_phase = None
    run = None
    if eng:
        snap = eng.snapshot()
        engine_phase = snap["reducer"]["phase"]
        run = eng.run_id
        eng._emit(
            "wokwi",
            "phase_preview",
            {
                "phase": phase,
                "annotation": wokwi_bridge.PHASE_ANNOTATIONS.get(phase),
                "engine_phase": engine_phase,
                "preview": True,
            },
        )
    visual = wokwi_bridge.visual_state(phase, preview=True)
    return {
        "ok": True,
        "run_id": run,
        "preview_phase": phase,
        "engine_phase": engine_phase,
        "visual": visual,
        "serial_cmd": {
            "cmd": "phase_preview",
            "phase": phase,
            "annotation": visual.get("annotation"),
            "authority": "visual_subset_only",
        },
        "note": "Preview does not change Lab engine SOS state — Sync from engine to restore",
        "profile": "SIM",
        "simulated": True,
        "evidence_profile": "Wokwi",
    }


@router.get("/doctor")
def wokwi_doctor() -> dict[str, Any]:
    """WB-017 — PlatformIO + firmware hash + fidelity."""
    return wokwi_bridge.doctor()


@router.get("/fidelity")
def wokwi_fidelity() -> dict[str, Any]:
    """WB-019 — Lab engine pixel indices vs Wokwi palette."""
    return wokwi_bridge.fidelity_report()


@router.post("/smoke")
def wokwi_smoke(run_pio: bool = Query(False)) -> dict[str, Any]:
    """WB-020 — headless PIO/firmware smoke (pio optional via query)."""
    return wokwi_bridge.headless_smoke(run_pio=run_pio)


@router.get("/view")
def wokwi_view(run_id: str | None = None) -> dict[str, Any]:
    """Combined payload for Device Simulator Wokwi panel."""
    eng = get_engine_store().get(run_id) if run_id else get_engine_store().latest()
    phase = "Ready"
    hold_down = False
    run = None
    if eng:
        snap = eng.snapshot()
        phase = snap["reducer"]["phase"]
        hold_down = bool(snap.get("hold", {}).get("down"))
        run = eng.run_id
    visual = wokwi_bridge.visual_state(phase, hold_down=hold_down)
    return {
        "run_id": run,
        "status": wokwi_bridge.project_status(),
        "diagram": wokwi_bridge.load_diagram(),
        "gpio_map": wokwi_bridge.gpio_map(),
        "visual": visual,
        "open": wokwi_bridge.open_links(),
        "sync": {
            "source_of_truth": "lab_engine",
            "wokwi_role": "visual_subset",
            "mirrored_fields": ["phase", "pixels", "button", "pattern"],
        },
        "limits_banner": {
            "text": "Wokwi subset · no BLE · no I2S · no Nicla target · evidence_profile=Wokwi",
            "ble": False,
            "i2s": False,
            "nicla_target": False,
        },
        "profile": "SIM",
        "simulated": True,
    }


@router.post("/sync/{run_id}")
def wokwi_sync(run_id: str) -> dict[str, Any]:
    """Push current engine phase into visual state (and log serial-style line)."""
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, "run not found")
    snap = eng.snapshot()
    phase = snap["reducer"]["phase"]
    eng._emit("wokwi", "sync_phase", {"phase": phase})
    return {
        "ok": True,
        "visual": wokwi_bridge.visual_state(
            phase, hold_down=bool(snap.get("hold", {}).get("down"))
        ),
        "serial_cmd": {"cmd": "phase", "phase": phase},
    }
