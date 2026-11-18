# Implementation — SV0-01.01

Approved plan: **v0.2**  
Implemented: 2026-11-17 / 2026-11-18 UTC

## What changed and why

Frozen shared vocabulary so later tickets cannot invent certification from mocks, and recorded owner UI/toolchain amendments immediately.

## Actual artifacts

| Path | Change |
| --- | --- |
| `docs/decisions.md` | Profiles, status fields, capability matrix, toolchain notes |
| `docs/architecture/ui_theme_svaraa.md` | Light/dark tokens from svaraa.ai |
| `evidence/SV0-01.01/theme/*.png` | Light + dark screenshots |
| `evidence/SV0-01.01/toolchain_versions.txt` | Installed tool versions |
| `evidence/SV0-01.01/baseline_rerun/` | New host C++/Python runs |
| `evidence/P0_discovery/clt_install_log.txt` | CLT install |
| `scripts/env.sh` | PATH helper for Node + uv Python |
| `docs/tickets/SV0-01.01/plan.md` | Bumped to v0.2 with amendments |

## Host changes (outside repo)

- Installed Xcode CLT 27.2 system-wide
- Installed Node v22.21.1 under `~/.local/node-v22.21.1-darwin-arm64`
- Installed `uv` + CPython 3.12.16 under `~/.local`
- Homebrew `/opt/homebrew` **not** installed (sudo denied)

## Deviations / limitations

- No app scaffold (still SV0-01.02)
- PlatformIO/Wokwi not installed
- Homebrew deferred until owner can grant sudo, or continue with user-local tools
- Theme not yet wired into a running UI (WB-002)

## Known follow-ups

- SV0-01.02 reproducible repository structure + pinned lockfiles
- Optional: Homebrew with sudo if preferred over user-local Node/uv
