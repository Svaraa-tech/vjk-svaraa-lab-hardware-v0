"""Bridge behavioral SimEngine ↔ Wokwi visual subset (WB-011+)."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from simulator.pixel_palette import (
    PHASE_PATTERN,
    PHASE_PIXEL_INDICES,
    fidelity_report,
    pixels_for_phase,
)

ROOT = Path(__file__).resolve().parents[2]
WOKWI_DIR = ROOT / "simulation" / "wokwi"


def load_diagram() -> dict[str, Any]:
    path = WOKWI_DIR / "diagram.json"
    return json.loads(path.read_text())


def gpio_map() -> dict[str, Any]:
    return {
        "sos_button": {"wokwi_gpio": 5, "arduino_product": "D2", "part": "sos"},
        "privacy_switch": {
            "wokwi_gpio": 21,
            "arduino_product": "D10",
            "part": "privacy",
        },
        "pixels": {
            "wokwi_gpio": 18,
            "arduino_product": "D9",
            "parts": ["px0", "px1", "px2", "px3", "px4"],
        },
        "buzzer": {"wokwi_gpio": 1, "arduino_product": "A0", "part": "buzzer"},
        "haptic_proxy_led": {
            "wokwi_gpio": 14,
            "arduino_product": "D12 (product GPIO47)",
            "part": "haptic",
            "note": "Vibration motor not in Wokwi — LED proxy",
        },
        "i2c": {
            "sda": {"wokwi_gpio": 11, "arduino_product": "A4"},
            "scl": {"wokwi_gpio": 12, "arduino_product": "A5"},
            "parts": {
                "bmp180_stand_in_for_bmp390": "bmp",
                "mpu6050_stand_in_not_nicla_bmi270": "imu",
            },
        },
        "unsupported_in_wokwi": [
            "BLE",
            "I2S",
            "Nicla_I2C_target",
            "MAX_M10S_GNSS",
            "AHCT125_buffer",
        ],
        "doc": "simulation/wokwi/GPIO_MAP.md",
        "how_to_run": "Open simulation/wokwi in VS Code → Wokwi: Start Simulator",
    }


PHASE_ORDER: list[str] = list(PHASE_PIXEL_INDICES.keys())

PHASE_ANNOTATIONS: dict[str, str] = {
    "Ready": "idle dim · waiting for qualified hold",
    "Prealert": "hold crossing qualify threshold",
    "Pending": "SOS committed · awaiting server",
    "ServerAccepted": "server accepted · guardian queue",
    "HumanAck": "guardian ACK · human in loop",
    "Resolved": "incident closed · fade to idle",
}


def phase_catalog() -> dict[str, Any]:
    """WB-025 — ordered phases + serial annotation copy for stepper."""
    steps = []
    for i, phase in enumerate(PHASE_ORDER):
        steps.append(
            {
                "index": i,
                "phase": phase,
                "pattern": PHASE_PATTERN.get(phase, "idle_dim"),
                "annotation": PHASE_ANNOTATIONS.get(phase, phase),
                "pixels_on": PHASE_PIXEL_INDICES.get(phase, [0]),
            }
        )
    return {
        "phases": PHASE_ORDER,
        "steps": steps,
        "count": len(steps),
        "note": "Preview stepper mirrors Wokwi palette only; Lab engine remains SOS authority",
        "evidence_profile": "Wokwi",
    }


def visual_state(
    phase: str,
    *,
    hold_down: bool = False,
    preview: bool = False,
    annotation: str | None = None,
) -> dict[str, Any]:
    pixels = pixels_for_phase(phase)
    note = annotation or PHASE_ANNOTATIONS.get(phase)
    serial_payload: dict[str, Any] = {
        "type": "phase_preview" if preview else "phase",
        "phase": phase,
        "pattern": PHASE_PATTERN.get(phase),
        "simulated": True,
        "source": "lab_bridge",
    }
    if note:
        serial_payload["annotation"] = note
    if preview:
        serial_payload["preview"] = True
        serial_payload["authority"] = "visual_subset_only"
    return {
        "phase": phase,
        "pattern": PHASE_PATTERN.get(phase, "idle_dim"),
        "button": {"id": "sos", "pressed": hold_down, "label": "SIM SOS"},
        "pixels": pixels,
        "preview": preview,
        "annotation": note,
        "serial_lines": [json.dumps(serial_payload)],
        "limits": {
            "ble": False,
            "i2s": False,
            "nicla_target": False,
            "real_notification": False,
        },
    }


def load_embed_config() -> dict[str, Any]:
    """WB-022 — optional published Wokwi project for elements iframe."""
    path = WOKWI_DIR / "embed.json"
    default: dict[str, Any] = {
        "schema_version": "1",
        "project_id": None,
        "embed_base": "https://wokwi.com/projects/",
        "height_px": 360,
    }
    if not path.is_file():
        return default
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {**default, "error": "embed.json invalid JSON"}
    return {**default, **data}


def open_links() -> dict[str, Any]:
    """Honest open paths for WB-015/022 (no fake full-system embed claim)."""
    abs_dir = str(WOKWI_DIR)
    diagram = WOKWI_DIR / "diagram.json"
    emb = load_embed_config()
    project_id = emb.get("project_id")
    available = bool(project_id) and str(project_id).strip() not in ("", "null", "None")
    base = str(emb.get("embed_base") or "https://wokwi.com/projects/").rstrip("/") + "/"
    iframe_src = f"{base}{project_id}" if available else None
    return {
        "project_abs": abs_dir,
        "diagram_abs": str(diagram) if diagram.is_file() else None,
        "vscode_folder_uri": f"vscode://file{abs_dir}",
        "vscode_hint": "Install Wokwi for VS Code → Open Folder → simulation/wokwi → Start Simulator",
        "elements_embed": {
            "available": available,
            "project_id": project_id if available else None,
            "iframe_src": iframe_src,
            "height_px": int(emb.get("height_px") or 360),
            "config_path": "simulation/wokwi/embed.json",
            "reason": None
            if available
            else "Set simulation/wokwi/embed.json project_id after publishing to Wokwi.com; Lab panel remains authority",
            "docs": "https://docs.wokwi.com/guides/diagram-format",
            "publish_hint": "In Wokwi for VS Code: Share / Save to Wokwi.com → paste project ID into embed.json",
        },
        "cli": "cd simulation/wokwi && pio run -e sim -c platformio_local.ini && (command -v wokwi-cli >/dev/null && wokwi-cli . || echo 'wokwi-cli optional')",
        "web_panel": "Device Simulator → Wokwi panel (Lab-synced visual subset)",
    }


def firmware_hash() -> dict[str, Any]:
    firmware = WOKWI_DIR / ".pio" / "build" / "sim" / "firmware.bin"
    if not firmware.is_file():
        return {"present": False, "sha256": None, "bytes": 0, "path": None}
    data = firmware.read_bytes()
    return {
        "present": True,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "path": str(firmware.relative_to(ROOT)),
    }


def _which_pio() -> str | None:
    for cand in (
        shutil.which("pio"),
        str(Path.home() / "Library/Python/3.9/bin/pio"),
        str(Path.home() / "Library/Python/3.12/bin/pio"),
        str(Path.home() / ".platformio/penv/bin/pio"),
    ):
        if cand and Path(cand).is_file() and os.access(cand, os.X_OK):
            return cand
    return None


def _which_wokwi_cli() -> str | None:
    for cand in (
        shutil.which("wokwi-cli"),
        str(Path.home() / ".wokwi" / "bin" / "wokwi-cli"),
        str(Path.home() / "bin" / "wokwi-cli"),
        str(Path.home() / ".local" / "bin" / "wokwi-cli"),
    ):
        if cand and Path(cand).is_file() and os.access(cand, os.X_OK):
            return cand
    return None


def doctor() -> dict[str, Any]:
    """Toolchain + project checks (WB-017)."""
    checks: list[dict[str, Any]] = []
    pio = _which_pio()
    if pio:
        try:
            ver = subprocess.check_output(
                [pio, "--version"], text=True, timeout=15
            ).strip()
        except Exception as e:  # pragma: no cover
            ver = f"error:{e}"
        checks.append({"id": "platformio", "ok": True, "detail": f"{ver} ({pio})"})
    else:
        checks.append({"id": "platformio", "ok": False, "detail": "pio not on PATH"})

    wokwi_cli = _which_wokwi_cli()
    checks.append(
        {
            "id": "wokwi_cli",
            "ok": bool(wokwi_cli),
            "detail": wokwi_cli or "optional — not installed",
            "optional": True,
        }
    )

    for name, path in (
        ("diagram.json", WOKWI_DIR / "diagram.json"),
        ("platformio.ini", WOKWI_DIR / "platformio.ini"),
        ("wokwi.toml", WOKWI_DIR / "wokwi.toml"),
        ("main.cpp", WOKWI_DIR / "src" / "main.cpp"),
        ("GPIO_MAP.md", WOKWI_DIR / "GPIO_MAP.md"),
    ):
        checks.append(
            {
                "id": f"file:{name}",
                "ok": path.is_file(),
                "detail": str(path.relative_to(ROOT)) if path.is_file() else "missing",
            }
        )

    fw = firmware_hash()
    checks.append(
        {
            "id": "firmware.bin",
            "ok": fw["present"],
            "detail": f"sha256={fw['sha256']} bytes={fw['bytes']}"
            if fw["present"]
            else "not built — pio run -e sim",
        }
    )

    fid = fidelity_report()
    checks.append(
        {
            "id": "pixel_fidelity",
            "ok": fid.get("ok", False),
            "detail": "Lab PHASE_PIXEL indices match Wokwi palette"
            if fid.get("ok")
            else str(fid.get("mismatches")),
        }
    )

    emb = open_links()["elements_embed"]
    checks.append(
        {
            "id": "embed_config",
            "ok": True,
            "detail": (
                f"project_id={emb.get('project_id')} iframe ready"
                if emb.get("available")
                else "project_id unset — local Lab panel only (optional)"
            ),
            "optional": True,
        }
    )
    catalog = phase_catalog()
    checks.append(
        {
            "id": "phase_catalog",
            "ok": catalog["count"] >= 6,
            "detail": f"{catalog['count']} phases · stepper ready",
        }
    )

    required_ok = all(c["ok"] for c in checks if not c.get("optional"))
    return {
        "ok": required_ok,
        "checks": checks,
        "firmware": fw,
        "open": open_links(),
        "embed": emb,
        "phases": catalog,
        "fidelity": fid,
        "profile": "SIM",
        "evidence_profile": "Wokwi",
    }


def project_status() -> dict[str, Any]:
    fw = firmware_hash()
    diagram = WOKWI_DIR / "diagram.json"
    return {
        "project_dir": str(WOKWI_DIR.relative_to(ROOT)),
        "diagram_present": diagram.is_file(),
        "firmware_built": fw["present"],
        "firmware_path": fw["path"],
        "firmware_sha256": fw["sha256"],
        "platformio_ini": (WOKWI_DIR / "platformio.ini").is_file(),
        "wokwi_toml": (WOKWI_DIR / "wokwi.toml").is_file(),
        "open": open_links(),
        "open_hints": {
            "vscode": open_links()["vscode_hint"],
            "web": "Device Simulator embeds diagram + syncs pixels from Lab engine",
            "cli": open_links()["cli"],
        },
        "profile": "SIM",
        "evidence_profile": "Wokwi",
        "note": "Visual subset only — behavioral SOS authority remains Lab engine",
    }


def headless_smoke(*, run_pio: bool = False) -> dict[str, Any]:
    """PIO/wokwi-cli smoke for evidence (WB-020)."""
    steps: list[dict[str, Any]] = []
    pio = _which_pio()
    if run_pio and pio:
        try:
            out = subprocess.check_output(
                [pio, "run", "-e", "sim"],
                cwd=str(WOKWI_DIR),
                text=True,
                timeout=300,
                stderr=subprocess.STDOUT,
            )
            steps.append(
                {
                    "id": "pio_run",
                    "ok": True,
                    "detail": out[-400:] if len(out) > 400 else out,
                }
            )
        except subprocess.CalledProcessError as e:
            steps.append(
                {
                    "id": "pio_run",
                    "ok": False,
                    "detail": (e.output or str(e))[-400:],
                }
            )
    elif run_pio:
        steps.append({"id": "pio_run", "ok": False, "detail": "pio missing"})
    else:
        steps.append(
            {
                "id": "pio_run",
                "ok": True,
                "detail": "skipped (use run_pio=true); firmware presence checked",
                "skipped": True,
            }
        )

    fw = firmware_hash()
    steps.append(
        {
            "id": "firmware_hash",
            "ok": fw["present"],
            "detail": fw,
        }
    )

    wokwi_cli = _which_wokwi_cli()
    if wokwi_cli:
        steps.append(
            {
                "id": "wokwi_cli",
                "ok": True,
                "detail": f"present at {wokwi_cli} (not executed — needs diagram/runtime)",
                "optional": True,
            }
        )
    else:
        steps.append(
            {
                "id": "wokwi_cli",
                "ok": True,
                "detail": "not installed (optional)",
                "optional": True,
                "skipped": True,
            }
        )

    ok = all(s["ok"] for s in steps if not s.get("optional"))
    return {
        "ok": ok,
        "steps": steps,
        "firmware": fw,
        "profile": "SIM",
        "evidence_profile": "Wokwi",
    }
