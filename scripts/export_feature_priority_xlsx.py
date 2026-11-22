#!/usr/bin/env python3
"""Export Svaraa features × priority × Arduino/Lab parts to a formatted Excel workbook."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
HW_PATH = ROOT / "apps/workbench/src/data/hardwareParts.ts"
FEAT_PATH = ROOT / "apps/workbench/src/data/featureList.ts"
OUT = ROOT / "Svaraa_Feature_Priority_Hardware.xlsx"

PILLAR_ORDER = [
    "Recite",
    "Respond",
    "Remind",
    "Rescue",
    "Recall",
    "Repository",
    "Riddle",
    "Platform",
]
PILLAR_NUM = {
    "Recite": "01",
    "Respond": "02",
    "Remind": "03",
    "Rescue": "04",
    "Recall": "05",
    "Repository": "06",
    "Riddle": "07",
    "Platform": "··",
}
PILLAR_TAG = {
    "Recite": "Prayer, recitation & ambient sound",
    "Respond": "Natural conversation → support",
    "Remind": "Medicine, water & routines",
    "Rescue": "SOS to the care circle",
    "Recall": "Briefing, plans & follow-through",
    "Repository": "Stories & notes with permission",
    "Riddle": "Gentle movement & cognitive play",
    "Platform": "Pendant UX, privacy, family app & HW",
}
PRI_ORDER = ["P1", "P2", "P3"]
PRI_LABEL = {
    "P1": "P1 · Must have",
    "P2": "P2 · Need to have",
    "P3": "P3 · Good to have",
}
MAT_LABEL = {
    "v0_bench": "V0 Lab / Wokwi now",
    "product_path": "Product path on this BOM",
    "needs_phone": "Needs paired phone / BLE",
    "needs_cloud": "Needs cloud + family app",
    "later_gated": "Later / gated HW",
}

# Controllers / modem DKs — MCU-equivalent column left blank for custom PCB mapping
CONTROLLER_IDS = {"B01", "B02", "B29", "B30"}

HEADERS = [
    "Svaraa #",
    "Svaraa",
    "Priority",
    "Priority level",
    "Feature ID",
    "Feature name",
    "Summary",
    "Why for elders",
    "Maturity",
    "Also Svaraas",
    "BOM IDs",
    "Arduino / Lab sensors & parts needed",
    "Bench controllers referenced (Lab today)",
    "Microcontroller equivalent (custom PCB / Svaraa Pendant)",
]

COL_WIDTHS = {
    "A": 10,
    "B": 12,
    "C": 10,
    "D": 18,
    "E": 12,
    "F": 36,
    "G": 42,
    "H": 36,
    "I": 22,
    "J": 18,
    "K": 18,
    "L": 55,
    "M": 40,
    "N": 42,
}


def parse_parts(text: str) -> dict[str, dict[str, str]]:
    parts: dict[str, dict[str, str]] = {}
    for m in re.finditer(
        r'id:\s*"(B\d+)",\s*name:\s*"([^"]+)",\s*category:\s*"([^"]+)",\s*role:\s*"([^"]+)"',
        text,
    ):
        pid, name, cat, role = m.groups()
        parts[pid] = {"name": name, "category": cat, "role": role}
    return parts


def _string_field(obj: str, field: str) -> str:
    m = re.search(rf'{field}:\s*"((?:[^"\\]|\\.)*)"', obj)
    if m:
        return m.group(1).replace("\\n", " ").replace('\\"', '"')
    m = re.search(rf"{field}:\s*\n\s*\"([^\"]*)\"", obj)
    if m:
        return m.group(1)
    m = re.search(rf"{field}:\s*`([^`]*)`", obj)
    if m:
        return m.group(1).replace("\n", " ")
    return ""


def parse_features(text: str) -> list[dict]:
    m = re.search(r"export const FEATURE_LIST[^=]*=\s*\[", text)
    if not m:
        raise SystemExit("FEATURE_LIST not found")
    start = m.end()
    i, depth = start, 1
    while i < len(text) and depth:
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
        i += 1
    body = text[start : i - 1]
    objs = re.split(r"\n  \{", body)

    features: list[dict] = []
    for o in objs:
        mid = re.search(r'id:\s*"([^"]+)"', o)
        mp = re.search(r'pillar:\s*"([^"]+)"', o)
        mpr = re.search(r'priority:\s*"(P[123])"', o)
        mn = re.search(r'name:\s*"([^"]+)"', o)
        mm = re.search(r'maturity:\s*"([^"]+)"', o)
        mh = re.search(r"hardware:\s*\[([^\]]*)\]", o)
        also = re.search(r"alsoSvaraas:\s*\[([^\]]*)\]", o)
        if not (mid and mp and mpr and mn):
            continue
        hw_ids = re.findall(r'"(B\d+)"', mh.group(1) if mh else "")
        also_list = re.findall(r'"([^"]+)"', also.group(1) if also else "")
        features.append(
            {
                "id": mid.group(1),
                "pillar": mp.group(1),
                "priority": mpr.group(1),
                "name": mn.group(1),
                "summary": _string_field(o, "summary"),
                "elderWhy": _string_field(o, "elderWhy"),
                "maturity": mm.group(1) if mm else "",
                "hardware": hw_ids,
                "also": also_list,
            }
        )
    return features


def arduino_parts_for(hw_ids: list[str], parts: dict) -> str:
    lines = []
    for hid in hw_ids:
        p = parts.get(hid)
        if not p:
            lines.append(f"{hid} (unknown)")
            continue
        if hid in CONTROLLER_IDS:
            continue
        lines.append(f"{hid} — {p['name']} ({p['role']})")
    if lines:
        return "; ".join(lines)
    return "— (app/cloud / no discrete Lab sensor; or MCU-only)"


def controllers_used(hw_ids: list[str], parts: dict) -> str:
    lines = []
    for hid in hw_ids:
        if hid in CONTROLLER_IDS and hid in parts:
            p = parts[hid]
            lines.append(f"{hid} — {p['name']} ({p['role']})")
    return "; ".join(lines)


def main() -> None:
    parts = parse_parts(HW_PATH.read_text())
    features = parse_features(FEAT_PATH.read_text())
    if len(features) != 127:
        raise SystemExit(f"Expected 127 features, got {len(features)}")

    features.sort(
        key=lambda f: (
            PILLAR_ORDER.index(f["pillar"]) if f["pillar"] in PILLAR_ORDER else 99,
            PRI_ORDER.index(f["priority"]),
            f["id"],
        )
    )

    thin = Border(
        left=Side(style="thin", color="D0D5DD"),
        right=Side(style="thin", color="D0D5DD"),
        top=Side(style="thin", color="D0D5DD"),
        bottom=Side(style="thin", color="D0D5DD"),
    )
    header_fill = PatternFill("solid", fgColor="1B3A4B")
    header_font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
    title_font = Font(name="Calibri", bold=True, size=16, color="1B3A4B")
    subtitle_font = Font(name="Calibri", size=10, color="475467")
    wrap = Alignment(wrap_text=True, vertical="top")
    center = Alignment(wrap_text=True, vertical="center", horizontal="center")
    pri_fill = {
        "P1": PatternFill("solid", fgColor="FCE8E8"),
        "P2": PatternFill("solid", fgColor="FFF6E0"),
        "P3": PatternFill("solid", fgColor="F2F4F7"),
    }
    pri_font = {
        "P1": Font(name="Calibri", bold=True, color="912018", size=10),
        "P2": Font(name="Calibri", bold=True, color="93370D", size=10),
        "P3": Font(name="Calibri", bold=True, color="475467", size=10),
    }
    pillar_fills = {
        "Recite": PatternFill("solid", fgColor="EEF4FF"),
        "Respond": PatternFill("solid", fgColor="ECFDF3"),
        "Remind": PatternFill("solid", fgColor="FEF6EE"),
        "Rescue": PatternFill("solid", fgColor="FEF3F2"),
        "Recall": PatternFill("solid", fgColor="F4F3FF"),
        "Repository": PatternFill("solid", fgColor="FDF2FA"),
        "Riddle": PatternFill("solid", fgColor="F0F9FF"),
        "Platform": PatternFill("solid", fgColor="F8FAFC"),
    }
    mcu_fill = PatternFill("solid", fgColor="FFFBEB")

    def set_widths(ws) -> None:
        for col, w in COL_WIDTHS.items():
            ws.column_dimensions[col].width = w

    def write_feature_row(ws, row: int, f: dict) -> None:
        vals = [
            PILLAR_NUM[f["pillar"]],
            f["pillar"],
            f["priority"],
            PRI_LABEL[f["priority"]],
            f["id"],
            f["name"],
            f["summary"],
            f["elderWhy"],
            MAT_LABEL.get(f["maturity"], f["maturity"]),
            ", ".join(f["also"]) if f["also"] else "—",
            ", ".join(f["hardware"]) if f["hardware"] else "—",
            arduino_parts_for(f["hardware"], parts),
            controllers_used(f["hardware"], parts) or "—",
            "",
        ]
        for col, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=col, value=v)
            cell.border = thin
            cell.alignment = wrap
            cell.font = Font(name="Calibri", size=10)
        for col in (3, 4):
            ws.cell(row=row, column=col).fill = pri_fill[f["priority"]]
            ws.cell(row=row, column=col).font = pri_font[f["priority"]]
            ws.cell(row=row, column=col).alignment = center
        ws.cell(row=row, column=1).fill = pillar_fills[f["pillar"]]
        ws.cell(row=row, column=2).fill = pillar_fills[f["pillar"]]
        ws.cell(row=row, column=1).alignment = center
        ws.cell(row=row, column=2).alignment = center
        ws.cell(row=row, column=5).font = Font(
            name="Calibri", bold=True, size=10, color="1B3A4B"
        )
        mcu = ws.cell(row=row, column=14)
        mcu.fill = mcu_fill
        mcu.alignment = wrap
        ws.row_dimensions[row].height = 48

    wb = Workbook()

    # ----- Cover -----
    cover = wb.active
    cover.title = "Cover & legend"
    cover["A1"] = "Svaraa V0 — Feature priorities × Arduino / Lab hardware"
    cover["A1"].font = title_font
    cover.merge_cells("A1:F1")
    cover["A2"] = (
        "Features ordered by Svaraa (01→07 + Platform), then priority P1 Must → P2 Need → P3 Nice. "
        "Arduino / Lab parts are resolved from the V0 BOM (B01–B32). "
        "Controller boards (Nano ESP32, Nicla Voice, later Nordic DKs) are listed under "
        "“Bench controllers” only — the Microcontroller equivalent column is intentionally blank "
        "for custom PCB / Pendant mapping."
    )
    cover["A2"].font = subtitle_font
    cover["A2"].alignment = wrap
    cover.merge_cells("A2:F2")
    cover.row_dimensions[2].height = 60

    cover["A4"] = "Priority definitions"
    cover["A4"].font = Font(name="Calibri", bold=True, size=12, color="1B3A4B")
    cover["A5"] = "Code"
    cover["B5"] = "Level"
    cover["C5"] = "Meaning"
    for c in range(1, 4):
        cover.cell(5, c).fill = header_fill
        cover.cell(5, c).font = header_font
    defs = [
        (
            "P1",
            "Must have",
            "Safety, trust, or Free-tier promise elders/families cannot ship without",
        ),
        (
            "P2",
            "Need to have",
            "Daily companion value — stickiness and caregiver load relief",
        ),
        (
            "P3",
            "Good to have",
            "Polish, festivals, later tiers (cellular, Find My–class, Diamond, lab tooling)",
        ),
    ]
    for i, (code, level, meaning) in enumerate(defs, 6):
        cover.cell(i, 1, code).fill = pri_fill[code]
        cover.cell(i, 1).font = pri_font[code]
        cover.cell(i, 2, level)
        cover.cell(i, 3, meaning)

    cover["A10"] = "Workbook sheets"
    cover["A10"].font = Font(name="Calibri", bold=True, size=12, color="1B3A4B")
    cover["A11"] = "All features — master table (filterable)"
    cover["A12"] = "One sheet per Svaraa — same columns, P1→P3 within that Svaraa"
    cover["A13"] = "BOM reference — full B01–B32 part names for lookup"

    cover["A15"] = "Counts"
    cover["A15"].font = Font(name="Calibri", bold=True, size=12, color="1B3A4B")
    for c, h in enumerate(["Svaraa", "P1 Must", "P2 Need", "P3 Nice", "Total"], 1):
        cover.cell(16, c, h).fill = header_fill
        cover.cell(16, c).font = header_font

    counts: dict[str, Counter] = defaultdict(Counter)
    for f in features:
        counts[f["pillar"]][f["priority"]] += 1
    r = 17
    for p in PILLAR_ORDER:
        cover.cell(r, 1, f"{PILLAR_NUM[p]} {p}").fill = pillar_fills[p]
        cover.cell(r, 2, counts[p]["P1"])
        cover.cell(r, 3, counts[p]["P2"])
        cover.cell(r, 4, counts[p]["P3"])
        cover.cell(r, 5, sum(counts[p].values()))
        r += 1
    cover.cell(r, 1, "TOTAL").font = Font(bold=True)
    cover.cell(r, 2, sum(counts[p]["P1"] for p in PILLAR_ORDER)).font = Font(bold=True)
    cover.cell(r, 3, sum(counts[p]["P2"] for p in PILLAR_ORDER)).font = Font(bold=True)
    cover.cell(r, 4, sum(counts[p]["P3"] for p in PILLAR_ORDER)).font = Font(bold=True)
    cover.cell(r, 5, len(features)).font = Font(bold=True)

    cover["A27"] = "Source"
    cover["A27"].font = Font(bold=True, size=12, color="1B3A4B")
    cover["A28"] = str(FEAT_PATH.relative_to(ROOT))
    cover["A29"] = str(HW_PATH.relative_to(ROOT))
    cover["A30"] = "Generated for Svaraa Lab Hardware V0 — svaraa.ai"

    for col, w in {"A": 28, "B": 14, "C": 14, "D": 14, "E": 10, "F": 40}.items():
        cover.column_dimensions[col].width = w

    # ----- All features -----
    all_ws = wb.create_sheet("All features", 1)
    for col, h in enumerate(HEADERS, 1):
        cell = all_ws.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cell.border = thin
    all_ws.row_dimensions[1].height = 36
    set_widths(all_ws)
    for i, f in enumerate(features, 2):
        write_feature_row(all_ws, i, f)
    last = 1 + len(features)
    all_ws.auto_filter.ref = f"A1:{get_column_letter(len(HEADERS))}{last}"
    all_ws.freeze_panes = "F2"

    # ----- Per-Svaraa -----
    for p in PILLAR_ORDER:
        title = f"{PILLAR_NUM[p]} {p}"[:31]
        ws = wb.create_sheet(title)
        ws.merge_cells("A1:N1")
        banner = ws["A1"]
        banner.value = (
            f"Svaraa {PILLAR_NUM[p]} · {p} — {PILLAR_TAG[p]}  |  "
            "Ordered P1 Must → P2 Need → P3 Nice"
        )
        banner.font = Font(name="Calibri", bold=True, size=12, color="1B3A4B")
        banner.fill = pillar_fills[p]
        banner.alignment = Alignment(vertical="center", wrap_text=True)
        ws.row_dimensions[1].height = 28

        for col, h in enumerate(HEADERS, 1):
            cell = ws.cell(row=2, column=col, value=h)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(
                wrap_text=True, vertical="center", horizontal="center"
            )
            cell.border = thin
        ws.row_dimensions[2].height = 36
        set_widths(ws)
        ws.freeze_panes = "F3"

        subset = [f for f in features if f["pillar"] == p]
        row = 3
        cur_pri = None
        for f in subset:
            if cur_pri is not None and f["priority"] != cur_pri:
                for c in range(1, 15):
                    ws.cell(row=row, column=c).fill = PatternFill(
                        "solid", fgColor="E4E7EC"
                    )
                ws.row_dimensions[row].height = 8
                row += 1
            cur_pri = f["priority"]
            write_feature_row(ws, row, f)
            row += 1
        ws.auto_filter.ref = f"A2:N{row - 1}"

    # ----- BOM -----
    bom = wb.create_sheet("BOM reference")
    bom["A1"] = "V0 Lab BOM — Arduino / bench parts (B01–B32)"
    bom["A1"].font = title_font
    bom.merge_cells("A1:E1")
    bom_headers = [
        "BOM ID",
        "Name",
        "Category",
        "Role",
        "Used as MCU candidate?",
    ]
    for c, h in enumerate(bom_headers, 1):
        cell = bom.cell(2, c, h)
        cell.fill = header_fill
        cell.font = header_font
        cell.border = thin
    for i, pid in enumerate(sorted(parts.keys(), key=lambda x: int(x[1:])), 3):
        p = parts[pid]
        bom.cell(i, 1, pid).border = thin
        bom.cell(i, 2, p["name"]).border = thin
        bom.cell(i, 3, p["category"]).border = thin
        bom.cell(i, 4, p["role"]).border = thin
        is_mcu = (
            "Yes — leave MCU equivalent blank for now"
            if pid in CONTROLLER_IDS
            else "No — listed under Arduino / Lab parts"
        )
        bom.cell(i, 5, is_mcu).border = thin
        if pid in CONTROLLER_IDS:
            for c in range(1, 6):
                bom.cell(i, c).fill = mcu_fill
    for col, w in {"A": 10, "B": 48, "C": 16, "D": 32, "E": 42}.items():
        bom.column_dimensions[col].width = w
    bom.freeze_panes = "A3"
    bom.auto_filter.ref = f"A2:E{2 + len(parts)}"

    wb.save(OUT)
    print(f"Wrote {OUT}")
    print(f"Features {len(features)} · Parts {len(parts)}")
    print(
        "Priority totals",
        {
            "P1": sum(1 for f in features if f["priority"] == "P1"),
            "P2": sum(1 for f in features if f["priority"] == "P2"),
            "P3": sum(1 for f in features if f["priority"] == "P3"),
        },
    )


def export_mcu_ts_from_xlsx(xlsx: Path | None = None) -> Path:
    """Sync column N (MCU equivalent) from the filled workbook into mcuEquivalents.ts."""
    from openpyxl import load_workbook

    path = xlsx or (ROOT / "Svaraa_Feature_Priority_Hardware.xlsx")
    wb = load_workbook(path, data_only=True)
    ws = wb["All features"]
    mapping: dict[str, str] = {}
    for r in range(2, ws.max_row + 1):
        fid = ws.cell(r, 5).value
        mcu = ws.cell(r, 14).value
        if not fid:
            continue
        text = " ".join(str(mcu).split()) if mcu else ""
        mapping[str(fid)] = text

    out = ROOT / "apps/workbench/src/data/mcuEquivalents.ts"
    lines = [
        "/** Pendant / custom-PCB microcontroller equivalents — from Svaraa_Feature_Priority_Hardware.xlsx */",
        "",
        "export const MCU_EQUIVALENTS: Record<string, string> = {",
    ]
    for k in sorted(mapping.keys()):
        v = mapping[k].replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'  "{k}": "{v}",')
    lines.extend(
        [
            "};",
            "",
            "export function featureMcuEquivalent(featureId: string): string | undefined {",
            "  const v = MCU_EQUIVALENTS[featureId]?.trim();",
            "  return v || undefined;",
            "}",
            "",
        ]
    )
    out.write_text("\n".join(lines) + "\n")
    return out


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--sync-mcu":
        path = export_mcu_ts_from_xlsx()
        print(f"Synced MCU map → {path}")
    else:
        main()
