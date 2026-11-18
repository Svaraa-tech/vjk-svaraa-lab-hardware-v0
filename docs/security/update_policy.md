# Signed update / recovery policy — SV0-12.03

SIM freeze (no OTA binary in V0 Lab):

1. Image must declare compatibility + signature fields before accept.
2. During an active incident (`Pending` / `ServerAccepted` / `HumanAck`), OTA is **deferred**.
3. Invalid signature or interrupted write → status `rejected` / `rollback`, never `success`.
4. Workbench must not show optimistic “updated” without verified result.
