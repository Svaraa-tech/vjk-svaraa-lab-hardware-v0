#pragma once
#include <array>
#include <cstdint>
#include <optional>
#include <string>
#include <vector>

// SDK-free POD types for HAL ports (SV0-01.03). Not Arduino/Wire/BLE types.

namespace svaraa::hal {

enum class Result : uint8_t {
  Ok = 0,
  Full = 1,
  Unavailable = 2,
  NotImplemented = 3,
  Invalid = 4,
  PrivacyBlocked = 5,
  Unreachable = 6,
  AuthFailed = 7,
  Conflict = 8,
};

enum class Health : uint8_t {
  Unknown = 0,
  Ok = 1,
  Degraded = 2,
  Faulted = 3,
  Missing = 4,
  Mocked = 5,
};

enum class LocationSource : uint8_t {
  None = 0,
  Gnss = 1,
  PhoneConsented = 2,
  TagOnly = 3,
};

enum class AudioMode : uint8_t {
  Idle = 0,
  Capture = 1,
  Playback = 2,
};

struct MotionSample {
  int16_t accel_mg[3]{};
  int16_t gyro_dps_x10[3]{};  // 0.1 deg/s units
  uint64_t acquired_monotonic_ms = 0;
  bool valid = false;
  bool saturated = false;
  bool overrun = false;
};

struct LocationFix {
  LocationSource source = LocationSource::None;
  std::optional<double> latitude;
  std::optional<double> longitude;
  std::optional<double> accuracy_m;
  std::optional<uint64_t> fix_at_monotonic_ms;
  std::optional<uint32_t> age_ms;
  bool valid = false;
};

struct JournalRecord {
  std::array<char, 37> event_id{};
  std::vector<uint8_t> canonical_bytes;
  uint32_t crc32 = 0;
};

enum class JournalStatus : uint8_t {
  Ok = 0,
  Full = 1,
  CorruptTail = 2,
  CommitInterrupted = 3,
};

struct TransportAttempt {
  std::array<char, 37> event_id{};
  uint32_t attempt = 0;
  bool reachable = false;
  bool authenticated = false;
  bool accepted_by_provider = false;  // NOT server receipt / human ack
};

struct TransportReceipt {
  std::array<char, 37> event_id{};
  uint32_t revision = 0;
  bool verified_match = false;
};

struct AudioStatus {
  AudioMode mode = AudioMode::Idle;
  bool privacy_effective = false;
  uint32_t buffer_occupancy = 0;
  uint32_t overflow_count = 0;
  Health health = Health::Unknown;
};

struct ComponentHealth {
  Health motion = Health::Unknown;
  Health location = Health::Unknown;
  Health journal = Health::Unknown;
  Health transport = Health::Unknown;
  Health audio = Health::Unknown;
  Health nicla_link = Health::Unknown;
};

// Types-only supervisor snapshot (not a watchdog implementation).
struct SupervisorSnapshot {
  bool required_tasks_progressing = false;
  uint32_t reboot_cause_code = 0;
  ComponentHealth health{};
};

struct UiSnapshot {
  // Phase encoded as int to avoid forcing core include here; glue maps enums.
  int phase_code = 0;  // 0 Ready … see host glue
  int mode_code = 0;   // 0 Live, 1 Drill
  bool cancel_requested = false;
  bool optimistic_success_forbidden = true;
  ComponentHealth health{};
  std::string caption;  // evidence-backed text only
};

inline std::array<char, 37> make_id(const char* s) {
  std::array<char, 37> out{};
  if (!s) return out;
  for (size_t i = 0; i < 36 && s[i]; ++i) out[i] = s[i];
  return out;
}

}  // namespace svaraa::hal
