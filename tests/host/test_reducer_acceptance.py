"""SV0-07.01 acceptance: precedence, cancellation, non-regressing ack."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services"))

from simulator.core import Action, Core, Mode, Phase  # noqa: E402


class TestReducerAcceptance(unittest.TestCase):
    def test_precedence_manual_over_second_sos(self) -> None:
        c = Core()
        a, b = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
        self.assertTrue(c.manual_sos(a) & Action.CreateEvent)
        self.assertFalse(c.manual_sos(b) & Action.CreateEvent)
        self.assertEqual(c.state().incident, a)

    def test_cancellation_prealert(self) -> None:
        c = Core()
        c.fall_candidate(1)
        self.assertEqual(c.state().phase, Phase.Prealert)
        self.assertTrue(c.cancel() & Action.Audit)
        self.assertEqual(c.state().phase, Phase.Ready)

    def test_non_regressing_ack(self) -> None:
        c = Core()
        a = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
        c.manual_sos(a)
        self.assertTrue(c.update(a, Mode.Live, Phase.ServerAccepted, 1, True) & Action.Feedback)
        self.assertTrue(c.update(a, Mode.Live, Phase.HumanAck, 2, True) & Action.Feedback)
        # cannot go back
        self.assertEqual(c.update(a, Mode.Live, Phase.ServerAccepted, 3, True), Action.None_)
        self.assertEqual(c.state().phase, Phase.HumanAck)

    def test_unverified_rejected(self) -> None:
        c = Core()
        a = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
        c.manual_sos(a)
        self.assertEqual(c.update(a, Mode.Live, Phase.ServerAccepted, 1, False), Action.None_)

    def test_drill_preempted_by_live(self) -> None:
        c = Core()
        d = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
        live = "llllllll-llll-4lll-8lll-llllllllllll"
        self.assertTrue(c.start_drill(d) & Action.CreateEvent)
        self.assertTrue(c.manual_sos(live) & Action.DrillInterrupted)
        self.assertEqual(c.state().mode, Mode.Live)
        self.assertEqual(c.state().incident, live)


if __name__ == "__main__":
    unittest.main()
