# WB-001 — Source import, validation, provenance and traceability

```yaml
ticket_id: WB-001
work_type: Workbench
source_namespace: workbench
links: [SV0-S01, SV0-S11]
profile: SIM
```

## Problem and user outcome

Import the original 87-ticket backlog plus WB proposals into a durable Lab board with provenance (CSV/plan hashes) and traceability links.

## Definition of done (SIM)

- Bootstrap import into SQLite board authority
- Provenance endpoint re-hashes pack CSV/plan vs seed
- Traceability docs under `docs/traceability/`
- Ticket dossier modal surfaces task/execution/results for every key
