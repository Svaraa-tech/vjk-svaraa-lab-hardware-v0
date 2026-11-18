"""Physical interaction models — debounce, pixels, haptic/buzzer (SV0-05.* SIM)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DebouncedHold:
    """Nonblocking 20ms debounce + 2s qualified hold; boot-held must release first."""

    debounce_ms: int = 20
    hold_ms: int = 2000
    raw_down: bool = False
    stable_down: bool = False
    last_change_ms: int = 0
    down_since_ms: int | None = None
    boot_held: bool = False
    qualified_edges: int = 0
    last_incident: str | None = None

    def on_boot(self, raw_down: bool) -> None:
        self.raw_down = raw_down
        self.stable_down = raw_down
        self.boot_held = raw_down
        self.down_since_ms = None

    def set_raw(self, down: bool, now_ms: int) -> None:
        if down == self.raw_down:
            return
        self.raw_down = down
        self.last_change_ms = now_ms

    def tick(self, now_ms: int) -> dict[str, Any]:
        out: dict[str, Any] = {"qualified": False, "bounce_ignored": False}
        if now_ms - self.last_change_ms < self.debounce_ms:
            out["bounce_ignored"] = self.raw_down != self.stable_down
            return out
        if self.raw_down != self.stable_down:
            self.stable_down = self.raw_down
            if self.stable_down:
                if self.boot_held:
                    # must release once after boot before qualifying
                    out["boot_held_block"] = True
                    self.down_since_ms = None
                else:
                    self.down_since_ms = now_ms
            else:
                self.boot_held = False
                held = 0 if self.down_since_ms is None else now_ms - self.down_since_ms
                self.down_since_ms = None
                if held >= self.hold_ms:
                    self.qualified_edges += 1
                    out["qualified"] = True
                    out["held_ms"] = held
        elif self.stable_down and self.down_since_ms is not None and not self.boot_held:
            held = now_ms - self.down_since_ms
            out["held_ms"] = held
            if held >= self.hold_ms and self.qualified_edges == 0:
                # edge on crossing threshold while still held
                self.qualified_edges += 1
                out["qualified"] = True
        return out

    def snapshot(self) -> dict[str, Any]:
        return {
            "debounce_ms": self.debounce_ms,
            "hold_ms": self.hold_ms,
            "raw_down": self.raw_down,
            "stable_down": self.stable_down,
            "boot_held": self.boot_held,
            "qualified_edges": self.qualified_edges,
            "last_incident": self.last_incident,
        }


PHASE_PIXEL = {
    "Ready": {"pattern": "idle_dim", "indices": [0], "alarm": False},
    "Prealert": {"pattern": "prealert_pulse", "indices": [0, 1], "alarm": False},
    "Pending": {"pattern": "pending_chase", "indices": [0, 1, 2, 3, 4], "alarm": True},
    "ServerAccepted": {"pattern": "received_solid", "indices": [0, 1, 2], "alarm": True},
    "HumanAck": {"pattern": "human_ack_breathe", "indices": [0, 1, 2, 3, 4], "alarm": False},
    "Resolved": {"pattern": "resolved_fade", "indices": [0], "alarm": False},
}


@dataclass
class PixelModel:
    """Five logical pixels; indices 5–19 forced off. Color not sole feedback."""

    levels: list[float] = field(default_factory=lambda: [0.0] * 5)
    pattern: str = "idle_dim"
    caption: str = ""

    def apply_phase(self, phase: str) -> None:
        cfg = PHASE_PIXEL.get(phase, PHASE_PIXEL["Ready"])
        self.pattern = cfg["pattern"]
        self.levels = [0.0] * 5
        for i in cfg["indices"]:
            self.levels[i] = 1.0 if phase != "Ready" else 0.2
        self.caption = f"{phase}:{self.pattern}"

    def snapshot(self) -> dict[str, Any]:
        return {
            "logical": self.levels,
            "forced_off_indices": list(range(5, 20)),
            "pattern": self.pattern,
            "caption": self.caption,
            "color_not_sole_feedback": True,
        }


@dataclass
class LocalAlarm:
    """Independent buzzer/haptic — survives assistant audio failure (SV0-05.03)."""

    buzzer_on: bool = False
    haptic_on: bool = False
    duty: float = 0.4
    duration_ms: int = 0
    assistant_audio_ok: bool = True

    def apply_phase(self, phase: str, *, assistant_failed: bool = False) -> None:
        self.assistant_audio_ok = not assistant_failed
        need = PHASE_PIXEL.get(phase, {}).get("alarm", False)
        # Local alarm independent of assistant path
        self.buzzer_on = bool(need)
        self.haptic_on = bool(need)
        self.duration_ms = 500 if need else 0

    def snapshot(self) -> dict[str, Any]:
        return {
            "buzzer_on": self.buzzer_on,
            "haptic_on": self.haptic_on,
            "duty": self.duty,
            "duration_ms": self.duration_ms,
            "assistant_audio_ok": self.assistant_audio_ok,
            "independent_of_assistant": True,
        }


@dataclass
class PrivacyModel:
    """Physical privacy switch dominates remote unmute (SV0-05.04). Not hard isolation."""

    physical_down: bool = False
    remote_mute_request: bool = False
    nicla_applied: bool = False
    pcm_stopped: bool = False
    hard_isolation_claim: bool = False  # always false — software request only

    def set_physical(self, down: bool) -> dict[str, Any]:
        self.physical_down = down
        return self._apply()

    def set_remote(self, mute: bool) -> dict[str, Any]:
        self.remote_mute_request = mute
        return self._apply()

    def _apply(self) -> dict[str, Any]:
        # Physical down forces mute; remote unmute ignored while physical down
        effective = self.physical_down or (
            self.remote_mute_request and not self.physical_down
        )
        if self.physical_down and not self.remote_mute_request:
            effective = True
        if self.physical_down:
            effective = True  # dominates remote unmute
        self.pcm_stopped = effective
        self.nicla_applied = effective
        return {
            "effective": effective,
            "pending": False,
            "applied": self.nicla_applied,
            "physical_dominates": True,
            "hard_isolation_claim": False,
        }

    def snapshot(self) -> dict[str, Any]:
        effective = self.physical_down or (
            self.remote_mute_request and not self.physical_down
        )
        if self.physical_down:
            effective = True
        return {
            "physical_down": self.physical_down,
            "remote_mute_request": self.remote_mute_request,
            "effective": effective,
            "pcm_stopped": self.pcm_stopped,
            "nicla_applied": self.nicla_applied,
            "hard_isolation_claim": False,
            "note": "Prototype software privacy request, not hard microphone isolation",
        }


@dataclass
class GesturePolicy:
    """SV0-05.05 — no delete of delivered incident; no voice-only critical action."""

    def request(
        self,
        action: str,
        *,
        phase: str,
        voice_only: bool = False,
    ) -> dict[str, Any]:
        delivered = phase in ("ServerAccepted", "HumanAck", "Resolved")
        if action == "delete_incident" and delivered:
            return {
                "allowed": False,
                "reason": "no_deletion_of_already_delivered_incident",
            }
        if action in ("manual_sos", "cancel_prealert", "cancel_request") and voice_only:
            return {
                "allowed": False,
                "reason": "no_voice_only_critical_action",
            }
        if action == "cancel_prealert" and phase == "Prealert":
            return {"allowed": True, "gesture": "short_tap"}
        if action == "manual_sos":
            return {"allowed": True, "gesture": "long_hold"}
        if action == "cancel_request" and phase in ("Pending", "ServerAccepted"):
            return {"allowed": True, "gesture": "cancel_request_only"}
        return {"allowed": False, "reason": "unsupported_or_invalid_phase"}

