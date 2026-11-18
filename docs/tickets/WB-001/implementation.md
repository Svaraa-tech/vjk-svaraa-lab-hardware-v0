# Execution — WB-001

## What changed

- `data/seeds/board_bootstrap_v0.1.json` seeds original + WB tickets
- `services/api/app/board_db.py` imports once into `.workbench/lab.db`
- `GET /lab/v1/board/provenance` re-hashes CSV/plan and compares to seed
- `docs/traceability/` + `contracts/PROVENANCE.json`
- `docs/tickets/<id>/ticket.md` generated for all 97 keys so every card has a task dossier

## Limitations

- Import validation UI report is API-backed; gallery links pack paths (WB-002)
- Re-import with `force=true` resets workflow unless board is treated as authority
