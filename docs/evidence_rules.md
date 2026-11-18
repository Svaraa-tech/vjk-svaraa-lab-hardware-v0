# Evidence rules (SV0-01.05)

## Profiles

| Profile | May claim |
| --- | --- |
| Host / SIM | Logic, contracts, mocks, local API |
| BENCH | Measured hardware only |
| Phone | Native phone tests only |
| Wokwi | Emulation subset only |
| Gated | Licensed/extension studies |

## Hard rules

1. CI running mocks **cannot** set `evidence_profile=BENCH` or mark physical tests passed.
2. `Health::Mocked` / SIM adapters never close T01–T07 electrical gates.
3. Historical pack logs are `source_revision=pack`, not new runs.
4. Each evidence folder needs: command, exit code, versions, profile, result.
5. Owner acceptance is separate from CI green.

## Machine check

`scripts/check_evidence_profiles.py` fails if any committed evidence JSON claims BENCH/Phone pass from host-only tooling.
