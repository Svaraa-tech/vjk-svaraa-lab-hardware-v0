"""Hardware bench + sensor panel APIs (WB-006 / WB-007)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

_ROOT = Path(__file__).resolve().parents[3]
_SIM = _ROOT / "services"
if str(_SIM) not in sys.path:
    sys.path.insert(0, str(_SIM))

from simulator.engine import get_engine_store  # noqa: E402

router = APIRouter(prefix="/lab/v1", tags=["lab-hardware"])


def _pinmap() -> dict[str, Any]:
    path = _ROOT / "hardware" / "pinmap_sim.json"
    return json.loads(path.read_text())


@router.get("/hardware/pinmap")
def hardware_pinmap() -> dict[str, Any]:
    data = _pinmap()
    data["simulated"] = True
    data["note"] = "Proposed V0 design model for SIM visualization — not bench-measured."
    return data


@router.get("/hardware/bench")
def hardware_bench(run_id: str | None = None) -> dict[str, Any]:
    pinmap = _pinmap()
    eng = get_engine_store().get(run_id) if run_id else get_engine_store().latest()
    phase = eng.snapshot()["reducer"]["phase"] if eng else "Ready"
    # highlight nets by phase
    active_roles = {
        "Ready": [],
        "Prealert": ["manual_sos", "pixels"],
        "Pending": ["manual_sos", "pixels", "buzzer", "haptic"],
        "ServerAccepted": ["pixels", "buzzer", "haptic"],
        "HumanAck": ["pixels"],
        "Resolved": [],
    }.get(phase, [])
    nets = []
    for n in pinmap["nets"]:
        item = dict(n)
        item["active"] = n.get("role") in active_roles
        nets.append(item)
    return {
        "phase": phase,
        "power_domains": pinmap["power_domains"],
        "nets": nets,
        "parts": pinmap["parts"],
        "pixel_policy": pinmap["pixel_policy"],
        "run_id": eng.run_id if eng else None,
        "profile": "SIM",
        "simulated": True,
    }


@router.get("/hardware/sensors")
def hardware_sensors(run_id: str | None = None) -> dict[str, Any]:
    eng = get_engine_store().get(run_id) if run_id else get_engine_store().latest()
    if not eng:
        raise HTTPException(404, "no sim run — create /lab/v1/sim/runs first")
    # advance one sample for live feel
    eng.sensors.step(100)
    snap = eng.snapshot()
    return {
        "run_id": eng.run_id,
        "phase": snap["reducer"]["phase"],
        "sensors": snap["sensors"],
        "pixels": snap["pixels"],
        "alarm": snap["alarm"],
        "hold_model": snap["hold_model"],
        "profile": "SIM",
        "simulated": True,
        "clinical_claim": False,
    }
