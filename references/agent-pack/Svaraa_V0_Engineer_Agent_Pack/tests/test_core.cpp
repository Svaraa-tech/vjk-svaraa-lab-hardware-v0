#include "../firmware/sos_core.hpp"
#include <cassert>
#include <iostream>
using namespace svaraa;
int main(){
 int checks=0;
 auto check=[&](bool ok){assert(ok);++checks;};
 auto a=id("00000000-0000-4000-8000-000000000001");
 auto b=id("00000000-0000-4000-8000-000000000002");Core c;
 check(c.state().phase==Phase::Ready);
 check(c.fall_candidate(100)&Feedback);
 check(c.state().phase==Phase::Prealert);
 check(c.tick(20099,a)==None);
 check(c.tick(20100,a)&CreateEvent);
 check(c.state().phase==Phase::Pending);
 check(!(c.manual_sos(b)&CreateEvent));
 check(c.state().incident==a);
 check(c.update(a,Mode::Live,Phase::HumanAck,1,false)==None);
 check(c.update(b,Mode::Live,Phase::HumanAck,1,true)==None);
 check(c.update(a,Mode::Drill,Phase::HumanAck,1,true)==None);
 check(c.update(a,Mode::Live,Phase::ServerAccepted,1,true)&Feedback);
 check(c.cancel()&CancelRequest);
 check(c.state().phase==Phase::ServerAccepted);
 check(c.update(a,Mode::Live,Phase::HumanAck,2,true)&Feedback);
 check(c.update(a,Mode::Live,Phase::ServerAccepted,3,true)==None);
 check(c.update(a,Mode::Live,Phase::Resolved,2,true)==None);
 check(c.update(a,Mode::Live,Phase::Resolved,4,true)&Audit);
 check(c.start_drill(b)&CreateEvent);
 check(c.manual_sos(a)&DrillInterrupted);
 check(c.state().mode==Mode::Live);
 check(c.start_drill(b)==None);
 Core d;d.fall_candidate(1);check(d.cancel()&Audit);
 check(d.state().phase==Phase::Ready);check(d.tick(99999,a)==None);
 d.fall_candidate(1);check(d.manual_sos(b)&Send);check(d.tick(99999,a)==None);
 Core e;e.start_drill(b);check(e.fall_candidate(500)&DrillInterrupted);
 check(e.state().phase==Phase::Prealert);check(e.state().mode==Mode::Live);
 check(e.tick(20500,a)&CreateEvent);
 std::cout<<"PASS: "<<checks<<" host reducer checks; no physical hardware tested\n";
}
