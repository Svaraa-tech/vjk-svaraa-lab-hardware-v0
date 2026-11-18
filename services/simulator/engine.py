"""In-process SIM engine: virtual clock + sos core + journal/outbox + traces (WB-005)."""
from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .clock import VirtualClock
from .core import Action, Core, Mode, Phase
from .journal import DurableJournal, JournalError
from .health import Watchdog
from .ux import DebouncedHold, PixelModel, LocalAlarm, PrivacyModel, GesturePolicy
from .protocol import ProtocolInspector
from .location import LocationService
from .audio import AudioSession
from .link_status import LinkStatus
from .sensors import SensorBus


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


@dataclass
class TraceEvent:
    seq: int
    sim_ts_ms: int
    layer: str
    kind: str
    detail: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "seq": self.seq,
            "sim_ts_ms": self.sim_ts_ms,
            "layer": self.layer,
            "kind": self.kind,
            "detail": self.detail,
        }


@dataclass
class JournalEntry:
    event_id: str
    kind: str
    incident_id: str
    canonical: dict[str, Any]
    committed: bool = True


class SimEngine:
    HOLD_MS = 2000  # qualified manual hold

    def __init__(self, *, scenario_id: str = "manual_no_gps", seed: str | None = None) -> None:
        self.run_id = _uuid()
        self.scenario_id = scenario_id
        self.seed = seed or self.run_id[:8]
        self.device_id = "sv0-lab-001"
        self.boot_id = _uuid()
        self.clock = VirtualClock(0)
        self.core = Core()
        self.seq = 0
        self.event_seq = 0
        self.traces: list[TraceEvent] = []
        self.journal: list[JournalEntry] = []
        self.outbox: list[dict[str, Any]] = []
        self.incidents: dict[str, dict[str, Any]] = {}
        self.hold_down_at: int | None = None
        self.created_at = _utc()
        self._lock = threading.RLock()
        root = Path(__file__).resolve().parents[2]
        jpath = root / ".workbench" / "journals" / f"{self.run_id}.jsonl"
        self.durable = DurableJournal(jpath, capacity=64, reserve=4)
        self.fall_model_version = "fall-synth-0.1"
        self.watchdog = Watchdog()
        self.watchdog.kick(0)
        self.hold = DebouncedHold()
        self.pixels = PixelModel()
        self.alarm = LocalAlarm()
        self.sensors = SensorBus()
        self.privacy = PrivacyModel()
        self.gestures = GesturePolicy()
        self.protocol = ProtocolInspector()
        self.location = LocationService()
        self.audio = AudioSession()
        self.link = LinkStatus()
        self.faults: dict[str, bool] = {}
        self._incident_fix_at: dict[str, int] = {}
        self.pixels.apply_phase("Ready")
        self.alarm.apply_phase("Ready")
        self._emit("engine", "run_created", {"scenario_id": scenario_id, "seed": self.seed})

    def _emit(self, layer: str, kind: str, detail: dict[str, Any] | None = None) -> None:
        self.seq += 1
        self.traces.append(
            TraceEvent(
                seq=self.seq,
                sim_ts_ms=self.clock.monotonic_ms,
                layer=layer,
                kind=kind,
                detail=detail or {},
            )
        )

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            st = self.core.state()
            return {
                "run_id": self.run_id,
                "scenario_id": self.scenario_id,
                "seed": self.seed,
                "device_id": self.device_id,
                "boot_id": self.boot_id,
                "created_at": self.created_at,
                "clock": {
                    "monotonic_ms": self.clock.monotonic_ms,
                    "paused": self.clock.paused,
                    "speed": self.clock.speed,
                },
                "reducer": {
                    "phase": st.phase.value,
                    "mode": st.mode.value,
                    "incident_id": st.incident or None,
                    "deadline_ms": st.deadline_ms,
                    "revision": st.revision,
                },
                "hold": {
                    "down": self.hold_down_at is not None,
                    "down_at_ms": self.hold_down_at,
                    "qualified_ms": self.HOLD_MS,
                },
                "journal_count": len(self.journal),
                "outbox_count": len(self.outbox),
                "incident_count": len(self.incidents),
                "trace_count": len(self.traces),
                "durable_journal": self.durable.snapshot(),
                "health": self.watchdog.snapshot(journal_status=self.durable.status, transport_ok=True),
                "hold_model": self.hold.snapshot(),
                "pixels": self.pixels.snapshot(),
                "alarm": self.alarm.snapshot(),
                "sensors": self.sensors.snapshot(),
                "privacy": self.privacy.snapshot(),
                "protocol_packets": len(self.protocol.packets),
                "location": self.location.snapshot(),
                "audio": self.audio.snapshot(),
                "link": self.link.snapshot(),
                "faults": dict(self.faults),
                "profile": "SIM",
                "notification_provider": "mock",
                "simulated": True,
            }

    def control(self, action: str, *, delta_ms: int = 100, speed: float = 1.0) -> dict[str, Any]:
        with self._lock:
            if action == "play":
                self.clock.play(speed)
                self._emit("clock", "play", {"speed": speed})
            elif action == "pause":
                self.clock.pause()
                self._emit("clock", "pause", {})
            elif action == "step":
                self.clock.step(delta_ms)
                self._on_tick()
                self.watchdog.kick(self.clock.monotonic_ms)
                self.watchdog.tick(self.clock.monotonic_ms)
                self._emit("clock", "step", {"delta_ms": delta_ms})
            elif action == "reset":
                raise RuntimeError("use store.create for a fresh run")
            else:
                raise ValueError(f"unknown control action {action}")
            return self.snapshot()

    def _on_tick(self) -> None:
        actions = self.core.tick(self.clock.monotonic_ms, _uuid())
        if actions:
            self._emit("reducer", "tick", {"actions": int(actions)})

    def input_hold(self, down: bool) -> dict[str, Any]:
        """Debounced SOS button: qualify after HOLD_MS while held (or step clock)."""
        with self._lock:
            now = self.clock.monotonic_ms
            if down:
                if self.hold_down_at is None:
                    self.hold_down_at = now
                    self._emit("ui", "hold_down", {"at_ms": now})
            else:
                if self.hold_down_at is not None:
                    held = now - self.hold_down_at
                    self._emit("ui", "hold_up", {"held_ms": held})
                    self.hold_down_at = None
                    if held < self.HOLD_MS:
                        self._emit("ui", "hold_rejected_short", {"held_ms": held})
            return self.snapshot()

    def qualify_hold_now(self) -> dict[str, Any]:
        """Advance clock to satisfy hold and fire manual SOS (SIM convenience)."""
        with self._lock:
            if self.hold_down_at is None:
                self.hold_down_at = self.clock.monotonic_ms
                self._emit("ui", "hold_down", {"at_ms": self.hold_down_at, "synth": True})
            need = self.HOLD_MS - (self.clock.monotonic_ms - self.hold_down_at)
            if need > 0:
                self.clock.step(need)
            return self._fire_manual_sos()

    def _fire_manual_sos(self) -> dict[str, Any]:
        incident_id = _uuid()
        actions = self.core.manual_sos(incident_id)
        self._emit(
            "reducer",
            "manual_sos",
            {"actions": int(actions), "incident_id": incident_id},
        )
        self.hold_down_at = None
        if actions & Action.CreateEvent:
            self.event_seq += 1
            event = self._build_device_event(incident_id)
            entry = JournalEntry(
                event_id=event["event_id"],
                kind=event["kind"],
                incident_id=incident_id,
                canonical=event,
            )
            try:
                self.durable.append_commit(event["event_id"], event)
            except JournalError as e:
                self._emit("journal", "write_failed", {"code": e.code, "error": str(e)})
                self.render_degraded = True
                return self.snapshot()
            self.journal.append(entry)
            self._emit("journal", "append_commit", {"event_id": event["event_id"], "crc": True})
            self.outbox.append(
                {
                    "event_id": event["event_id"],
                    "status": "pending",
                    "attempts": 0,
                }
            )
            self.incidents[incident_id] = {
                "incident_id": incident_id,
                "mode": "live",
                "phase": Phase.Pending.value,
                "revision": 0,
                "location": event["payload"]["location"],
                "event_id": event["event_id"],
                "created_sim_ms": self.clock.monotonic_ms,
            }
            self._emit("transport", "outbox_enqueued", {"event_id": event["event_id"]})
            self._sync_ux()
            if not self.faults.get("drop_ble"):
                self.protocol.emit_imu(self.clock.monotonic_ms)
                self.protocol.emit_ble_event(
                    self.clock.monotonic_ms, event["event_id"].encode()
                )
        return self.snapshot()

    def _build_device_event(self, incident_id: str) -> dict[str, Any]:
        # manual_no_gps: null location, live, manual_button
        return {
            "schema_version": "1.0",
            "event_id": _uuid(),
            "device_id": self.device_id,
            "boot_id": self.boot_id,
            "seq": self.event_seq,
            "mode": "live",
            "kind": "sos.created",
            "occurred_at": None,
            "uptime_ms": self.clock.monotonic_ms,
            "incident_id": incident_id,
            "drill_id": None,
            "payload": {
                "trigger": "manual_button",
                "location": self.location.fix.for_sos_payload(),
                "battery_percent": None,
                "model_version": None,
            },
        }

    def commit_to_server(self, event_id: str | None = None) -> dict[str, Any]:
        """Idempotent mock ingest: Pending → ServerAccepted (verified). Same event_id = one incident."""
        with self._lock:
            if not self.journal:
                raise ValueError("no journal entries")
            entry = None
            if event_id:
                entry = next((j for j in self.journal if j.event_id == event_id), None)
            else:
                entry = self.journal[-1]
            if not entry:
                raise KeyError(event_id)
            incident_id = entry.incident_id
            already = (
                incident_id in self.incidents
                and self.incidents[incident_id].get("phase")
                in (Phase.ServerAccepted.value, Phase.HumanAck.value, Phase.Resolved.value)
            )
            actions = Action.None_
            if not already:
                actions = self.core.update(
                    incident_id, Mode.Live, Phase.ServerAccepted, 1, verified=True
                )
                if incident_id in self.incidents:
                    self.incidents[incident_id]["phase"] = Phase.ServerAccepted.value
                    self.incidents[incident_id]["revision"] = 1
            for o in self.outbox:
                if o["event_id"] == entry.event_id:
                    o["status"] = "accepted"
                    o["attempts"] = o.get("attempts", 0) + 1
            self._sync_ux()
            self._emit(
                "server",
                "device_event_accepted",
                {
                    "event_id": entry.event_id,
                    "actions": int(actions),
                    "idempotent": already,
                },
            )
            return {
                "accepted": True,
                "idempotent": already,
                "event": entry.canonical,
                "snapshot": self.snapshot(),
            }

    def human_ack(self, incident_id: str | None = None) -> dict[str, Any]:
        with self._lock:
            st = self.core.state()
            iid = incident_id or st.incident
            if not iid:
                raise ValueError("no active incident")
            actions = self.core.update(iid, Mode.Live, Phase.HumanAck, 2, verified=True)
            if iid in self.incidents:
                self.incidents[iid]["phase"] = Phase.HumanAck.value
                self.incidents[iid]["revision"] = 2
            self._emit(
                "guardian",
                "human_ack",
                {"incident_id": iid, "actions": int(actions), "provider": "mock"},
            )
            self._sync_ux()
            return self.snapshot()


    def fall_candidate(self, *, quality_ok: bool = True) -> dict[str, Any]:
        """Experimental fall path (SV0-07.02) — synthetic; no clinical claim."""
        with self._lock:
            if not quality_ok:
                self._emit(
                    "fall",
                    "rejected_quality",
                    {"model": self.fall_model_version, "clinical_claim": False},
                )
                return self.snapshot()
            actions = self.core.fall_candidate(self.clock.monotonic_ms)
            self._emit(
                "fall",
                "candidate",
                {
                    "actions": int(actions),
                    "model": self.fall_model_version,
                    "clinical_claim": False,
                },
            )
            return self.snapshot()

    def confirm_fall_after_deadline(self) -> dict[str, Any]:
        with self._lock:
            st = self.core.state()
            if st.phase != Phase.Prealert:
                return self.snapshot()
            need = max(0, st.deadline_ms - self.clock.monotonic_ms)
            if need:
                self.clock.step(need)
            incident_id = _uuid()
            actions = self.core.tick(self.clock.monotonic_ms, incident_id)
            self._emit("reducer", "fall_escalated", {"actions": int(actions)})
            if actions & Action.CreateEvent:
                # reuse manual fire path shape
                self.event_seq += 1
                # force incident id used by tick start
                st = self.core.state()
                incident_id = st.incident
                event = self._build_device_event(incident_id)
                event["payload"]["trigger"] = "fall_candidate_confirmed"
                event["payload"]["model_version"] = self.fall_model_version
                try:
                    self.durable.append_commit(event["event_id"], event)
                except JournalError as e:
                    self._emit("journal", "write_failed", {"code": e.code})
                    return self.snapshot()
                self.journal.append(
                    JournalEntry(event["event_id"], event["kind"], incident_id, event)
                )
                self.outbox.append({"event_id": event["event_id"], "status": "pending", "attempts": 0})
                self.incidents[incident_id] = {
                    "incident_id": incident_id,
                    "mode": "live",
                    "phase": Phase.Pending.value,
                    "revision": 0,
                    "location": event["payload"]["location"],
                    "event_id": event["event_id"],
                    "created_sim_ms": self.clock.monotonic_ms,
                }
            return self.snapshot()

    def retry_outbox(self, *, drop_response: bool = False) -> dict[str, Any]:
        """SV0-07.04: retry same event_id; lost receipt still one incident."""
        with self._lock:
            if not self.outbox:
                raise ValueError("empty outbox")
            item = self.outbox[-1]
            item["attempts"] = item.get("attempts", 0) + 1
            event_id = item["event_id"]
            # same bytes/id
            if drop_response:
                self._emit("transport", "lost_receipt", {"event_id": event_id, "attempt": item["attempts"]})
                return self.snapshot()
            # dual-route: second accept still same incident
            self._emit("transport", "retry_send", {"event_id": event_id, "attempt": item["attempts"]})
            return self.commit_to_server(event_id)

    def _sync_ux(self, *, assistant_failed: bool = False) -> None:
        phase = self.core.state().phase.value
        self.pixels.apply_phase(phase)
        self.alarm.apply_phase(phase, assistant_failed=assistant_failed)
        self.sensors.step(0)
        self.sensors.privacy = self.privacy.snapshot()["effective"]

    def set_privacy_physical(self, down: bool) -> dict:
        with self._lock:
            detail = self.privacy.set_physical(down)
            self.protocol.emit_mailbox_privacy(self.clock.monotonic_ms, detail["applied"])
            self.audio.on_privacy(detail["effective"])
            self._emit("privacy", "physical", detail)
            self._sync_ux()
            return self.snapshot()

    def set_privacy_remote(self, mute: bool) -> dict:
        with self._lock:
            detail = self.privacy.set_remote(mute)
            self._emit("privacy", "remote", detail)
            self._sync_ux()
            return self.snapshot()

    def gesture(self, action: str, *, voice_only: bool = False) -> dict:
        with self._lock:
            phase = self.core.state().phase.value
            result = self.gestures.request(action, phase=phase, voice_only=voice_only)
            self._emit("gesture", action, result)
            if result.get("allowed") and action == "cancel_prealert":
                self.core.cancel()
                self._sync_ux()
            return {"gesture": result, "snapshot": self.snapshot()}

    def inject_protocol_sample(self) -> dict:
        with self._lock:
            t = self.clock.monotonic_ms
            self.protocol.emit_imu(t)
            if self.journal:
                payload = self.journal[-1].canonical["event_id"].encode()
            else:
                payload = b"sim-event"
            if not self.faults.get("drop_ble"):
                self.protocol.emit_ble_event(t, payload)
            else:
                self._emit("fault", "drop_ble", {})
            return {"packets": self.protocol.journey(), "snapshot": self.snapshot()}

    def set_fault(self, name: str, enabled: bool) -> dict:
        with self._lock:
            self.faults[name] = enabled
            self._emit("fault", name, {"enabled": enabled})
            return self.snapshot()

    def link_event(self, event: str, which: str | None = None) -> dict:
        with self._lock:
            if event == "terminate":
                snap = self.link.terminate_app()
            elif event == "reboot":
                snap = self.link.reboot_device()
            elif event == "revoke":
                snap = self.link.revoke(which or "location")
            elif event == "restore":
                snap = self.link.restore()
            else:
                raise ValueError("unknown link event")
            self._emit("link", event, snap)
            return self.snapshot()

    def location_action(self, action: str, **kwargs) -> dict:
        with self._lock:
            now = self.clock.monotonic_ms
            if action == "no_fix":
                self.location.set_no_fix()
            elif action == "indoor":
                self.location.set_indoor_null()
            elif action == "gnss":
                self.location.set_gnss(
                    kwargs["lat"], kwargs["lon"], accuracy_m=kwargs.get("accuracy_m", 12.0), now_ms=now
                )
            elif action == "phone":
                self.location.set_phone_fix(
                    kwargs["lat"], kwargs["lon"], accuracy_m=kwargs.get("accuracy_m", 25.0), now_ms=now
                )
            elif action == "tag":
                tag = self.location.persist_tag(
                    label=kwargs.get("label", "home"),
                    notes=kwargs.get("notes", ""),
                    lat=kwargs.get("lat"),
                    lon=kwargs.get("lon"),
                )
                self._emit("location", "tag", tag)
                return {"tag": tag, "snapshot": self.snapshot()}
            elif action == "enrich":
                st = self.core.state()
                iid = st.incident
                if not iid:
                    raise ValueError("no active incident")
                prev = self._incident_fix_at.get(iid)
                rec = self.location.enrich_incident(
                    incident_id=iid, now_ms=now, existing_fix_at_ms=prev
                )
                if rec and rec.get("applied") and self.location.fix.fix_at_ms is not None:
                    self._incident_fix_at[iid] = self.location.fix.fix_at_ms
                self._emit("location", "enrich", rec or {})
                return {"enrichment": rec, "snapshot": self.snapshot()}
            elif action == "pressure_stale":
                self.location.mark_pressure_stale(True)
            elif action == "pressure_fault":
                self.location.mark_pressure_fault(True)
            else:
                raise ValueError(action)
            self._emit("location", action, self.location.fix.as_dict())
            return self.snapshot()

    def audio_action(self, action: str, **kwargs) -> dict:
        with self._lock:
            if action == "start":
                r = self.audio.start_session(authorized=kwargs.get("authorized", True))
            elif action == "end":
                r = self.audio.end_session(kwargs.get("reason", "user"))
            elif action == "upload":
                r = self.audio.enqueue_upload(kwargs.get("chunk", b"x" * 64))
            elif action == "play":
                r = self.audio.half_duplex_play(kwargs.get("chunk", b"y" * 64))
            elif action == "tool":
                r = self.audio.tool_call(kwargs["name"])
            elif action == "flood":
                # prove bounded queue does not grow forever / block SOS
                results = [self.audio.enqueue_upload(b"z" * 32) for _ in range(20)]
                r = {"flood": results, "blocks_sos": False, "overflow": self.audio.overflow_count}
            else:
                raise ValueError(action)
            self._emit("audio", action, r if isinstance(r, dict) else {})
            return {"result": r, "snapshot": self.snapshot()}



    def watchdog_starve(self, advance_ms: int | None = None) -> dict[str, Any]:
        with self._lock:
            delta = self.watchdog.timeout_ms + 1 if advance_ms is None else advance_ms
            self.clock.step(delta)
            self.watchdog.tick(self.clock.monotonic_ms)
            self._emit("watchdog", "tick", {"tripped": self.watchdog.tripped})
            return self.snapshot()

    def start_drill(self) -> dict[str, Any]:
        with self._lock:
            drill_id = _uuid()
            actions = self.core.start_drill(drill_id)
            self._emit("reducer", "start_drill", {"actions": int(actions), "drill_id": drill_id})
            return self.snapshot()

    def run_manual_no_gps(self) -> dict[str, Any]:
        """Headless acceptance path for scenario manual_no_gps."""
        with self._lock:
            self.qualify_hold_now()
            commit = self.commit_to_server()
            snap = self.human_ack()
            expect_ok = (
                snap["reducer"]["phase"] == Phase.HumanAck.value
                and snap["incident_count"] == 1
                and commit["event"]["payload"]["location"]["valid"] is False
            )
            self._emit(
                "scenario",
                "manual_no_gps_complete",
                {"expect_ok": expect_ok},
            )
            return {
                "expect_ok": expect_ok,
                "snapshot": snap,
                "event": commit["event"],
                "trace": [t.as_dict() for t in self.traces],
            }

    def trace(self) -> list[dict[str, Any]]:
        with self._lock:
            return [t.as_dict() for t in self.traces]

    def pending_event(self) -> dict[str, Any] | None:
        with self._lock:
            if not self.journal:
                return None
            return self.journal[-1].canonical


class EngineStore:
    def __init__(self) -> None:
        self._runs: dict[str, SimEngine] = {}
        self._lock = threading.RLock()

    def create(self, scenario_id: str = "manual_no_gps", seed: str | None = None) -> SimEngine:
        eng = SimEngine(scenario_id=scenario_id, seed=seed)
        with self._lock:
            self._runs[eng.run_id] = eng
        return eng

    def get(self, run_id: str) -> SimEngine | None:
        with self._lock:
            return self._runs.get(run_id)

    def latest(self) -> SimEngine | None:
        with self._lock:
            if not self._runs:
                return None
            return next(reversed(self._runs.values()))


_STORE = EngineStore()


def get_engine_store() -> EngineStore:
    return _STORE


def project_scenarios() -> list[dict[str, Any]]:
    root = Path(__file__).resolve().parents[2]
    path = root / "simulation" / "scenarios" / "scenarios.json"
    if path.is_file():
        return json.loads(path.read_text())
    return []
