"""WB-005 / SOS SIM slice — in-process engine + manual_no_gps."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services"))

from simulator.engine import SimEngine  # noqa: E402
from simulator.core import Phase  # noqa: E402


class TestManualNoGps(unittest.TestCase):
    def test_manual_no_gps_path(self) -> None:
        eng = SimEngine(scenario_id="manual_no_gps", seed="test")
        result = eng.run_manual_no_gps()
        self.assertTrue(result["expect_ok"])
        self.assertEqual(result["snapshot"]["reducer"]["phase"], Phase.HumanAck.value)
        loc = result["event"]["payload"]["location"]
        self.assertFalse(loc["valid"])
        self.assertEqual(loc["source"], "none")
        self.assertIsNone(loc["latitude"])
        kinds = [t["kind"] for t in result["trace"]]
        self.assertIn("manual_sos", kinds)
        self.assertIn("device_event_accepted", kinds)
        self.assertIn("human_ack", kinds)

    def test_short_hold_rejected(self) -> None:
        eng = SimEngine()
        eng.input_hold(True)
        eng.clock.step(500)
        eng.input_hold(False)
        self.assertEqual(eng.snapshot()["reducer"]["phase"], Phase.Ready.value)
        self.assertEqual(eng.snapshot()["journal_count"], 0)


if __name__ == "__main__":
    unittest.main()
