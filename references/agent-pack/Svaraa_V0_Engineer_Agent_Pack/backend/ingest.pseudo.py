# IMPLEMENTATION PSEUDOCODE, not a deployed service.
def ingest(request, principal):
    event = validate_schema_and_semantics(request.body)
    authorize_device_gateway_and_mode(principal, event)
    require(request.idempotency_key == event.event_id)
    digest = sha256(canonical_json(event))
    with database.transaction() as tx:
        old = tx.lookup_event(event.device_id, event.event_id)
        if old:
            require_same_hash_or_conflict(old, digest)
            return old.original_receipt
        # UNIQUE constraint arbitrates a concurrent insert; handle conflict safely.
        tx.insert_event_unique(event, digest)
        incident = apply_authorized_domain_transition(tx, event)
        tx.insert_outbox_once_if_needed(event, incident)
        receipt = tx.store_receipt(event, incident)
    return receipt  # after commit, never a human response claim

def caregiver_ack(principal, incident_id, action):
    authorize_current_assigned_caregiver(principal, incident_id)
    with database.transaction() as tx:
        if tx.action_seen(action.id): return tx.previous_result(action.id)
        incident = tx.lock_incident(incident_id)
        require(incident.revision == action.expected_revision)
        incident.record_human_ack(principal.user_id)
        tx.audit(action, incident)
        tx.queue_authenticated_device_status(incident)
    return incident.snapshot()
