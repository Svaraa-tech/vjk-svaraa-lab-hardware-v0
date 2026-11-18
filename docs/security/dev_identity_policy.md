# Development identity policy — SV0-12.02

- Lab uses **unique test device IDs** (`sv0-lab-*`), never a shared fleet production secret.
- TLS to real cloud providers is **out of scope** for SIM; when introduced, certificate validation must remain enabled.
- Credential rotation design: rotate Lab device `boot_id` per run; future product keys via HSM/secure element (V1).
- `notification_provider=mock` only under current batch auth.
