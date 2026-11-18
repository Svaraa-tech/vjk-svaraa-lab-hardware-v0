#pragma once
#include <array>
#include <cstdint>
#include <cstring>
// Pure reference reducer; caller supplies unique IDs, verified provenance,
// persistence, scheduling, physical input qualification and actual transports.
namespace svaraa {
enum class Phase { Ready, Prealert, Pending, ServerAccepted, HumanAck, Resolved };
enum class Mode { Live, Drill };
enum Action : uint32_t { None=0,CreateEvent=1,Send=2,Feedback=4,CancelRequest=8,
                         DrillInterrupted=16,Audit=32 };
using Id=std::array<char,37>;
inline Id id(const char* s){Id out{};if(s)std::strncpy(out.data(),s,36);return out;}
struct State {Phase phase=Phase::Ready;Mode mode=Mode::Live;Id incident{};
              uint64_t deadline_ms=0;uint32_t revision=0;};
inline bool active(Phase p){return p==Phase::Pending || p==Phase::ServerAccepted || p==Phase::HumanAck;}
inline int rank(Phase p){switch(p){case Phase::Pending:return 1;case Phase::ServerAccepted:return 2;
 case Phase::HumanAck:return 3;case Phase::Resolved:return 4;default:return 0;}}
class Core {
 State s_{};
 uint32_t start(Mode m,const Id& i){s_={Phase::Pending,m,i,0,0};return CreateEvent|Send|Feedback;}
public:
 const State& state()const{return s_;}
 uint32_t fall_candidate(uint64_t now){
  if(s_.phase==Phase::Prealert || (active(s_.phase)&&s_.mode==Mode::Live))return None;
  bool interrupt=active(s_.phase)&&s_.mode==Mode::Drill;
  s_={Phase::Prealert,Mode::Live,{},now+20000,0};
  return Feedback|Audit|(interrupt?DrillInterrupted:0u);
 }
 uint32_t start_drill(const Id& i){if(active(s_.phase)||s_.phase==Phase::Prealert)return None;return start(Mode::Drill,i);}
 uint32_t manual_sos(const Id& i){
  if(s_.mode==Mode::Live&&active(s_.phase))return Feedback;
  bool interrupt=s_.mode==Mode::Drill&&active(s_.phase);
  return start(Mode::Live,i)|(interrupt?DrillInterrupted|Audit:0u);
 }
 uint32_t tick(uint64_t now,const Id& i){if(s_.phase==Phase::Prealert&&now>=s_.deadline_ms)return start(Mode::Live,i);return None;}
 uint32_t cancel(){if(s_.phase==Phase::Prealert){s_=State{};return Feedback|Audit;}
  return active(s_.phase)?CancelRequest|Audit:None;}
 uint32_t update(const Id& i,Mode m,Phase p,uint32_t rev,bool verified){
  if(!verified||i!=s_.incident||m!=s_.mode||rev<=s_.revision||!active(s_.phase)||rank(p)<rank(s_.phase)||rank(p)<2)return None;
  s_.phase=p;s_.revision=rev;return Feedback|Audit;
 }
};
}
