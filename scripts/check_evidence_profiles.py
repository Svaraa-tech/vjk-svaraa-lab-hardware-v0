#!/usr/bin/env python3
"""Fail if evidence claims physical pass without allowed profile metadata."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {"BENCH", "Phone", "Field", "Electrical"}


def main() -> int:
    bad = []
    for path in (ROOT / "evidence").rglob("*.json"):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        profile = str(data.get("evidence_profile") or data.get("profile") or "")
        result = str(data.get("result") or data.get("status") or "").lower()
        host_only = data.get("host_only") or data.get("simulated") or profile.upper() in {
            "SIM",
            "HOST",
        }
        if profile in FORBIDDEN and result in {"passed", "pass", "ok"} and host_only:
            bad.append(str(path.relative_to(ROOT)))
        # Explicit ban: physical_pass true under SIM
        if data.get("physical_pass") and str(data.get("profile", "SIM")).upper() in {
            "SIM",
            "HOST",
        }:
            bad.append(str(path.relative_to(ROOT)) + " (physical_pass under SIM)")
    if bad:
        print("FORBIDDEN physical claims in SIM/host evidence:")
        for b in bad:
            print(" -", b)
        return 1
    print("evidence profile guard OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
