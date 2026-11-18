"""Audio half-duplex SIM — bounded queues, privacy ends session (SV0-06.*)."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any


ALLOWED_TOOLS = {"tag_status", "read_phase", "request_privacy_state"}
FORBIDDEN_TOOLS = {"suppress_sos", "human_ack", "change_ownership", "resolve_incident"}


@dataclass
class AudioSession:
    """Explicit authorized voice session — no background upload."""

    active: bool = False
    mode: str = "idle"  # idle | capture | playback
    privacy_ends_session: bool = True
    upload_queue: deque[bytes] = field(default_factory=lambda: deque(maxlen=8))
    playback_queue: deque[bytes] = field(default_factory=lambda: deque(maxlen=8))
    overflow_count: int = 0
    sample_rate_hz: int = 16000
    slot_bits: int = 32
    channels: str = "stereo_slots_left_pcm_signed"
    assistant_ok: bool = True

    def start_session(self, *, authorized: bool) -> dict[str, Any]:
        if not authorized:
            return {"ok": False, "reason": "not_authorized"}
        self.active = True
        self.mode = "capture"
        return {"ok": True, "mode": self.mode}

    def end_session(self, reason: str = "timeout") -> dict[str, Any]:
        self.active = False
        self.mode = "idle"
        self.upload_queue.clear()
        return {"ok": True, "reason": reason, "active": False}

    def on_privacy(self, effective: bool) -> dict[str, Any]:
        if effective and self.privacy_ends_session and self.active:
            return self.end_session("privacy")
        return {"ok": True, "active": self.active}

    def enqueue_upload(self, chunk: bytes) -> dict[str, Any]:
        if not self.active:
            return {"ok": False, "reason": "no_session", "background_upload": False}
        before = len(self.upload_queue)
        self.upload_queue.append(chunk)
        if len(self.upload_queue) == before and before == self.upload_queue.maxlen:
            self.overflow_count += 1
            return {
                "ok": False,
                "reason": "queue_full",
                "overflow_count": self.overflow_count,
                "blocks_sos": False,
            }
        return {"ok": True, "occupancy": len(self.upload_queue)}

    def half_duplex_play(self, chunk: bytes) -> dict[str, Any]:
        if self.mode == "capture":
            self.mode = "playback"  # stop capture for playback turn
        self.playback_queue.append(chunk)
        return {"ok": True, "mode": self.mode, "occupancy": len(self.playback_queue)}

    def tool_call(self, name: str) -> dict[str, Any]:
        if name in FORBIDDEN_TOOLS:
            return {
                "allowed": False,
                "reason": "llm_cannot_hold_safety_authority",
                "tool": name,
            }
        if name not in ALLOWED_TOOLS:
            return {"allowed": False, "reason": "unknown_tool", "tool": name}
        return {"allowed": True, "tool": name}

    def snapshot(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "mode": self.mode,
            "upload_occupancy": len(self.upload_queue),
            "upload_capacity": self.upload_queue.maxlen,
            "playback_occupancy": len(self.playback_queue),
            "overflow_count": self.overflow_count,
            "sample_rate_hz": self.sample_rate_hz,
            "channels": self.channels,
            "background_upload": False,
            "blocks_sos": False,
            "assistant_ok": self.assistant_ok,
            "allowed_tools": sorted(ALLOWED_TOOLS),
            "forbidden_tools": sorted(FORBIDDEN_TOOLS),
            "note": "SIM model — not measured I2S bench timing",
            "simulated": True,
        }
