"""Virtual monotonic clock — pause / step / speed (WB-005)."""

from __future__ import annotations


class VirtualClock:
    def __init__(self, start_ms: int = 0) -> None:
        self._ms = int(start_ms)
        self.paused = True
        self.speed = 1.0

    @property
    def monotonic_ms(self) -> int:
        return self._ms

    def pause(self) -> None:
        self.paused = True

    def play(self, speed: float = 1.0) -> None:
        self.speed = max(0.0, float(speed))
        self.paused = False

    def step(self, delta_ms: int) -> int:
        self._ms += max(0, int(delta_ms))
        return self._ms

    def advance_wall(self, wall_delta_ms: float) -> int:
        if self.paused:
            return self._ms
        self._ms += int(wall_delta_ms * self.speed)
        return self._ms

    def reset(self, start_ms: int = 0) -> None:
        self._ms = int(start_ms)
        self.paused = True
        self.speed = 1.0
