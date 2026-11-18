// Minimal JSONL host-bridge around sos_core (WB-005).
// Lines in:  {"cmd":"ping"|"reset"|"manual_sos"|"snapshot"|"update",...}
// Lines out: {"ok":true,...} or {"ok":false,"error":"..."}
#include <cstdio>
#include <cstring>
#include <iostream>
#include <string>

#include "../core/sos_core.hpp"

static svaraa::Core g_core;
static uint64_t g_now = 0;

static void emit_ok_snapshot() {
  const auto& s = g_core.state();
  const char* phase = "Ready";
  switch (s.phase) {
    case svaraa::Phase::Ready: phase = "Ready"; break;
    case svaraa::Phase::Prealert: phase = "Prealert"; break;
    case svaraa::Phase::Pending: phase = "Pending"; break;
    case svaraa::Phase::ServerAccepted: phase = "ServerAccepted"; break;
    case svaraa::Phase::HumanAck: phase = "HumanAck"; break;
    case svaraa::Phase::Resolved: phase = "Resolved"; break;
  }
  const char* mode = s.mode == svaraa::Mode::Drill ? "drill" : "live";
  std::printf(
      "{\"ok\":true,\"cmd\":\"snapshot\",\"phase\":\"%s\",\"mode\":\"%s\","
      "\"incident\":\"%.36s\",\"revision\":%u,\"now_ms\":%llu}\n",
      phase, mode, s.incident.data(), s.revision,
      static_cast<unsigned long long>(g_now));
  std::fflush(stdout);
}

// Tiny JSON field extractors (no full parser — lab bridge only).
static bool has_cmd(const std::string& line, const char* cmd) {
  std::string needle = std::string("\"cmd\":\"") + cmd + "\"";
  return line.find(needle) != std::string::npos;
}

static std::string extract_str(const std::string& line, const char* key) {
  std::string needle = std::string("\"") + key + "\":\"";
  auto p = line.find(needle);
  if (p == std::string::npos) return {};
  p += needle.size();
  auto e = line.find('"', p);
  if (e == std::string::npos) return {};
  return line.substr(p, e - p);
}

static int extract_int(const std::string& line, const char* key, int def = 0) {
  std::string needle = std::string("\"") + key + "\":";
  auto p = line.find(needle);
  if (p == std::string::npos) return def;
  p += needle.size();
  return std::atoi(line.c_str() + p);
}

int main() {
  std::string line;
  while (std::getline(std::cin, line)) {
    if (line.empty()) continue;
    if (has_cmd(line, "ping")) {
      std::printf("{\"ok\":true,\"cmd\":\"ping\",\"bridge\":\"svaraa_host_bridge\",\"v\":1}\n");
      std::fflush(stdout);
    } else if (has_cmd(line, "reset")) {
      g_core = svaraa::Core{};
      g_now = 0;
      emit_ok_snapshot();
    } else if (has_cmd(line, "manual_sos")) {
      auto id = extract_str(line, "incident_id");
      if (id.empty()) id = "00000000-0000-4000-8000-000000000001";
      auto actions = g_core.manual_sos(svaraa::id(id.c_str()));
      std::printf("{\"ok\":true,\"cmd\":\"manual_sos\",\"actions\":%u}\n", actions);
      std::fflush(stdout);
      emit_ok_snapshot();
    } else if (has_cmd(line, "update")) {
      auto id = extract_str(line, "incident_id");
      int rev = extract_int(line, "revision", 1);
      std::string phase_s = extract_str(line, "phase");
      svaraa::Phase phase = svaraa::Phase::ServerAccepted;
      if (phase_s == "HumanAck") phase = svaraa::Phase::HumanAck;
      if (phase_s == "Resolved") phase = svaraa::Phase::Resolved;
      auto actions = g_core.update(svaraa::id(id.c_str()), svaraa::Mode::Live, phase,
                                   static_cast<uint32_t>(rev), true);
      std::printf("{\"ok\":true,\"cmd\":\"update\",\"actions\":%u}\n", actions);
      std::fflush(stdout);
      emit_ok_snapshot();
    } else if (has_cmd(line, "snapshot")) {
      emit_ok_snapshot();
    } else if (has_cmd(line, "tick")) {
      g_now = static_cast<uint64_t>(extract_int(line, "now_ms", static_cast<int>(g_now)));
      auto id = extract_str(line, "incident_id");
      if (id.empty()) id = "00000000-0000-4000-8000-000000000099";
      auto actions = g_core.tick(g_now, svaraa::id(id.c_str()));
      std::printf("{\"ok\":true,\"cmd\":\"tick\",\"actions\":%u}\n", actions);
      std::fflush(stdout);
      emit_ok_snapshot();
    } else {
      std::printf("{\"ok\":false,\"error\":\"unknown_or_malformed_cmd\"}\n");
      std::fflush(stdout);
    }
  }
  return 0;
}
