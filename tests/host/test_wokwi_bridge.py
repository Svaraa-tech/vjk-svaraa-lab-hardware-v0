"""Wokwi bridge + API (SV0-11.01 / WB-011–013)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services"))
sys.path.insert(0, str(ROOT / "services" / "api"))

from simulator import wokwi_bridge  # noqa: E402
from app.main import app  # noqa: E402


client = TestClient(app)


def test_project_status_and_diagram():
    st = wokwi_bridge.project_status()
    assert st["diagram_present"] is True
    assert st["platformio_ini"] is True
    assert st["evidence_profile"] == "Wokwi"
    diagram = wokwi_bridge.load_diagram()
    ids = {p["id"] for p in diagram["parts"]}
    assert {"esp", "sos", "px0", "px1", "px2", "px3", "px4"} <= ids


def test_visual_state_phases():
    for phase in ("Ready", "Pending", "HumanAck"):
        v = wokwi_bridge.visual_state(phase, hold_down=phase == "Pending")
        assert v["phase"] == phase
        assert len(v["pixels"]) == 5
        assert v["limits"]["ble"] is False
        assert "phase" in v["serial_lines"][0]


def test_api_wokwi_status_diagram_view_sync():
    r = client.get("/lab/v1/wokwi/status")
    assert r.status_code == 200
    body = r.json()
    assert body["diagram_present"] is True
    assert body["project_dir"].endswith("simulation/wokwi") or "wokwi" in body["project_dir"]

    d = client.get("/lab/v1/wokwi/diagram")
    assert d.status_code == 200
    assert "diagram" in d.json()
    assert d.json()["gpio_map"]["sos_button"]["wokwi_gpio"] == 5

    run = client.post("/lab/v1/sim/runs", json={"scenario_id": "manual_no_gps"})
    assert run.status_code == 200
    run_id = run.json()["run_id"]

    view = client.get(f"/lab/v1/wokwi/view?run_id={run_id}")
    assert view.status_code == 200
    vj = view.json()
    assert vj["visual"]["phase"] == "Ready"
    assert vj["sync"]["source_of_truth"] == "lab_engine"

    sync = client.post(f"/lab/v1/wokwi/sync/{run_id}")
    assert sync.status_code == 200
    assert sync.json()["ok"] is True
    assert sync.json()["serial_cmd"]["cmd"] == "phase"


def test_firmware_built_flag_honest():
    st = wokwi_bridge.project_status()
    firmware = ROOT / "simulation" / "wokwi" / ".pio" / "build" / "sim" / "firmware.bin"
    assert st["firmware_built"] == firmware.is_file()
