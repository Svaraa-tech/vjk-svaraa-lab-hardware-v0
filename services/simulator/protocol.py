"""Nicla I2C frames + BLE fragment SIM (SV0-03.03/08.*, WB-008)."""
from __future__ import annotations

import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Reuse pack reference codec
_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "contracts"))
import reference_frame as rf  # noqa: E402


def encode_imu(seq: int, uptime: int, values: list[int], flags: int = 1) -> bytes:
    return rf.imu_frame(seq, uptime, values, flags=flags)


def decode_frame(raw: bytes) -> dict[str, Any]:
    if len(raw) != 32:
        raise ValueError("length")
    decoded = rf.decode(raw)
    ftype = raw[2]
    return {
        "type": {1: "IMU", 2: "wake", 3: "health", 4: "command_result"}.get(ftype, ftype),
        "flags": raw[3],
        "sequence": struct.unpack_from("<H", raw, 4)[0],
        "uptime_ms": struct.unpack_from("<I", raw, 6)[0],
        "payload": decoded if ftype == 1 else list(decoded),
        "crc_ok": True,
        "bus": "nicla_i2c_0x2A",
    }


def crc8(data: bytes) -> int:
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


def mailbox_frame(command_seq: int, opcode: int, arg: int = 0, health: int = 0) -> bytes:
    """8-byte mailbox: magic,version,command_seq,opcode,arg,health,reserved,CRC8."""
    b = bytearray(8)
    b[0], b[1] = 0x4D, 1
    b[2], b[3], b[4], b[5], b[6] = command_seq & 0xFF, opcode & 0xFF, arg & 0xFF, health & 0xFF, 0
    b[7] = crc8(bytes(b[:7]))
    return bytes(b)


def decode_mailbox(raw: bytes) -> dict[str, Any]:
    if len(raw) != 8:
        raise ValueError("mailbox length")
    if raw[0] != 0x4D or raw[1] != 1:
        raise ValueError("mailbox version")
    if crc8(raw[:7]) != raw[7]:
        raise ValueError("mailbox crc")
    opcode = {0: "none", 1: "privacy", 2: "health"}.get(raw[3], raw[3])
    return {
        "command_seq": raw[2],
        "opcode": opcode,
        "arg": raw[4],
        "health": raw[5],
        "idempotent": True,
    }


@dataclass
class BleAssembler:
    """ATT_MTU=23 → payload_per_fragment = 23-3-10 = 10 bytes."""

    mtu: int = 23
    max_message: int = 2048
    timeout_ms: int = 5000
    _bufs: dict[int, dict[str, Any]] = field(default_factory=dict)

    @property
    def payload_per_fragment(self) -> int:
        return self.mtu - 3 - 10

    def fragment(self, msg_id: int, kind: int, payload: bytes) -> list[bytes]:
        if len(payload) > self.max_message:
            raise ValueError("message too large")
        chunk = self.payload_per_fragment
        if chunk < 1:
            raise ValueError("MTU too small")
        parts = [payload[i : i + chunk] for i in range(0, max(len(payload), 1), chunk)] or [b""]
        count = len(parts)
        if count > 255:
            raise ValueError("too many fragments")
        full_crc = rf.crc16(payload)
        out = []
        for idx, part in enumerate(parts):
            hdr = struct.pack("<BBHBBHH", 1, kind, msg_id, idx, count, len(payload), full_crc)
            assert len(hdr) == 10
            out.append(hdr + part)
        return out

    def accept(self, frag: bytes, now_ms: int = 0) -> dict[str, Any] | None:
        if len(frag) < 10:
            raise ValueError("short fragment")
        ver, kind, msg_id, idx, count, total, full_crc = struct.unpack_from("<BBHBBHH", frag, 0)
        if ver != 1:
            raise ValueError("ble version")
        if total > self.max_message:
            raise ValueError("unbounded rejected")
        body = frag[10:]
        slot = self._bufs.setdefault(
            msg_id,
            {"kind": kind, "count": count, "total": total, "crc": full_crc, "parts": {}, "t": now_ms},
        )
        if slot["count"] != count or slot["total"] != total or slot["crc"] != full_crc:
            raise ValueError("conflicting duplicate fragment")
        slot["parts"][idx] = body
        if len(slot["parts"]) == count:
            payload = b"".join(slot["parts"][i] for i in range(count))
            if len(payload) != total:
                raise ValueError("length mismatch")
            if rf.crc16(payload) != full_crc:
                raise ValueError("payload crc")
            del self._bufs[msg_id]
            return {
                "msg_id": msg_id,
                "kind": {1: "event", 2: "authenticated_return", 3: "status"}.get(kind, kind),
                "payload": payload,
                "att_ack": True,
                "caregiver_ack": False,
                "note": "ATT acknowledgment never becomes caregiver acknowledgment",
            }
        return None


@dataclass
class ProtocolInspector:
    packets: list[dict[str, Any]] = field(default_factory=list)
    ble: BleAssembler = field(default_factory=BleAssembler)
    seq: int = 0

    def _add(self, layer: str, kind: str, detail: dict[str, Any], sim_ts_ms: int) -> None:
        self.seq += 1
        self.packets.append(
            {
                "seq": self.seq,
                "sim_ts_ms": sim_ts_ms,
                "layer": layer,
                "kind": kind,
                "detail": detail,
            }
        )

    def emit_imu(self, sim_ts_ms: int, values: list[int] | None = None) -> bytes:
        values = values or [0, 0, 1000, 0, 0, 0]
        raw = encode_imu(self.seq + 1, sim_ts_ms, values)
        decoded = decode_frame(raw)
        self._add("nicla_i2c", "imu_frame", {"hex": raw.hex(), **decoded}, sim_ts_ms)
        return raw

    def emit_mailbox_privacy(self, sim_ts_ms: int, applied: bool) -> bytes:
        raw = mailbox_frame(self.seq + 1, opcode=1, arg=1 if applied else 0)
        decoded = decode_mailbox(raw)
        self._add("nicla_mailbox", "privacy_command", {"hex": raw.hex(), **decoded}, sim_ts_ms)
        # result frame confirms applied state
        self._add(
            "nicla_mailbox",
            "command_result",
            {"applied": applied, "mute_disables_motion": False},
            sim_ts_ms,
        )
        return raw

    def emit_ble_event(self, sim_ts_ms: int, payload: bytes) -> dict[str, Any]:
        frags = self.ble.fragment(msg_id=self.seq + 1, kind=1, payload=payload)
        for i, f in enumerate(frags):
            self._add(
                "ble",
                "fragment",
                {"index": i, "count": len(frags), "mtu": 23, "hex": f.hex()},
                sim_ts_ms,
            )
        result = None
        for f in frags:
            result = self.ble.accept(f, sim_ts_ms)
        assert result is not None
        self._add("ble", "reassembled", result, sim_ts_ms)
        self._add(
            "ble",
            "att_ack",
            {"att_ack": True, "caregiver_ack": False, "server_receipt": False},
            sim_ts_ms,
        )
        return result

    def journey(self) -> list[dict[str, Any]]:
        return list(self.packets)
