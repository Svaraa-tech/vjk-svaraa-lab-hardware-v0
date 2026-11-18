# Execution — SV0-07.04
`SimEngine.retry_outbox` reuses same event_id; lost receipt + dual accept → one incident (`idempotent` commit).
