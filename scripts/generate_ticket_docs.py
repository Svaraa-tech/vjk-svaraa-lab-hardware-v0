#!/usr/bin/env python3
"""Create docs/tickets/<key>/ticket.md for any seed ticket missing one (future-safe)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def key_of(row: dict) -> str:
    if row.get("display_key"):
        return str(row["display_key"])
    if row.get("ticket_id"):
        return str(row["ticket_id"])
    return str(row.get("source_id") or "UNKNOWN")


def main() -> None:
    data = json.loads((ROOT / "data/seeds/board_bootstrap_v0.1.json").read_text())
    out_root = ROOT / "docs" / "tickets"
    created = 0
    for ns, rows in (
        ("original", data.get("original_tickets", [])),
        ("workbench", data.get("proposed_workbench_tickets", [])),
    ):
        for t in rows:
            key = key_of(t)
            d = out_root / key
            d.mkdir(parents=True, exist_ok=True)
            path = d / "ticket.md"
            if path.exists():
                continue
            summary = t.get("summary") or key
            work_type = t.get("work_type") or (
                "Workbench" if ns == "workbench" else "Sub-task"
            )
            desc = t.get("description_source") or ""
            if ns == "workbench" and not desc:
                links = ",".join(t.get("links") or [])
                desc = f"Workbench addition; links {links}" if links else "Workbench ticket."
            deps = t.get("plan_dependencies") or ",".join(t.get("links") or []) or ""
            path.write_text(
                f"""# {key} — {summary}

```yaml
ticket_id: {key}
work_type: {work_type}
source_namespace: {ns}
workflow_state: {t.get('workflow_state') or 'Backlog'}
implementation_state: {t.get('implementation_state') or 'not_started'}
profile: SIM
plan_dependencies: {deps or '—'}
```

## Problem and user outcome

{desc}

## Source scope

- Board: `.workbench/lab.db`
- Execution/results: add implementation.md / tests.md / review.md when work runs
- Evidence: `evidence/{key}/`
"""
            )
            created += 1
    print(f"created={created}")


if __name__ == "__main__":
    main()
