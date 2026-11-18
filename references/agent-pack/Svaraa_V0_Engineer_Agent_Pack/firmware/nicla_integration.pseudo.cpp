// Separate Arduino/Mbed Nicla build. Placeholder driver calls require qualification.
setup() {
  nicla::begin(); // verify exposed I/O is 3.3 V before wiring
  Wire.begin();  // Nicla is controller on external ESLOV bus
  load_supported_ndp_firmware_and_verified_model();
  configure_bmi270_and_read_back(100_HZ, RANGE_16G, RANGE_2000_DPS);
}
loop() {
  if(new_imu_sample()) {
    Frame32 f=encode_imu_units_and_crc(next_seq(), monotonic_ms(), read_motion());
    Wire.beginTransmission(0x2A); Wire.write(f.bytes,32);
    count_transfer_result(Wire.endTransmission());
  }
  if(wake_event() && !privacy) send_frame(WAKE, model_id_class_confidence());
  if(mailbox_due_10hz()) {
    auto cmd=read_exact_8_bytes(0x2A);
    if(crc_valid(cmd) && new_command(cmd)) {
      execute_bounded_idempotent_command(cmd);
      send_frame(COMMAND_RESULT, actual_applied_state());
    }
  }
  if(health_due()) send_frame(HEALTH, rate_range_drops_saturation_privacy());
}
// No raw audio PCM on this I2C link; Nano uses its own INMP441 I2S path.
