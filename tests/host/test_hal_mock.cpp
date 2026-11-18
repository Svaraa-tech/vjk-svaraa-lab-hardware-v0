#include "../../firmware/hal/board/board_stubs.hpp"
#include "../../firmware/hal/host_safety_glue.hpp"
#include "../../firmware/hal/mock/mock_ports.hpp"
#include <cassert>
#include <iostream>

using namespace svaraa;
using namespace svaraa::hal;
using namespace svaraa::hal::mock;

int main() {
  int checks = 0;
  auto check = [&](bool ok) {
    assert(ok);
    ++checks;
  };

  // --- Mock clock drives core timers ---
  MockClock clock(1000);
  Core core;
  check(core.fall_candidate(clock.monotonic_ms()) & Feedback);
  check(core.state().phase == Phase::Prealert);
  clock.advance(19999);
  auto id_a = id("00000000-0000-4000-8000-000000000001");
  check(core.tick(clock.monotonic_ms(), id_a) == None);
  clock.advance(1);
  check(core.tick(clock.monotonic_ms(), id_a) & CreateEvent);
  check(core.state().phase == Phase::Pending);

  // --- Location nulls stay null ---
  MockLocation loc;
  loc.clear_fix();
  LocationFix fix;
  check(loc.read(fix) == Result::Ok);
  check(!fix.valid);
  check(!fix.latitude.has_value());
  check(!fix.longitude.has_value());

  // --- Journal full fault ---
  MockJournal journal(1);
  JournalRecord r1;
  r1.event_id = make_id("00000000-0000-4000-8000-000000000010");
  r1.canonical_bytes = {1, 2, 3};
  check(journal.append_commit(r1) == Result::Ok);
  JournalRecord r2 = r1;
  r2.event_id = make_id("00000000-0000-4000-8000-000000000011");
  check(journal.append_commit(r2) == Result::Full);
  check(journal.status() == JournalStatus::Full);

  // --- Transport attempt ≠ receipt ---
  MockTransport transport;
  TransportAttempt attempt;
  check(transport.attempt_send(r1, attempt) == Result::Ok);
  check(attempt.accepted_by_provider);
  check(!transport.last_receipt().has_value());
  transport.set_reachable(false);
  check(transport.attempt_send(r1, attempt) == Result::Unreachable);

  // --- Audio privacy blocks capture ---
  MockAudio audio;
  check(audio.set_privacy(true) == Result::Ok);
  check(audio.start_capture() == Result::PrivacyBlocked);

  // --- UI rejects optimistic success ---
  MockUi ui;
  UiSnapshot bad;
  bad.optimistic_success_forbidden = false;
  check(ui.render(bad) == Result::Invalid);
  UiSnapshot good;
  good.optimistic_success_forbidden = true;
  good.phase_code = 2;
  good.caption = "pending";
  check(ui.render(good) == Result::Ok);
  check(ui.last().caption == "pending");

  // --- Board stubs do not invent measurements ---
  board::BoardLocation bloc;
  LocationFix bfix;
  check(bloc.read(bfix) == Result::NotImplemented);
  check(!bfix.latitude.has_value());
  board::BoardMotion bmot;
  MotionSample ms;
  check(bmot.read(ms) == Result::NotImplemented);
  check(bmot.health() == Health::Missing);

  // --- Host glue: qualified hold journals + transport attempt ---
  MockClock gclock(0);
  MockJournal gjournal(4);
  MockTransport gtransport;
  MockLocation glocation;
  MockUi gui;
  HostSafetyGlue glue;
  glue.clock = &gclock;
  glue.journal = &gjournal;
  glue.transport = &gtransport;
  glue.location = &glocation;
  glue.ui = &gui;
  auto actions =
      glue.on_qualified_hold("00000000-0000-4000-8000-000000000020");
  check(actions & CreateEvent);
  check(gjournal.size() == 1);
  check(gtransport.attempts() == 1);
  check(!gtransport.last_receipt().has_value());
  check(gui.last().phase_code == phase_code(Phase::Pending));

  // Motion port smoke
  MockMotion motion;
  MotionSample sample;
  sample.accel_mg[2] = 1000;
  sample.valid = true;
  sample.acquired_monotonic_ms = 42;
  motion.set_sample(sample);
  MotionSample got;
  check(motion.read(got) == Result::Ok);
  check(got.accel_mg[2] == 1000);
  check(motion.health() == Health::Mocked);

  std::cout << "PASS: " << checks
            << " HAL mock/board-stub host checks; SIM adapters only\n";
  return 0;
}
