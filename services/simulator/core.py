"""Python port of firmware/core/sos_core.hpp for in-process SIM (must stay aligned)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntFlag


class Phase(str, Enum):
    Ready = "Ready"
    Prealert = "Prealert"
    Pending = "Pending"
    ServerAccepted = "ServerAccepted"
    HumanAck = "HumanAck"
    Resolved = "Resolved"


class Mode(str, Enum):
    Live = "live"
    Drill = "drill"


class Action(IntFlag):
    None_ = 0
    CreateEvent = 1
    Send = 2
    Feedback = 4
    CancelRequest = 8
    DrillInterrupted = 16
    Audit = 32


def _active(p: Phase) -> bool:
    return p in (Phase.Pending, Phase.ServerAccepted, Phase.HumanAck)


def _rank(p: Phase) -> int:
    return {
        Phase.Pending: 1,
        Phase.ServerAccepted: 2,
        Phase.HumanAck: 3,
        Phase.Resolved: 4,
    }.get(p, 0)


@dataclass
class State:
    phase: Phase = Phase.Ready
    mode: Mode = Mode.Live
    incident: str = ""
    deadline_ms: int = 0
    revision: int = 0


@dataclass
class Core:
    s: State = field(default_factory=State)

    def state(self) -> State:
        return self.s

    def _start(self, mode: Mode, incident: str) -> Action:
        self.s = State(phase=Phase.Pending, mode=mode, incident=incident)
        return Action.CreateEvent | Action.Send | Action.Feedback

    def fall_candidate(self, now: int) -> Action:
        if self.s.phase == Phase.Prealert or (
            _active(self.s.phase) and self.s.mode == Mode.Live
        ):
            return Action.None_
        interrupt = _active(self.s.phase) and self.s.mode == Mode.Drill
        self.s = State(phase=Phase.Prealert, mode=Mode.Live, deadline_ms=now + 20000)
        out = Action.Feedback | Action.Audit
        if interrupt:
            out |= Action.DrillInterrupted
        return out

    def start_drill(self, incident: str) -> Action:
        if _active(self.s.phase) or self.s.phase == Phase.Prealert:
            return Action.None_
        return self._start(Mode.Drill, incident)

    def manual_sos(self, incident: str) -> Action:
        if self.s.mode == Mode.Live and _active(self.s.phase):
            return Action.Feedback
        interrupt = self.s.mode == Mode.Drill and _active(self.s.phase)
        out = self._start(Mode.Live, incident)
        if interrupt:
            out |= Action.DrillInterrupted | Action.Audit
        return out

    def tick(self, now: int, incident: str) -> Action:
        if self.s.phase == Phase.Prealert and now >= self.s.deadline_ms:
            return self._start(Mode.Live, incident)
        return Action.None_

    def cancel(self) -> Action:
        if self.s.phase == Phase.Prealert:
            self.s = State()
            return Action.Feedback | Action.Audit
        return Action.CancelRequest | Action.Audit if _active(self.s.phase) else Action.None_

    def update(
        self, incident: str, mode: Mode, phase: Phase, rev: int, verified: bool
    ) -> Action:
        if (
            not verified
            or incident != self.s.incident
            or mode != self.s.mode
            or rev <= self.s.revision
            or not _active(self.s.phase)
            or _rank(phase) < _rank(self.s.phase)
            or _rank(phase) < 2
        ):
            return Action.None_
        self.s.phase = phase
        self.s.revision = rev
        return Action.Feedback | Action.Audit
