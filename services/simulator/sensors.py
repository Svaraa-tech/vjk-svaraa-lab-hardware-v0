"""Synthetic sensor streams for SIM panels (WB-007) — not clinical/physical accuracy."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SensorBus:
    t_ms: int = 0
    pressure_hpa: float = 1013.25
    gnss_valid: bool = False
    accel_mg: tuple[float, float, float] = (0.0, 0.0, 1000.0)
    privacy: bool = False
    samples: list[dict[str, Any]] = field(default_factory=list)

    def step(self, dt_ms: int = 100) -> dict[str, Any]:
        self.t_ms += dt_ms
        # gentle synthetic wander — labeled simulated
        self.pressure_hpa = 1013.25 + 0.5 * math.sin(self.t_ms / 5000.0)
        ax = 40.0 * math.sin(self.t_ms / 800.0)
        self.accel_mg = (ax, 0.0, 1000.0)
        sample = {
            "t_ms": self.t_ms,
            "bmp390": {
                "pressure_hpa": round(self.pressure_hpa, 3),
                "addr": "0x77",
                "valid": True,
                "simulated": True,
            },
            "gnss": {
                "source": "none",
                "valid": False,
                "latitude": None,
                "longitude": None,
                "addr": "0x42",
                "simulated": True,
                "note": "null/stale honest — no invented coords",
            },
            "bmi270": {
                "accel_mg": [round(v, 1) for v in self.accel_mg],
                "valid": True,
                "simulated": True,
                "clinical_claim": False,
            },
            "privacy_effective": self.privacy,
        }
        self.samples.append(sample)
        self.samples = self.samples[-120:]
        return sample

    def snapshot(self) -> dict[str, Any]:
        latest = self.samples[-1] if self.samples else self.step(0)
        return {
            "latest": latest,
            "history_len": len(self.samples),
            "history": self.samples[-40:],
            "profile": "SIM",
            "simulated": True,
        }
