"""Phone/link degraded status honesty (SV0-08.05 SIM)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LinkStatus:
    """Termination, reboot, revoked permissions → honest degraded — never fake OK."""

    connected: bool = True
    permission_location: bool = True
    permission_bluetooth: bool = True
    permission_notify: bool = True
    last_event: str = "ok"
    degraded_reasons: list[str] = field(default_factory=list)

    def terminate_app(self) -> dict[str, Any]:
        self.connected = False
        self.last_event = "terminated"
        self._add("app_terminated")
        return self.snapshot()

    def reboot_device(self) -> dict[str, Any]:
        self.connected = False
        self.last_event = "reboot"
        self._add("device_reboot")
        # permissions unknown until restored
        self.permission_location = False
        self.permission_bluetooth = False
        self.permission_notify = False
        self._add("permissions_unknown_after_reboot")
        return self.snapshot()

    def revoke(self, which: str) -> dict[str, Any]:
        if which == "location":
            self.permission_location = False
        elif which == "bluetooth":
            self.permission_bluetooth = False
        elif which == "notify":
            self.permission_notify = False
        else:
            raise ValueError("unknown permission")
        self.last_event = f"revoked_{which}"
        self._add(f"permission_revoked_{which}")
        return self.snapshot()

    def restore(self) -> dict[str, Any]:
        self.connected = True
        self.permission_location = True
        self.permission_bluetooth = True
        self.permission_notify = True
        self.last_event = "restored"
        self.degraded_reasons.clear()
        return self.snapshot()

    def _add(self, reason: str) -> None:
        if reason not in self.degraded_reasons:
            self.degraded_reasons.append(reason)

    @property
    def degraded(self) -> bool:
        return (not self.connected) or not all(
            [
                self.permission_location,
                self.permission_bluetooth,
                self.permission_notify,
            ]
        )

    def snapshot(self) -> dict[str, Any]:
        status = "degraded" if self.degraded else "ok"
        return {
            "status": status,
            "connected": self.connected,
            "permissions": {
                "location": self.permission_location,
                "bluetooth": self.permission_bluetooth,
                "notify": self.permission_notify,
            },
            "last_event": self.last_event,
            "degraded_reasons": list(self.degraded_reasons),
            "honest": True,
            "note": "Never report OK when terminated/revoked/rebooted",
            "profile": "SIM",
            "simulated": True,
            "physical_phone": False,
        }
