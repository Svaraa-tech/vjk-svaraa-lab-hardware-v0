#pragma once
#include "../core/sos_core.hpp"
#include "mock/mock_ports.hpp"
#include "types.hpp"

// Thin host glue: maps qualified inputs → Core using HAL types only (SV0-01.03).

namespace svaraa::hal {

inline int phase_code(svaraa::Phase p) {
  switch (p) {
    case svaraa::Phase::Ready: return 0;
    case svaraa::Phase::Prealert: return 1;
    case svaraa::Phase::Pending: return 2;
    case svaraa::Phase::ServerAccepted: return 3;
    case svaraa::Phase::HumanAck: return 4;
    case svaraa::Phase::Resolved: return 5;
  }
  return 0;
}

inline int mode_code(svaraa::Mode m) {
  return m == svaraa::Mode::Drill ? 1 : 0;
}

struct HostSafetyGlue {
  svaraa::Core core;
  mock::MockClock* clock = nullptr;
  mock::MockJournal* journal = nullptr;
  mock::MockTransport* transport = nullptr;
  mock::MockLocation* location = nullptr;
  mock::MockUi* ui = nullptr;

  ComponentHealth health_snapshot() const {
    ComponentHealth h;
    h.motion = Health::Mocked;
    h.location = location ? location->health() : Health::Unknown;
    h.journal = journal ? (journal->status() == JournalStatus::Full ? Health::Degraded
                                                                   : Health::Mocked)
                        : Health::Unknown;
    h.transport = transport ? transport->health() : Health::Unknown;
    h.audio = Health::Mocked;
    h.nicla_link = Health::Mocked;
    return h;
  }

  void render_ui(const char* caption) {
    if (!ui) return;
    UiSnapshot snap;
    snap.phase_code = phase_code(core.state().phase);
    snap.mode_code = mode_code(core.state().mode);
    snap.cancel_requested = false;
    snap.optimistic_success_forbidden = true;
    snap.health = health_snapshot();
    snap.caption = caption ? caption : "";
    ui->render(snap);
  }

  uint32_t on_qualified_hold(const char* incident_id) {
    auto actions = core.manual_sos(svaraa::id(incident_id));
    if (actions & svaraa::CreateEvent) {
      JournalRecord rec;
      rec.event_id = make_id(incident_id);
      // Opaque canonical bytes for this ticket — real schema freeze is later.
      const char* marker = "sos.created";
      rec.canonical_bytes.assign(marker, marker + 11);
      rec.crc32 = 0;
      if (journal) {
        auto jr = journal->append_commit(rec);
        if (jr == Result::Full) {
          render_ui("storage_degraded");
        } else if (transport) {
          TransportAttempt attempt;
          transport->attempt_send(rec, attempt);
          // Provider accept is not server receipt / human ack.
          render_ui(attempt.reachable ? "pending_not_delivered_or_in_flight"
                                      : "pending_unreachable");
        }
      }
    } else {
      render_ui("feedback_only");
    }
    return actions;
  }

  uint32_t on_tick() {
    if (!clock) return svaraa::None;
    return core.tick(clock->monotonic_ms(),
                     svaraa::id("00000000-0000-4000-8000-000000000099"));
  }
};

}  // namespace svaraa::hal
