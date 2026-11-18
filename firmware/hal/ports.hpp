#pragma once
#include "types.hpp"
#include <cstddef>

namespace svaraa::hal {

struct IClock {
  virtual ~IClock() = default;
  virtual uint64_t monotonic_ms() const = 0;
  // Trusted UTC milliseconds since epoch if known; empty if unknown/untrusted.
  virtual std::optional<uint64_t> trusted_utc_ms() const = 0;
};

struct IMotion {
  virtual ~IMotion() = default;
  virtual Result read(MotionSample& out) = 0;
  virtual Health health() const = 0;
};

struct ILocation {
  virtual ~ILocation() = default;
  virtual Result read(LocationFix& out) = 0;
  virtual Health health() const = 0;
};

struct IJournal {
  virtual ~IJournal() = default;
  virtual Result append_commit(const JournalRecord& record) = 0;
  virtual Result replay_from(size_t index, JournalRecord& out) const = 0;
  virtual size_t size() const = 0;
  virtual size_t capacity() const = 0;
  virtual JournalStatus status() const = 0;
};

struct ITransport {
  virtual ~ITransport() = default;
  virtual bool reachable() const = 0;
  // Attempt send of the same canonical bytes / identity. Does NOT imply receipt.
  virtual Result attempt_send(const JournalRecord& record, TransportAttempt& out) = 0;
  // Apply only a verified matching receipt (caller supplies verification flag).
  virtual Result note_receipt(const TransportReceipt& receipt) = 0;
  virtual Health health() const = 0;
};

struct IAudio {
  virtual ~IAudio() = default;
  virtual Result start_capture() = 0;
  virtual Result start_playback() = 0;
  virtual Result stop() = 0;
  virtual Result set_privacy(bool effective) = 0;
  virtual AudioStatus status() const = 0;
};

struct IUi {
  virtual ~IUi() = default;
  // Must render actual phase + independent health; never invent success.
  virtual Result render(const UiSnapshot& snap) = 0;
  virtual UiSnapshot last() const = 0;
};

}  // namespace svaraa::hal
