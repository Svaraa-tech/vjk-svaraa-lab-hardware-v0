#!/usr/bin/env python3
"""Export read-only board JSON for GitHub Pages (no Lab API)."""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "api"))

from app import board_db  # noqa: E402


def main() -> None:
    out = ROOT / "apps" / "workbench" / "public" / "data" / "board.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    live = ROOT / ".workbench" / "lab.db"
    if live.exists():
        conn = sqlite3.connect(str(live))
        conn.row_factory = sqlite3.Row
    else:
        tmp = Path(tempfile.mkdtemp()) / "lab.db"
        board_db.db_path = lambda: tmp  # type: ignore[method-assign]
        conn = board_db.connect()
        board_db.init_schema(conn)
        board_db.import_bootstrap(conn, force=True)

    payload = {
        "schema_version": "1",
        "mode": "static_pages",
        "note": (
            "Read-only board snapshot for GitHub Pages when Lab API is offline. "
            "Run local `make dev` for live board mutations."
        ),
        "summary": board_db.summary(conn),
        "tickets": board_db.list_tickets(conn),
    }
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out} tickets={len(payload['tickets'])}")


if __name__ == "__main__":
    main()
