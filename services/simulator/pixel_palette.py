"""Shared Lab ↔ Wokwi pixel palette (WB-019).

Indices follow `ux.PHASE_PIXEL`; RGB values are the Wokwi NeoPixel colors
used by firmware `showPhase` and the Device Simulator Wokwi panel.
"""
from __future__ import annotations

from typing import Any

# Must stay aligned with services/simulator/ux.py PHASE_PIXEL indices
# and simulation/wokwi/src/main.cpp showPhase().
PHASE_PIXEL_INDICES: dict[str, list[int]] = {
    "Ready": [0],
    "Prealert": [0, 1],
    "Pending": [0, 1, 2, 3, 4],
    "ServerAccepted": [0, 1, 2],
    "HumanAck": [0, 1, 2, 3, 4],
    "Resolved": [0],
}

PHASE_RGB: dict[str, tuple[int, int, int]] = {
    "Ready": (0, 20, 8),
    "Prealert": (40, 25, 0),
    "Pending": (50, 0, 0),
    "ServerAccepted": (40, 20, 0),
    "HumanAck": (0, 40, 0),
    "Resolved": (0, 0, 30),
}

PHASE_PATTERN: dict[str, str] = {
    "Ready": "idle_dim",
    "Prealert": "prealert_pulse",
    "Pending": "pending_chase",
    "ServerAccepted": "received_solid",
    "HumanAck": "human_ack_breathe",
    "Resolved": "resolved_fade",
}


def pixels_for_phase(phase: str) -> list[dict[str, Any]]:
    indices = set(PHASE_PIXEL_INDICES.get(phase, PHASE_PIXEL_INDICES["Ready"]))
    rgb = PHASE_RGB.get(phase, PHASE_RGB["Ready"])
    ready_dim = phase == "Ready"
    out: list[dict[str, Any]] = []
    for i in range(5):
        if i in indices:
            # Ready uses dim green on index 0 only (matches PixelModel 0.2 level)
            c = (0, 8, 3) if ready_dim else rgb
            out.append({"id": f"px{i}", "rgb": list(c), "on": True, "index": i})
        else:
            out.append({"id": f"px{i}", "rgb": [0, 0, 0], "on": False, "index": i})
    return out


def fidelity_report() -> dict[str, Any]:
    """Compare palette indices to ux.PHASE_PIXEL (import soft)."""
    try:
        from simulator.ux import PHASE_PIXEL  # type: ignore
    except Exception as e:  # pragma: no cover
        return {"ok": False, "error": str(e)}
    mismatches = []
    for phase, cfg in PHASE_PIXEL.items():
        expected = list(cfg["indices"])
        actual = PHASE_PIXEL_INDICES.get(phase)
        if actual != expected:
            mismatches.append({"phase": phase, "ux": expected, "palette": actual})
        if PHASE_PATTERN.get(phase) != cfg.get("pattern"):
            mismatches.append(
                {
                    "phase": phase,
                    "pattern_ux": cfg.get("pattern"),
                    "pattern_palette": PHASE_PATTERN.get(phase),
                }
            )
    return {
        "ok": not mismatches,
        "mismatches": mismatches,
        "phases": list(PHASE_PIXEL_INDICES.keys()),
        "evidence_profile": "Wokwi",
    }
