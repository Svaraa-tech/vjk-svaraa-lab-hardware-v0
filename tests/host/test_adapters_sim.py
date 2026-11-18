"""SV0-04 / SV0-06 / SV0-08.05 SIM adapter tests."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services"))

from simulator.engine import SimEngine  # noqa: E402
from simulator.location import LocationService  # noqa: E402
from simulator.audio import AudioSession  # noqa: E402
from simulator.link_status import LinkStatus  # noqa: E402


class TestLocation(unittest.TestCase):
    def test_null_indoor_and_no_body_temp(self) -> None:
        loc = LocationService()
        loc.set_indoor_null()
        d = loc.fix.for_sos_payload()
        self.assertFalse(d["valid"])
        self.assertIsNone(d["latitude"])
        p = loc.pressure.as_dict()
        self.assertIsNone(p["body_temperature"])
        self.assertIn("not body temperature", p["note"])

    def test_phone_labelled_tag_once(self) -> None:
        loc = LocationService()
        loc.set_phone_fix(37.0, -122.0, accuracy_m=20, now_ms=100)
        self.assertEqual(loc.fix.label, "phone")
        self.assertEqual(loc.fix.source, "phone")
        t1 = loc.persist_tag(label="gate", notes="n", lat=1.0, lon=2.0)
        t2 = loc.persist_tag(label="gate", notes="n", lat=1.0, lon=2.0)
        self.assertTrue(t2.get("duplicate"))
        self.assertEqual(t1["tag_id"], t2["tag_id"])

    def test_sos_first_stale_rejected(self) -> None:
        e = SimEngine()
        e.location.set_gnss(1.0, 2.0, accuracy_m=5, now_ms=50)
        e.qualify_hold_now()
        iid = e.core.state().incident
        e._incident_fix_at[iid] = 100  # newer already recorded
        e.location.set_gnss(3.0, 4.0, accuracy_m=5, now_ms=10)  # older stamp
        r = e.location_action("enrich")
        self.assertFalse(r["enrichment"]["applied"])
        self.assertEqual(r["enrichment"]["reason"], "stale_observation_rejected")


class TestAudio(unittest.TestCase):
    def test_bounded_queue_and_privacy_ends(self) -> None:
        a = AudioSession()
        a.start_session(authorized=True)
        for _ in range(20):
            a.enqueue_upload(b"x" * 8)
        self.assertGreater(a.overflow_count, 0)
        self.assertLessEqual(len(a.upload_queue), 8)
        a.on_privacy(True)
        self.assertFalse(a.active)

    def test_no_background_upload_and_llm_blocked(self) -> None:
        a = AudioSession()
        r = a.enqueue_upload(b"x")
        self.assertFalse(r.get("ok"))
        self.assertFalse(a.tool_call("suppress_sos")["allowed"])
        self.assertFalse(a.tool_call("human_ack")["allowed"])
        self.assertTrue(a.tool_call("tag_status")["allowed"])

    def test_flood_does_not_block_sos(self) -> None:
        e = SimEngine()
        e.audio_action("start")
        e.audio_action("flood")
        e.qualify_hold_now()
        self.assertEqual(e.snapshot()["reducer"]["phase"], "Pending")


class TestLinkDegraded(unittest.TestCase):
    def test_terminate_reboot_revoke_honest(self) -> None:
        link = LinkStatus()
        self.assertEqual(link.terminate_app()["status"], "degraded")
        link.restore()
        self.assertEqual(link.reboot_device()["status"], "degraded")
        self.assertIn("device_reboot", link.degraded_reasons)
        link.restore()
        snap = link.revoke("bluetooth")
        self.assertEqual(snap["status"], "degraded")
        self.assertFalse(snap["permissions"]["bluetooth"])
        # never OK while revoked
        self.assertNotEqual(snap["status"], "ok")


if __name__ == "__main__":
    unittest.main()
