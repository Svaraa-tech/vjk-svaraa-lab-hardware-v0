"""SV0-07.03 — power-cut replay + visible write failure."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services"))

from simulator.journal import DurableJournal, JournalError, simulate_power_cut_reopen  # noqa: E402


class TestDurableJournal(unittest.TestCase):
    def test_power_cut_preserves_committed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "j.jsonl"
            j = DurableJournal(path, capacity=8, reserve=2)
            e1 = {
                "schema_version": "1.0",
                "event_id": "11111111-1111-4111-8111-111111111111",
                "kind": "sos.created",
                "device_id": "sv0-lab-001",
            }
            j.append_commit(e1["event_id"], e1)
            # power cut = reopen
            j2 = simulate_power_cut_reopen(path, capacity=8)
            self.assertEqual(j2.size(), 1)
            self.assertEqual(j2.replay()[0].event_id, e1["event_id"])
            self.assertEqual(j2.status, "ok")

    def test_write_failure_visible(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "j.jsonl"
            j = DurableJournal(path, capacity=4, reserve=1)
            j.set_force_fail(True)
            with self.assertRaises(JournalError) as ctx:
                j.append_commit("x", {"kind": "sos.created", "event_id": "x"})
            self.assertEqual(ctx.exception.code, "write_failed")
            self.assertEqual(j.status, "write_failed")
            self.assertIsNotNone(j.last_error)

    def test_critical_reserve(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "j.jsonl"
            j = DurableJournal(path, capacity=3, reserve=2)
            j.append_commit("a", {"kind": "sos.created", "event_id": "a"})
            with self.assertRaises(JournalError):
                j.append_commit("b", {"kind": "device.heartbeat", "event_id": "b"})
            # critical still allowed
            j.append_commit("c", {"kind": "sos.created", "event_id": "c"})
            self.assertEqual(j.size(), 2)

    def test_corrupt_tail_stops_replay(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "j.jsonl"
            j = DurableJournal(path, capacity=8)
            j.append_commit("a", {"kind": "sos.created", "event_id": "a"})
            with path.open("a") as f:
                f.write("{bad json\n")
            j2 = DurableJournal(path, capacity=8)
            self.assertEqual(j2.size(), 1)
            self.assertEqual(j2.status, "corrupt_tail")


if __name__ == "__main__":
    unittest.main()
