# Threat model — Svaraa V0 Lab (SV0-12.01)

Profile: **SIM** documentation freeze. Does not certify a production device.

| Risk ID | Threat | Control | Test | Owner |
| --- | --- | --- | --- | --- |
| T-SOS-01 | Spoofed SOS from untrusted client | Lab only accepts `sv0-lab-*` device IDs; tenant header must match | `test_product_ingest.test_wrong_tenant` | Backend / SRE |
| T-LOC-01 | Unauthorized / invented location | `source=none` forces null lat/lon; no Find My coords into SOS | device_event schema + ingest validation | Firmware / Backend |
| T-CMD-01 | Malicious commands via browser | Browser never sets `verified=true`; only bridge/API after durable receipt | host-bridge README + reducer unverified reject | Embedded lead |
| T-DEV-01 | Stolen device / shared secrets | Unique test credentials; no fleet production secret in Lab | SV0-12.02 policy + `test_dev_identity` | Security / embedded |
| T-PROV-01 | Bad provisioning / trust break | Development identity scoped to SIM profile | docs + identity file check | Security / embedded |
| T-OTA-01 | Invalid/interrupted update marked success | Updates deferred during incident; invalid signature → reject | `test_update_policy` | Security / embedded |
| T-AUD-01 | Ambient audio upload | Purpose allowlist; `ambient_audio_upload` forbidden | consent API 422 | Security / privacy |
| T-ACL-01 | Stale guardian access | Role revoke clears grants; audited | consent revoke test | Security / privacy |

## Trust boundaries

1. Pendant / host-bridge (trusted after local qualification)
2. Lab API (SIM, local SQLite)
3. Mock notification provider (never human ACK)
4. Browser workbench (untrusted for `verified` flags)
