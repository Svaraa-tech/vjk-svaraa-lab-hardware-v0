# Execution — WB-004

## What changed

- `decisions` table + `POST/GET /lab/v1/decisions`
- Ticket modal Activity: Approve plan / Accept (SIM)
- `GET /lab/v1/tickets/{key}/dossier` merges `docs/tickets/<key>/*` + evidence index
- Transition audit rows on every board move

## Sync rule

Agent writes `docs/tickets/<id>/{ticket,plan,implementation,tests,review}.md`; UI always reads via dossier endpoint so Done / In Progress / Backlog cards share one modal shape.
