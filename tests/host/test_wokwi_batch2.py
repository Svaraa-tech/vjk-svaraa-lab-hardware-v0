"""Wokwi batch 2 — open/doctor/fidelity/smoke/limits (WB-015…021)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services"))
sys.path.insert(0, str(ROOT / "services" / "api"))

from fastapi.testclient import TestClient  # noqa: E402
from simulator import wokwi_bridge  # noqa: E402
from simulator.pixel_palette import fidelity_report, pixels_for_phase  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)


def test_fidelity_matches_ux():
    r = fidelity_report()
    assert r["ok"] is True, r
    pending = pixels_for_phase("Pending")
    assert all(p["on"] for p in pending)
    ready = pixels_for_phase("Ready")
    assert ready[0]["on"] and not ready[1]["on"]


def test_open_doctor_smoke_routes():
    o = client.get("/lab/v1/wokwi/open")
    assert o.status_code == 200
    body = o.json()
    assert "simulation/wokwi" in body["project_abs"] or body["project_abs"].endswith("wokwi")
    assert body["elements_embed"]["available"] is False
    assert body["vscode_folder_uri"].startswith("vscode://file")

    d = client.get("/lab/v1/wokwi/doctor")
    assert d.status_code == 200
    doc = d.json()
    assert doc["firmware"]["present"] is True
    assert doc["ok"] is True
    assert any(c["id"] == "pixel_fidelity" and c["ok"] for c in doc["checks"])

    f = client.get("/lab/v1/wokwi/fidelity")
    assert f.status_code == 200 and f.json()["ok"] is True

    s = client.post("/lab/v1/wokwi/smoke?run_pio=false")
    assert s.status_code == 200 and s.json()["ok"] is True


def test_view_limits_banner():
    v = client.get("/lab/v1/wokwi/view")
    assert v.status_code == 200
    j = v.json()
    assert "no BLE" in j["limits_banner"]["text"]
    assert j["open"]["web_panel"]
    assert j["visual"]["pattern"] == "idle_dim"
