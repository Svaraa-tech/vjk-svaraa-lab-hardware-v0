"""SV0-07.06 watchdog + SV0-09.05/09.06 reconcile/consent."""
from __future__ import annotations

import sys
import tempfile
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services"))
sys.path.insert(0, str(ROOT / "services" / "api"))

from simulator.engine import SimEngine  # noqa: E402
from simulator.health import Watchdog  # noqa: E402


class TestWatchdog(unittest.TestCase):
    def test_trip_and_clear(self) -> None:
        w = Watchdog(timeout_ms=100)
        w.kick(0)
        self.assertFalse(w.tick(50))
        self.assertTrue(w.tick(200))
        self.assertTrue(w.tripped)
        w.kick(201)
        self.assertFalse(w.tripped)

    def test_engine_starve(self) -> None:
        e = SimEngine()
        snap = e.watchdog_starve()
        self.assertTrue(snap["health"]["watchdog"]["tripped"])


class TestConsentReconcile(unittest.TestCase):
    def test_consent_and_reconcile(self) -> None:
        from fastapi.testclient import TestClient
        from app import product_routes
        from app.main import app

        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.close()
        product_routes._conn = None
        product_routes._db_path = lambda: Path(tmp.name)  # type: ignore
        client = TestClient(app)

        # forbid ambient
        r = client.post(
            "/v1/consent",
            json={
                "subject_id": "user-1",
                "purpose": "ambient_audio_upload",
                "granted": True,
            },
        )
        self.assertEqual(r.status_code, 422)

        r = client.post(
            "/v1/consent",
            json={"subject_id": "user-1", "purpose": "sos_delivery", "granted": True},
        )
        self.assertEqual(r.status_code, 200)

        eid = str(uuid.uuid4())
        iid = str(uuid.uuid4())
        ev = {
            "schema_version": "1.0",
            "event_id": eid,
            "device_id": "sv0-lab-001",
            "boot_id": str(uuid.uuid4()),
            "seq": 1,
            "mode": "live",
            "kind": "sos.created",
            "occurred_at": None,
            "uptime_ms": 1,
            "incident_id": iid,
            "drill_id": None,
            "payload": {
                "trigger": "manual_button",
                "location": {
                    "source": "none",
                    "valid": False,
                    "latitude": None,
                    "longitude": None,
                    "accuracy_m": None,
                    "fix_at": None,
                    "age_ms": None,
                },
                "battery_percent": None,
                "model_version": None,
            },
        }
        self.assertEqual(client.post("/v1/device-events", json=ev).status_code, 200)
        self.assertEqual(
            client.post(
                f"/v1/incidents/{iid}/ack",
                json={"revision": 2, "actor": "g"},
            ).status_code,
            200,
        )
        rec = client.get(f"/v1/incidents/{iid}/reconcile").json()
        self.assertTrue(rec["ok"])
        self.assertIn("human_ack", rec["notification_stages"])

        client.post(f"/v1/consent/user-1/revoke")
        grants = client.get("/v1/consent/user-1").json()["grants"]
        self.assertTrue(all(v is False for v in grants.values()))


if __name__ == "__main__":
    unittest.main()
