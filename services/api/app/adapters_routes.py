"""Location / audio / link adapter APIs (SV0-04 / 06 / 08.05)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT / "services") not in sys.path:
    sys.path.insert(0, str(_ROOT / "services"))

from simulator.engine import get_engine_store  # noqa: E402

router = APIRouter(prefix="/lab/v1/sim/runs", tags=["lab-adapters"])


def _eng(run_id: str):
    eng = get_engine_store().get(run_id)
    if not eng:
        raise HTTPException(404, "run not found")
    return eng


class LinkBody(BaseModel):
    event: str  # terminate|reboot|revoke|restore
    which: str | None = None


@router.post("/{run_id}/link")
def link(run_id: str, body: LinkBody) -> dict[str, Any]:
    try:
        return _eng(run_id).link_event(body.event, body.which)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e


class LocationBody(BaseModel):
    action: str
    lat: float | None = None
    lon: float | None = None
    accuracy_m: float | None = None
    label: str | None = None
    notes: str | None = None


@router.post("/{run_id}/location")
def location(run_id: str, body: LocationBody) -> dict[str, Any]:
    kwargs = {k: v for k, v in body.model_dump().items() if k != "action" and v is not None}
    try:
        return _eng(run_id).location_action(body.action, **kwargs)
    except (ValueError, KeyError) as e:
        raise HTTPException(422, str(e)) from e


class AudioBody(BaseModel):
    action: str
    authorized: bool = True
    name: str | None = None
    reason: str | None = None


@router.post("/{run_id}/audio")
def audio(run_id: str, body: AudioBody) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"authorized": body.authorized}
    if body.name is not None:
        kwargs["name"] = body.name
    if body.reason is not None:
        kwargs["reason"] = body.reason
    try:
        return _eng(run_id).audio_action(body.action, **kwargs)
    except (ValueError, KeyError) as e:
        raise HTTPException(422, str(e)) from e
