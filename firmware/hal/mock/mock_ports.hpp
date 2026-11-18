#pragma once
#include "../ports.hpp"
#include <deque>

namespace svaraa::hal::mock {

class MockClock final : public IClock {
 public:
  explicit MockClock(uint64_t start_ms = 0) : now_(start_ms) {}
  uint64_t monotonic_ms() const override { return now_; }
  std::optional<uint64_t> trusted_utc_ms() const override { return utc_; }
  void advance(uint64_t delta_ms) { now_ += delta_ms; }
  void set(uint64_t ms) { now_ = ms; }
  void set_trusted_utc(std::optional<uint64_t> utc) { utc_ = utc; }

 private:
  uint64_t now_ = 0;
  std::optional<uint64_t> utc_{};
};

class MockMotion final : public IMotion {
 public:
  Result read(MotionSample& out) override {
    out = next_;
    if (force_missing_) {
      out.valid = false;
      return Result::Unavailable;
    }
    return out.valid ? Result::Ok : Result::Invalid;
  }
  Health health() const override {
    if (force_missing_) return Health::Missing;
    return next_.valid ? Health::Mocked : Health::Degraded;
  }
  void set_sample(const MotionSample& s) { next_ = s; }
  void set_missing(bool v) { force_missing_ = v; }

 private:
  MotionSample next_{};
  bool force_missing_ = false;
};

class MockLocation final : public ILocation {
 public:
  Result read(LocationFix& out) override {
    out = fix_;
    return Result::Ok;  // Ok with null coords is honest
  }
  Health health() const override {
    if (!fix_.valid) return Health::Degraded;
    return Health::Mocked;
  }
  void set_fix(const LocationFix& f) { fix_ = f; }
  void clear_fix() {
    fix_ = LocationFix{};
    fix_.source = LocationSource::None;
    fix_.valid = false;
  }

 private:
  LocationFix fix_{};
};

class MockJournal final : public IJournal {
 public:
  explicit MockJournal(size_t capacity = 8) : capacity_(capacity) {}
  Result append_commit(const JournalRecord& record) override {
    if (force_full_ || records_.size() >= capacity_) {
      status_ = JournalStatus::Full;
      return Result::Full;
    }
    records_.push_back(record);
    status_ = JournalStatus::Ok;
    return Result::Ok;
  }
  Result replay_from(size_t index, JournalRecord& out) const override {
    if (index >= records_.size()) return Result::Invalid;
    out = records_[index];
    return Result::Ok;
  }
  size_t size() const override { return records_.size(); }
  size_t capacity() const override { return capacity_; }
  JournalStatus status() const override { return status_; }
  void set_force_full(bool v) { force_full_ = v; }

 private:
  size_t capacity_;
  bool force_full_ = false;
  JournalStatus status_ = JournalStatus::Ok;
  std::vector<JournalRecord> records_;
};

class MockTransport final : public ITransport {
 public:
  bool reachable() const override { return reachable_; }
  Result attempt_send(const JournalRecord& record, TransportAttempt& out) override {
    ++attempts_;
    out.event_id = record.event_id;
    out.attempt = attempts_;
    out.reachable = reachable_;
    out.authenticated = authenticated_;
    out.accepted_by_provider = false;
    if (!reachable_) {
      health_ = Health::Faulted;
      return Result::Unreachable;
    }
    if (!authenticated_) {
      health_ = Health::Faulted;
      return Result::AuthFailed;
    }
    // Provider accept is still NOT a durable server receipt.
    out.accepted_by_provider = provider_accepts_;
    last_attempt_ = out;
    health_ = Health::Mocked;
    return Result::Ok;
  }
  Result note_receipt(const TransportReceipt& receipt) override {
    if (!receipt.verified_match) return Result::Invalid;
    last_receipt_ = receipt;
    return Result::Ok;
  }
  Health health() const override { return health_; }

  void set_reachable(bool v) { reachable_ = v; }
  void set_authenticated(bool v) { authenticated_ = v; }
  void set_provider_accepts(bool v) { provider_accepts_ = v; }
  uint32_t attempts() const { return attempts_; }
  const TransportAttempt& last_attempt() const { return last_attempt_; }
  const std::optional<TransportReceipt>& last_receipt() const { return last_receipt_; }

 private:
  bool reachable_ = true;
  bool authenticated_ = true;
  bool provider_accepts_ = true;
  uint32_t attempts_ = 0;
  Health health_ = Health::Mocked;
  TransportAttempt last_attempt_{};
  std::optional<TransportReceipt> last_receipt_{};
};

class MockAudio final : public IAudio {
 public:
  Result start_capture() override {
    if (privacy_) return Result::PrivacyBlocked;
    st_.mode = AudioMode::Capture;
    return Result::Ok;
  }
  Result start_playback() override {
    if (st_.mode == AudioMode::Capture) st_.mode = AudioMode::Idle;  // half-duplex
    st_.mode = AudioMode::Playback;
    return Result::Ok;
  }
  Result stop() override {
    st_.mode = AudioMode::Idle;
    return Result::Ok;
  }
  Result set_privacy(bool effective) override {
    privacy_ = effective;
    st_.privacy_effective = effective;
    if (effective && st_.mode == AudioMode::Capture) st_.mode = AudioMode::Idle;
    return Result::Ok;
  }
  AudioStatus status() const override {
    AudioStatus s = st_;
    s.health = Health::Mocked;
    return s;
  }

 private:
  bool privacy_ = false;
  AudioStatus st_{};
};

class MockUi final : public IUi {
 public:
  Result render(const UiSnapshot& snap) override {
    if (!snap.optimistic_success_forbidden) return Result::Invalid;
    last_ = snap;
    history_.push_back(snap);
    while (history_.size() > 32) history_.pop_front();
    return Result::Ok;
  }
  UiSnapshot last() const override { return last_; }
  size_t history_size() const { return history_.size(); }

 private:
  UiSnapshot last_{};
  std::deque<UiSnapshot> history_;
};

}  // namespace svaraa::hal::mock
