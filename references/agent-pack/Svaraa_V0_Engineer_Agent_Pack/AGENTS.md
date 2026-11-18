# Agent implementation contract

Read the entire manual, BOM, pinmap, wire schedule, contracts, Jira plan and test matrix before making changes. Preserve the zero-solder user requirement.

1. Use factory headers/connectors or through-hole breadboard parts. Reject a loose-header, incompatible-connector or bare-SMD substitution.
2. Preserve the main sensor bus and separate Nicla link. Nicla is private-bus controller; Nano is target 0x2A. J5 VCC_IN is a 5 V input and remains isolated. Never merge adapter-hub V+ with the sensor supply.
3. Distinguish Arduino aliases from raw GPIO. Inspect and pin official APIs; do not invent driver functions or claim pseudocode compiled.
4. Five logical lights only; unused bench-strand pixels off. Reset is not SOS. No motor/speaker/pixel load on a GPIO or Nano3V3 rail.
5. Safety state is independent of network, voice and AI. Local trigger, server receipt, human acknowledgment and resolution require different evidence.
6. Real SOS and real qualified sensor candidates preempt drills. Drills have server-issued IDs and only test notification adapters. A lab live-mode event still uses the environment's mock provider until explicitly reviewed.
7. Never mutate queued canonical bytes under the same event ID. Retry idempotently; use new event IDs for later observations on the same incident.
8. S2 privacy is software-enforced in V0. A remote unmute cannot override a closed physical switch. Preserve motion and manual SOS; report unsupported combinations honestly.
9. No credentials in source, disabled TLS checks, cross-household access, invented certified capabilities or unsupervised battery hookups.
10. No physical gate may be closed from a mock, UI animation, host test or successful firmware compile. No production release, irreversible provisioning or real emergency-provider integration without owner approval.

Begin with unchanged host tests. Implement foundation/security stories 01/12, then core and deterministic tests 07/11. Build contract-compatible mock backend/UI 09/10. Hardware receiving/power story 02 runs under a hardware reviewer; real integration 03-06 and native BLE08 follow its gates. Story13 records full bench evidence;14 produces the V1 design brief.

For each small change, record commit, profile, versions, actual tests, outputs, limitations and reviewer under `evidence/<task>/`. Report blockers instead of guessing. Default profile is SIM; notification provider is mock; no ambient audio upload; unknown battery/location stay null.
