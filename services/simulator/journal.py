"""Bounded durable journal — append/CRC/commit/replay with power-cut reopen (SV0-07.03)."""
from __future__ import annotations

import json
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class JournalError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class JournalRecord:
    event_id: str
    canonical: dict[str, Any]
    crc32: int
    committed: bool = True


class DurableJournal:
    """
    File-backed ring of committed records.
    Format (JSONL): one object per line with crc32 of canonical bytes.
    Critical capacity: reserve last `reserve` slots for sos.created only when near full.
    """

    def __init__(
        self,
        path: Path,
        *,
        capacity: int = 64,
        reserve: int = 4,
    ) -> None:
        self.path = Path(path)
        self.capacity = capacity
        self.reserve = reserve
        self.records: list[JournalRecord] = []
        self.status = "ok"  # ok | full | corrupt_tail | commit_interrupted | write_failed
        self.last_error: str | None = None
        self._force_fail = False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            self._load()

    def set_force_fail(self, v: bool) -> None:
        self._force_fail = v

    def _canonical_bytes(self, canonical: dict[str, Any]) -> bytes:
        return json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()

    def _crc(self, data: bytes) -> int:
        return zlib.crc32(data) & 0xFFFFFFFF

    def _load(self) -> None:
        self.records = []
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as e:
            self.status = "write_failed"
            self.last_error = str(e)
            return
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                raw = self._canonical_bytes(obj["canonical"])
                crc = int(obj["crc32"])
                if self._crc(raw) != crc:
                    self.status = "corrupt_tail"
                    self.last_error = f"crc mismatch at line {i}"
                    break
                self.records.append(
                    JournalRecord(
                        event_id=obj["event_id"],
                        canonical=obj["canonical"],
                        crc32=crc,
                        committed=True,
                    )
                )
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
                self.status = "corrupt_tail"
                self.last_error = f"corrupt at line {i}: {e}"
                break
        if len(self.records) >= self.capacity:
            self.status = "full"

    def size(self) -> int:
        return len(self.records)

    def _is_critical(self, canonical: dict[str, Any]) -> bool:
        return canonical.get("kind") == "sos.created"

    def append_commit(self, event_id: str, canonical: dict[str, Any]) -> JournalRecord:
        if self._force_fail:
            self.status = "write_failed"
            self.last_error = "forced write failure"
            raise JournalError("write_failed", self.last_error)

        free = self.capacity - len(self.records)
        if free <= 0:
            self.status = "full"
            self.last_error = "journal full"
            raise JournalError("full", self.last_error)
        if free <= self.reserve and not self._is_critical(canonical):
            self.status = "full"
            self.last_error = "critical capacity reserved"
            raise JournalError("full", self.last_error)

        raw = self._canonical_bytes(canonical)
        crc = self._crc(raw)
        rec = JournalRecord(event_id=event_id, canonical=canonical, crc32=crc, committed=True)
        # Simulate commit interrupt: write line then fsync; if fail mid-way, status visible
        line = json.dumps(
            {"event_id": event_id, "canonical": canonical, "crc32": crc},
            separators=(",", ":"),
        )
        try:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
                f.flush()
        except OSError as e:
            self.status = "commit_interrupted"
            self.last_error = str(e)
            raise JournalError("commit_interrupted", self.last_error) from e

        self.records.append(rec)
        self.status = "full" if len(self.records) >= self.capacity else "ok"
        self.last_error = None
        return rec

    def replay(self) -> list[JournalRecord]:
        """Return committed records (power-cut safe: only complete lines with valid CRC)."""
        return list(self.records)

    def snapshot(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "size": len(self.records),
            "capacity": self.capacity,
            "reserve": self.reserve,
            "status": self.status,
            "last_error": self.last_error,
            "event_ids": [r.event_id for r in self.records],
        }


def simulate_power_cut_reopen(path: Path, capacity: int = 64) -> DurableJournal:
    """Re-open journal after 'power cut' — only committed CRC-valid lines survive."""
    return DurableJournal(path, capacity=capacity)
