# Tests — SV0-01.01

## Acceptance mapping

| Criterion | Result | Evidence |
| --- | --- | --- |
| A1 capability statuses explicit | met | `docs/decisions.md` §5 |
| A2 SIM ≠ physical qualification | met | §1–2, matrix notes |
| A3 LIVE + mock provider | met | §1 |
| A4 battery null on USB | met | §5.1 |
| A5 Find My/cellular/hard mic gated | met | §5.6 |
| A6 light/dark tokens recorded | met | `docs/architecture/ui_theme_svaraa.md` + screenshots |
| A7 CLT/Node/Python installed or honest block | met | CLT+Node+Python yes; Homebrew sudo-blocked |
| N1 T01–T07 not marked passed | met | still not-run / electrical |
| N2 historical checks not falsely new | met | new re-runs recorded separately |

## Commands actually run

```sh
softwareupdate -i "Command Line Tools for Xcode 27.2-27.2"
# Node tarball + uv python install (user-local)
c++ -std=c++17 -Wall -Wextra -Werror tests/test_core.cpp -o .../svaraa_test_core
.../svaraa_test_core
python -m venv ... && pip install -r tests/requirements.txt
python -m unittest discover -s tests -p 'test_*.py' -v
```

(from pack directory / evidence paths; see logs)

## Results

| Suite | Result | Log |
| --- | --- | --- |
| C++ host reducer | **passed** — `PASS: 31 host reducer checks` | `evidence/SV0-01.01/baseline_rerun/host_core_rerun.txt` |
| Python contracts | **passed** — 15 tests OK | `evidence/SV0-01.01/baseline_rerun/host_contracts_rerun.txt` |
| T01–T56 electrical/bench | **not-run** | acceptance specs only |
| Homebrew install | **blocked** | insufficient sudo for `/opt/homebrew` |

## Untested / out of scope

- App UI theme rendering (no app yet)
- PlatformIO/Wokwi
- Physical continuity / T01–T07
