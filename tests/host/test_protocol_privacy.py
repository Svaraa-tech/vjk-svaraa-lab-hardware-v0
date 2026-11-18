"""WB-008 / SV0-03.03 / SV0-05.04-05 / SV0-08.* SIM protocol & privacy tests."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services"))
sys.path.insert(0, str(ROOT / "contracts"))

from simulator.protocol import (  # noqa: E402
    BleAssembler,
    decode_frame,
    decode_mailbox,
    encode_imu,
    mailbox_frame,
    ProtocolInspector,
)
from simulator.ux import GesturePolicy, PrivacyModel  # noqa: E402
from simulator.engine import SimEngine  # noqa: E402


class TestNiclaCodec(unittest.TestCase):
    def test_roundtrip_and_malformed(self) -> None:
        raw = encode_imu(3, 999, [10, -20, 1000, 1, 2, 3])
        d = decode_frame(raw)
        self.assertEqual(d["type"], "IMU")
        with self.assertRaises(ValueError):
            decode_frame(b"\x00" * 10)
        with self.assertRaises(ValueError):
            decode_frame(b"\x53\x01" + b"\x00" * 30)  # bad crc likely

    def test_mailbox_privacy_result(self) -> None:
        mb = mailbox_frame(2, 1, 1)
        d = decode_mailbox(mb)
        self.assertEqual(d["opcode"], "privacy")
        self.assertTrue(d["idempotent"])


class TestBleMtu(unittest.TestCase):
    def test_mtu23_reassemble_and_att_not_caregiver(self) -> None:
        ble = BleAssembler(mtu=23)
        self.assertEqual(ble.payload_per_fragment, 10)
        payload = b"x" * 25
        frags = ble.fragment(1, 1, payload)
        self.assertGreaterEqual(len(frags), 3)
        out = None
        for f in frags:
            self.assertLessEqual(len(f), 23)
            out = ble.accept(f)
        self.assertIsNotNone(out)
        assert out is not None
        self.assertEqual(out["payload"], payload)
        self.assertTrue(out["att_ack"])
        self.assertFalse(out["caregiver_ack"])

    def test_reject_unbounded(self) -> None:
        ble = BleAssembler()
        with self.assertRaises(ValueError):
            ble.fragment(1, 1, b"a" * 3000)


class TestPrivacyGestures(unittest.TestCase):
    def test_physical_dominates_remote_unmute(self) -> None:
        p = PrivacyModel()
        p.set_remote(True)
        p.set_physical(True)
        p.set_remote(False)  # remote unmute
        snap = p.snapshot()
        self.assertTrue(snap["effective"])
        self.assertFalse(snap["hard_isolation_claim"])

    def test_no_delete_delivered_no_voice_critical(self) -> None:
        g = GesturePolicy()
        self.assertFalse(
            g.request("delete_incident", phase="ServerAccepted")["allowed"]
        )
        self.assertFalse(
            g.request("manual_sos", phase="Ready", voice_only=True)["allowed"]
        )
        self.assertTrue(g.request("manual_sos", phase="Ready", voice_only=False)["allowed"])


class TestInspectorEngine(unittest.TestCase):
    def test_sos_produces_packet_journey(self) -> None:
        e = SimEngine()
        e.qualify_hold_now()
        packets = e.protocol.journey()
        layers = {p["layer"] for p in packets}
        self.assertIn("ble", layers)
        att = [p for p in packets if p["kind"] == "att_ack"]
        self.assertTrue(att)
        self.assertFalse(att[0]["detail"]["caregiver_ack"])


if __name__ == "__main__":
    unittest.main()
