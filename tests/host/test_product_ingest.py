"""SV0-09.01–09.04 SIM product API tests (via FastAPI TestClient)."""
from __future__ import annotations

import sys
import tempfile
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "api"))

from fastapi.testclient import TestClient  # noqa: E402

from app import product_routes  # noqa: E402
from app.main import app  # noqa: E402


def _event(**kwargs):
    eid = str(uuid.uuid4())
    iid = str(uuid.uuid4())
    base = {
        "schema_version": "1.0",
        "event_id": eid,
        "device_id": "sv0-lab-001",
        "boot_id": str(uuid.uuid4()),
        "seq": 1,
        "mode": "live",
        "kind": "sos.created",
        "occurred_at": None,
        "uptime_ms": 1000,
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
    base.update(kwargs)
    return base


class TestProductIngest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # isolate DB
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.close()
        product_routes._conn = None
        product_routes._db_path = lambda: Path(tmp.name)  # type: ignore
        cls.client = TestClient(app)

    def test_invalid_no_side_effects(self) -> None:
        r = self.client.post("/v1/device-events", json={"schema_version": "1.0"})
        self.assertEqual(r.status_code, 422)
        body = r.json()
        detail = body.get("detail", body)
        self.assertFalse(detail.get("side_effects", True))

    def test_wrong_tenant(self) -> None:
        ev = _event()
        r = self.client.post(
            "/v1/device-events",
            json=ev,
            headers={"X-Svaraa-Tenant": "other-device"},
        )
        self.assertEqual(r.status_code, 403)

    def test_duplicate_idempotent_and_conflict(self) -> None:
        ev = _event()
        r1 = self.client.post("/v1/device-events", json=ev)
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.json()["status"], "accepted")
        r2 = self.client.post("/v1/device-events", json=ev)
        self.assertEqual(r2.status_code, 200)
        self.assertTrue(r2.json()["idempotent"])
        ev2 = dict(ev)
        ev2["seq"] = 99
        r3 = self.client.post("/v1/device-events", json=ev2)
        self.assertEqual(r3.status_code, 409)

    def test_ack_stale_no_optimistic(self) -> None:
        ev = _event()
        self.client.post("/v1/device-events", json=ev)
        iid = ev["incident_id"]
        r = self.client.post(
            f"/v1/incidents/{iid}/ack",
            json={"actor": "g", "revision": 1},
        )
        # revision ge=2 on model — may 422; use 2 then stale 2 again
        r = self.client.post(
            f"/v1/incidents/{iid}/ack",
            json={"actor": "g", "revision": 2, "action_id": str(uuid.uuid4())},
        )
        self.assertEqual(r.status_code, 200)
        r2 = self.client.post(
            f"/v1/incidents/{iid}/ack",
            json={"actor": "g", "revision": 2, "action_id": str(uuid.uuid4())},
        )
        self.assertEqual(r2.status_code, 409)
        detail = r2.json().get("detail", r2.json())
        self.assertFalse(detail.get("optimistic_success", True))

    def test_drill_suppressed_dispatch(self) -> None:
        ev = _event(
            mode="drill",
            drill_id=str(uuid.uuid4()),
            payload={
                "trigger": "drill",
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
        )
        r = self.client.post("/v1/device-events", json=ev)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["notification_stage"], "drill_suppressed")


if __name__ == "__main__":
    unittest.main()
