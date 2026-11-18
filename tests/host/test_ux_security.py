"""SV0-05.* UX models + SV0-12.* security policy tests."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services"))

from simulator.ux import DebouncedHold, LocalAlarm, PixelModel  # noqa: E402
from simulator.update_policy import evaluate_update  # noqa: E402


class TestDebounceHold(unittest.TestCase):
    def test_bounce_does_not_duplicate(self) -> None:
        h = DebouncedHold()
        h.on_boot(False)
        # chatter
        h.set_raw(True, 0)
        h.tick(5)
        h.set_raw(False, 8)
        h.tick(10)
        h.set_raw(True, 12)
        r = h.tick(40)  # past debounce
        self.assertTrue(h.stable_down)
        # hold 2s
        r = h.tick(40 + 2000)
        self.assertTrue(r.get("qualified"))
        self.assertEqual(h.qualified_edges, 1)
        # more ticks should not add edges while still counting same hold
        h.tick(40 + 2500)
        self.assertEqual(h.qualified_edges, 1)

    def test_boot_held_requires_release(self) -> None:
        h = DebouncedHold()
        h.on_boot(True)
        h.set_raw(True, 0)
        h.tick(50)
        r = h.tick(3000)
        self.assertFalse(r.get("qualified"))
        h.set_raw(False, 3100)
        h.tick(3200)
        h.set_raw(True, 3300)
        h.tick(3400)  # debounce → stable down @ 3400
        r = h.tick(3400 + 2000)
        self.assertTrue(r.get("qualified"))


class TestPixelsAlarm(unittest.TestCase):
    def test_patterns_distinct(self) -> None:
        p = PixelModel()
        patterns = set()
        for phase in ("Pending", "ServerAccepted", "HumanAck"):
            p.apply_phase(phase)
            patterns.add(p.pattern)
            self.assertEqual(len(p.levels), 5)
            snap = p.snapshot()
            self.assertEqual(snap["forced_off_indices"][0], 5)
            self.assertTrue(snap["color_not_sole_feedback"])
        self.assertEqual(len(patterns), 3)

    def test_alarm_independent_of_assistant(self) -> None:
        a = LocalAlarm()
        a.apply_phase("Pending", assistant_failed=True)
        self.assertTrue(a.buzzer_on)
        self.assertTrue(a.haptic_on)
        self.assertFalse(a.assistant_audio_ok)
        self.assertTrue(a.snapshot()["independent_of_assistant"])


class TestSecurityPolicies(unittest.TestCase):
    def test_threat_model_table_exists(self) -> None:
        path = ROOT / "docs/security/threat_model_v0.md"
        text = path.read_text()
        for risk in ("T-SOS-01", "T-LOC-01", "T-CMD-01", "T-OTA-01", "T-AUD-01"):
            self.assertIn(risk, text)

    def test_no_shared_fleet_secret_file(self) -> None:
        # Lab must not ship a production secret material file
        for name in ("production_secrets.json", "fleet_key.pem", ".env.production"):
            self.assertFalse((ROOT / name).exists())
        policy = (ROOT / "docs/security/dev_identity_policy.md").read_text()
        self.assertIn("never a shared fleet production secret", policy)

    def test_update_reject_paths(self) -> None:
        self.assertEqual(
            evaluate_update(
                phase="Pending", signature_valid=True, compatible=True, interrupted=False
            )["status"],
            "deferred_incident",
        )
        self.assertEqual(
            evaluate_update(
                phase="Ready", signature_valid=False, compatible=True, interrupted=False
            )["status"],
            "rejected",
        )
        self.assertEqual(
            evaluate_update(
                phase="Ready", signature_valid=True, compatible=True, interrupted=True
            )["status"],
            "rollback",
        )
        self.assertTrue(
            evaluate_update(
                phase="Ready", signature_valid=True, compatible=True, interrupted=False
            )["accepted"]
        )

    def test_pinmap_sim_loads(self) -> None:
        data = json.loads((ROOT / "hardware/pinmap_sim.json").read_text())
        self.assertGreaterEqual(len(data["nets"]), 5)
        self.assertEqual(data["pixel_policy"]["logical_count"], 5)


if __name__ == "__main__":
    unittest.main()
