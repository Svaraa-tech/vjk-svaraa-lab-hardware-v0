# Tests — SV0-01.05

| Check | Result | Evidence |
| --- | --- | --- |
| `scripts/test.sh` (host C++ + contracts) | passed (prior host_latest) | `evidence/host_latest/` |
| Evidence profile guard script | present | `scripts/check_evidence_profiles.py` |
| GitHub Actions workflow file | present (not run on this Mac for push) | `.github/workflows/host-tests.yml` |

Note: Workflow execution on GitHub requires remote push; local host suite is the SIM evidence used for Done.
