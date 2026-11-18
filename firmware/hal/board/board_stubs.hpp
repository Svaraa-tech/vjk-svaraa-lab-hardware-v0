#pragma once
#include "../ports.hpp"

// Board adapter stubs for future Nano/Nicla builds (SV0-01.03).
// No Arduino/SDK includes. Methods return NotImplemented until a board ticket.

namespace svaraa::hal::board {

class BoardClock final : public IClock {
 public:
  uint64_t monotonic_ms() const override { return 0; }
  std::optional<uint64_t> trusted_utc_ms() const override { return std::nullopt; }
};

class BoardMotion final : public IMotion {
 public:
  Result read(MotionSample& out) override {
    out = MotionSample{};
    return Result::NotImplemented;
  }
  Health health() const override { return Health::Missing; }
};

class BoardLocation final : public ILocation {
 public:
  Result read(LocationFix& out) override {
    out = LocationFix{};  // null coords — do not invent a fix
    return Result::NotImplemented;
  }
  Health health() const override { return Health::Missing; }
};

class BoardJournal final : public IJournal {
 public:
  Result append_commit(const JournalRecord&) override { return Result::NotImplemented; }
  Result replay_from(size_t, JournalRecord&) const override { return Result::NotImplemented; }
  size_t size() const override { return 0; }
  size_t capacity() const override { return 0; }
  JournalStatus status() const override { return JournalStatus::Ok; }
};

class BoardTransport final : public ITransport {
 public:
  bool reachable() const override { return false; }
  Result attempt_send(const JournalRecord&, TransportAttempt& out) override {
    out = TransportAttempt{};
    return Result::NotImplemented;
  }
  Result note_receipt(const TransportReceipt&) override { return Result::NotImplemented; }
  Health health() const override { return Health::Missing; }
};

class BoardAudio final : public IAudio {
 public:
  Result start_capture() override { return Result::NotImplemented; }
  Result start_playback() override { return Result::NotImplemented; }
  Result stop() override { return Result::NotImplemented; }
  Result set_privacy(bool) override { return Result::NotImplemented; }
  AudioStatus status() const override {
    AudioStatus s;
    s.health = Health::Missing;
    return s;
  }
};

class BoardUi final : public IUi {
 public:
  Result render(const UiSnapshot&) override { return Result::NotImplemented; }
  UiSnapshot last() const override { return {}; }
};

}  // namespace svaraa::hal::board
