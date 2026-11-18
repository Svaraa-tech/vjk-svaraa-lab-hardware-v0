// Integration pseudocode, not a compiling Arduino sketch. Inspect and pin APIs.
setup() {
  set_outputs_safe(); init_clock_and_boot_identity(); restore_journal();
  Wire.begin(A4, A5, 100000);           // Nano controller: sensors
  Wire1.onReceive(copy_to_bounded_queue);
  Wire1.onRequest(return_prebuilt_mailbox);
  bool ok=Wire1.begin(uint8_t(0x2A), D4, D3, 100000); // Nano target
  if(!ok) mark_nicla_link_fault();      // manual SOS still available
  initialize_qualified_i2s_driver();
  start_safety_task(); start_sensor_task(); start_network_task();
  start_audio_task_at_lower_priority();
}
safety_tick_every_10ms() {
  auto now=monotonic_ms();
  auto input=debounce_and_qualify_button(now);
  if(input==QUALIFIED_HOLD) apply(core.manual_sos(new_incident_uuid()));
  if(input==SHORT_TAP && core.state().phase==Phase::Prealert) apply(core.cancel());
  auto samples=drain_bounded_sensor_queue();
  if(real_fall_candidate(samples)) apply(core.fall_candidate(now));
  apply(core.tick(now, reserved_next_incident_id()));
  expire_health_ttls(now); render_evidence_backed_feedback();
  report_watchdog_progress_only_if_required_work_ran();
}
apply(actions) {
  if(actions & CreateEvent) {
    const auto event=freeze_canonical_event(new_event_uuid(), core.state(), location_or_null());
    if(!journal.append_commit_bounded(event)) {
      mark_storage_degraded(); volatile_critical_queue.push(event);
      schedule_separate_health_fault(); // never mutate queued body under same ID
    }
    transport.wake(); // do not wait for GPS, cloud AI or network acquisition
  }
  render_local_feedback(actions);
}
network_worker() {
  for(auto record: pending_critical_first()) {
    auto result=send_same_bytes_and_idempotency_key(record);
    if(verify_matching_backend_receipt(result)) {
      store_receipt(record.id,result); apply_authoritative_revision(result);
    } else retry_same_id_with_bounded_backoff(record);
  }
}
privacy_asserted() {
  stop_capture_and_upload(); discard_unsent_audio();
  nicla_mailbox.request_software_privacy(true);
  // Closed physical S2 cannot be overridden by remote privacy-off.
}
