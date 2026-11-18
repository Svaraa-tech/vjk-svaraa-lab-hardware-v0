"""Health / watchdog snapshot for SIM (SV0-07.06)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Watchdog:
    last_kick_ms: int = 0
    timeout_ms: int = 5000
    tripped: bool = False
    faults: list[str] = field(default_factory=list)

    def kick(self, now_ms: int) -> None:
        self.last_kick_ms = now_ms
        if self.tripped:
            self.tripped = False
            self.faults.append("watchdog_cleared")

    def tick(self, now_ms: int) -> bool:
        if now_ms - self.last_kick_ms > self.timeout_ms:
            if not self.tripped:
                self.tripped = True
                self.faults.append("watchdog_timeout")
            return True
        return False

    def snapshot(self, *, journal_status: str, transport_ok: bool) -> dict[str, Any]:
        components = {
            "motion": "mocked",
            "location": "degraded" if True else "ok",  # null GPS honest
            "journal": "degraded" if journal_status not in ("ok",) else "mocked",
            "transport": "ok" if transport_ok else "faulted",
            "watchdog": "faulted" if self.tripped else "ok",
        }
        return {
            "components": components,
            "watchdog": {
                "last_kick_ms": self.last_kick_ms,
                "timeout_ms": self.timeout_ms,
                "tripped": self.tripped,
            },
            "faults": list(self.faults),
            "profile": "SIM",
        }
