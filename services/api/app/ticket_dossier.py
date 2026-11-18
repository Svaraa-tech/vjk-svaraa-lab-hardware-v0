"""Assemble per-ticket dossier: task, execution, results (WB-004 / board UX)."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from . import board_db

DOC_FILES = (
    ("ticket", "ticket.md"),
    ("plan", "plan.md"),
    ("implementation", "implementation.md"),
    ("tests", "tests.md"),
    ("review", "review.md"),
)


def _read_md(path: Path) -> str | None:
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return None


_SKIP_DIR_NAMES = {
    ".venv",
    "node_modules",
    "__pycache__",
    ".git",
    "dist",
    "build",
}


def _evidence_listing(root: Path, ticket_key: str) -> list[dict[str, Any]]:
    ev = root / "evidence" / ticket_key
    if not ev.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(ev.rglob("*")):
        if any(part in _SKIP_DIR_NAMES for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        rel = path.relative_to(ev).as_posix()
        size = path.stat().st_size
        item: dict[str, Any] = {
            "path": f"evidence/{ticket_key}/{rel}",
            "name": rel,
            "bytes": size,
        }
        # WB-029 — pin firmware.bin with sha thumb metadata
        if path.name.lower() == "firmware.bin" or path.suffix.lower() == ".bin":
            data = path.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            item.update(
                {
                    "kind": "firmware",
                    "sha256": sha,
                    "sha12": sha[:12],
                    "pinned": path.name.lower() == "firmware.bin",
                }
            )
        out.append(item)
    return out


def _firmware_pins(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pins = [e for e in evidence if e.get("kind") == "firmware" and e.get("pinned")]
    if pins:
        return pins
    return [e for e in evidence if e.get("kind") == "firmware"]


def _synthesize_task(ticket: dict[str, Any]) -> str:
    lines = [
        f"# {ticket['ticket_key']} — {ticket.get('summary') or ''}",
        "",
        f"**Type:** {ticket.get('work_type') or '—'}  ",
        f"**State:** {ticket.get('workflow_state') or '—'}  ",
        f"**Implementation:** {ticket.get('implementation_state') or 'not_started'}  ",
        f"**Acceptance:** {ticket.get('owner_acceptance') or 'none'}  ",
        f"**Profile:** {ticket.get('profile_default') or 'SIM'}  ",
        f"**Namespace:** {ticket.get('source_namespace') or '—'}  ",
    ]
    if ticket.get("parent_key"):
        lines.append(f"**Parent:** {ticket['parent_key']}  ")
    if ticket.get("plan_dependencies"):
        lines.append(f"**Links / deps:** {ticket['plan_dependencies']}  ")
    if ticket.get("priority"):
        lines.append(f"**Priority:** {ticket['priority']}  ")
    lines.append("")
    desc = (ticket.get("description") or "").strip()
    if desc:
        lines.extend(["## Description", "", desc, ""])
    else:
        lines.extend(
            [
                "## Description",
                "",
                "_No long-form description in board DB yet. "
                "Will appear here once `docs/tickets/<id>/ticket.md` is written._",
                "",
            ]
        )
    state = ticket.get("workflow_state") or "Backlog"
    if state == "Backlog":
        lines.extend(
            [
                "## Status note",
                "",
                "Not started. Open this modal anytime — task, execution, and results "
                "sections fill in as work proceeds.",
                "",
            ]
        )
    return "\n".join(lines)


def _synthesize_execution(ticket: dict[str, Any]) -> str:
    state = ticket.get("workflow_state") or "Backlog"
    impl = ticket.get("implementation_state") or "not_started"
    if state in ("Backlog", "Planning", "Awaiting Plan Approval", "Ready") and impl in (
        None,
        "not_started",
    ):
        return (
            "# Execution\n\n"
            "_Not executed yet._ When work starts, this section is filled from "
            f"`docs/tickets/{ticket['ticket_key']}/implementation.md` "
            "(what changed, artifacts, deviations).\n"
        )
    return (
        "# Execution\n\n"
        f"Workflow **{state}**, implementation **{impl}**.\n\n"
        f"_Detailed write-up not found at `docs/tickets/{ticket['ticket_key']}/implementation.md`. "
        "Decisions / transitions below still record board activity._\n"
    )


def _synthesize_results(ticket: dict[str, Any]) -> str:
    state = ticket.get("workflow_state") or "Backlog"
    if state == "Done":
        return (
            "# Results\n\n"
            "Marked **Done** on the board. Add `tests.md` / `review.md` and "
            f"`evidence/{ticket['ticket_key']}/` for a full results dossier.\n"
        )
    if state in ("Testing", "Awaiting Acceptance"):
        return (
            "# Results\n\n"
            f"In **{state}**. Test/review markdown will appear here when written.\n"
        )
    return (
        "# Results\n\n"
        "_No results yet._ Evidence files and test notes land here after runs.\n"
    )


def build_dossier(conn, ticket_key: str) -> dict[str, Any] | None:
    ticket = board_db.get_ticket(conn, ticket_key)
    if not ticket:
        return None

    root = board_db.project_root()
    docs_dir = root / "docs" / "tickets" / ticket_key
    docs: dict[str, str | None] = {}
    for key, fname in DOC_FILES:
        docs[key] = _read_md(docs_dir / fname)

    evidence = _evidence_listing(root, ticket_key)

    task = docs["ticket"] or _synthesize_task(ticket)
    plan = docs["plan"]
    execution = docs["implementation"] or _synthesize_execution(ticket)
    tests = docs["tests"]
    review = docs["review"]
    results_parts: list[str] = []
    if tests:
        results_parts.append(tests)
    if review:
        results_parts.append(review)
    if not results_parts:
        results_parts.append(_synthesize_results(ticket))
    if evidence:
        ev_lines = ["", "## Evidence files", ""]
        for e in evidence[:80]:
            ev_lines.append(f"- `{e['path']}` ({e['bytes']} bytes)")
        if len(evidence) > 80:
            ev_lines.append(f"- … +{len(evidence) - 80} more")
        results_parts.append("\n".join(ev_lines))

    firmware_pins = _firmware_pins(evidence)
    completeness = {
        "has_ticket_md": bool(docs["ticket"]),
        "has_plan_md": bool(docs["plan"]),
        "has_implementation_md": bool(docs["implementation"]),
        "has_tests_md": bool(docs["tests"]),
        "has_review_md": bool(docs["review"]),
        "evidence_file_count": len(evidence),
        "has_firmware_evidence": bool(firmware_pins),
        "firmware_pin_count": len(firmware_pins),
    }

    if firmware_pins:
        fw_lines = ["", "## Firmware pins (WB-029)", ""]
        for e in firmware_pins:
            fw_lines.append(
                f"- `{e['path']}` · sha256 `{e.get('sha12')}…` · {e['bytes']} bytes"
            )
        results_parts.append("\n".join(fw_lines))

    return {
        "ticket_key": ticket_key,
        "ticket": ticket,
        "sections": {
            "task": task,
            "plan": plan,
            "execution": execution,
            "results": "\n\n---\n\n".join(results_parts),
            "tests": tests,
            "review": review,
        },
        "docs_present": {k: bool(v) for k, v in docs.items()},
        "completeness": completeness,
        "evidence": evidence,
        "firmware_pins": firmware_pins,
        "docs_dir": f"docs/tickets/{ticket_key}/" if docs_dir.is_dir() else None,
        "profile": "SIM",
        "simulated": True,
    }
