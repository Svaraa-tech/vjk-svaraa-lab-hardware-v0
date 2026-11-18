"""Location / pressure adapters — honest null/stale (SV0-04.* SIM)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class PressureReading:
    pressure_hpa: float
    internal_temp_c: float | None
    relative_altitude_m: float | None
    stale: bool = False
    fault: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "pressure_hpa": self.pressure_hpa,
            "internal_temp_c": self.internal_temp_c,
            "body_temperature": None,  # never present internal as body temp
            "relative_altitude_m": self.relative_altitude_m,
            "stale": self.stale,
            "fault": self.fault,
            "note": "internal_temp is die/board temperature, not body temperature",
            "simulated": True,
        }


@dataclass
class LocationFix:
    source: str = "none"  # none | gnss | phone | tag
    valid: bool = False
    latitude: float | None = None
    longitude: float | None = None
    accuracy_m: float | None = None
    fix_at_ms: int | None = None
    age_ms: int | None = None
    label: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "valid": self.valid,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accuracy_m": self.accuracy_m,
            "fix_at_ms": self.fix_at_ms,
            "age_ms": self.age_ms,
            "label": self.label,
            "simulated": True,
        }

    def for_sos_payload(self) -> dict[str, Any]:
        """Schema-shaped location for device events."""
        if self.source == "none" or not self.valid:
            return {
                "source": "none",
                "valid": False,
                "latitude": None,
                "longitude": None,
                "accuracy_m": None,
                "fix_at": None,
                "age_ms": None,
            }
        src = "phone" if self.source == "phone" else "gnss"
        return {
            "source": src,
            "valid": True,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accuracy_m": self.accuracy_m,
            "fix_at": None,
            "age_ms": self.age_ms,
        }


@dataclass
class LocationService:
    pressure: PressureReading = field(
        default_factory=lambda: PressureReading(1013.25, 28.5, 0.0)
    )
    fix: LocationFix = field(default_factory=LocationFix)
    tags: dict[str, dict[str, Any]] = field(default_factory=dict)
    enrichments: list[dict[str, Any]] = field(default_factory=list)

    def set_no_fix(self) -> LocationFix:
        self.fix = LocationFix(source="none", valid=False)
        return self.fix

    def set_indoor_null(self) -> LocationFix:
        # Indoor: preserve nulls — do not invent
        return self.set_no_fix()

    def set_gnss(
        self,
        lat: float,
        lon: float,
        *,
        accuracy_m: float,
        now_ms: int,
        age_ms: int = 0,
    ) -> LocationFix:
        self.fix = LocationFix(
            source="gnss",
            valid=True,
            latitude=lat,
            longitude=lon,
            accuracy_m=accuracy_m,
            fix_at_ms=now_ms,
            age_ms=age_ms,
        )
        return self.fix

    def set_phone_fix(
        self, lat: float, lon: float, *, accuracy_m: float, now_ms: int
    ) -> LocationFix:
        self.fix = LocationFix(
            source="phone",
            valid=True,
            latitude=lat,
            longitude=lon,
            accuracy_m=accuracy_m,
            fix_at_ms=now_ms,
            age_ms=0,
            label="phone",
        )
        return self.fix

    def mark_pressure_stale(self, stale: bool = True) -> None:
        self.pressure.stale = stale

    def mark_pressure_fault(self, fault: bool = True) -> None:
        self.pressure.fault = fault

    def persist_tag(
        self, *, label: str, notes: str, lat: float | None, lon: float | None
    ) -> dict[str, Any]:
        """Offline tag persists once by ID (SV0-04.03)."""
        tag_id = str(uuid.uuid4())
        if any(t.get("label") == label for t in self.tags.values()):
            # same label — return existing (persist once semantics for identical label)
            for tid, t in self.tags.items():
                if t["label"] == label:
                    return {**t, "duplicate": True}
        tag = {
            "tag_id": tag_id,
            "label": label,
            "notes": notes,
            "latitude": lat,
            "longitude": lon,
            "provenance": "offline_tag",
            "immutable": True,
        }
        self.tags[tag_id] = tag
        return tag

    def enrich_incident(
        self,
        *,
        incident_id: str,
        now_ms: int,
        existing_fix_at_ms: int | None,
    ) -> dict[str, Any] | None:
        """
        SOS already sent — enrich with new event ID when fix arrives.
        Late stale observation cannot replace newer fix (SV0-04.04).
        """
        if not self.fix.valid:
            return None
        if (
            existing_fix_at_ms is not None
            and self.fix.fix_at_ms is not None
            and self.fix.fix_at_ms < existing_fix_at_ms
        ):
            return {
                "applied": False,
                "reason": "stale_observation_rejected",
                "incident_id": incident_id,
            }
        event_id = str(uuid.uuid4())
        rec = {
            "applied": True,
            "event_id": event_id,
            "incident_id": incident_id,
            "kind": "location.updated",
            "location": self.fix.as_dict(),
            "at_ms": now_ms,
            "note": "enrichment after SOS; trigger path did not wait for GPS",
        }
        self.enrichments.append(rec)
        return rec

    def snapshot(self) -> dict[str, Any]:
        return {
            "pressure": self.pressure.as_dict(),
            "fix": self.fix.as_dict(),
            "tags": list(self.tags.values()),
            "enrichments": list(self.enrichments),
            "sos_waits_for_gps": False,
            "profile": "SIM",
        }
