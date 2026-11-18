"""OTA accept policy stub (SV0-12.03) — SIM only."""
from __future__ import annotations

from typing import Any

ACTIVE = {"Pending", "ServerAccepted", "HumanAck"}


def evaluate_update(
    *,
    phase: str,
    signature_valid: bool,
    compatible: bool,
    interrupted: bool,
) -> dict[str, Any]:
    if phase in ACTIVE:
        return {
            "accepted": False,
            "status": "deferred_incident",
            "reason": "OTA deferred during active incident",
        }
    if not compatible:
        return {"accepted": False, "status": "rejected", "reason": "incompatible_image"}
    if not signature_valid:
        return {"accepted": False, "status": "rejected", "reason": "invalid_signature"}
    if interrupted:
        return {"accepted": False, "status": "rollback", "reason": "commit_interrupted"}
    return {"accepted": True, "status": "success", "reason": "verified"}
