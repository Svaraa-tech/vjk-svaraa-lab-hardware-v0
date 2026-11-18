# Tests — SV0-01.02

## Acceptance mapping

| ID | Result | Evidence |
| --- | --- | --- |
| A1 folders exist | met | tree under apps/services/firmware/contracts/tests |
| A2 lockfiles/pins | met | `apps/workbench/package-lock.json`, `services/api/requirements.txt`, npm_ls/pip_freeze |
| A3 make doctor | met | doctor exit 0 |
| A4 make test 31+15 | met | `evidence/SV0-01.02/latest/host_*.txt` |
| A5 versions recorded | met | `evidence/SV0-01.02/latest/versions.txt` |
| A6 workbench build + theme code | met | build log; theme.css; **manual** theme toggle review |
| A7 API health 200 | met | `api_v1_health.json`, `api_lab_health.json` |
| N1 no Kanban/sim claim | met | shell copy states placeholders |
| N2 no physical gates | met | |
| N3 references untouched | met | originals not rewritten |

## Commands

```sh
source scripts/env.sh
make doctor
make setup
make test
(cd apps/workbench && npm run build)
# API smoke
uvicorn … ; curl http://127.0.0.1:8000/v1/health
make dev  # then open http://127.0.0.1:5173 manually
```

## Results

| Check | Result |
| --- | --- |
| C++ host | **passed** — 31 checks |
| Python contracts | **passed** — 15 tests |
| Workbench production build | **passed** |
| API health | **passed** (200) |
| Automated browser UI | **not-run** (MCP browser cannot reach host loopback) |

## Manual review for owner

1. `source scripts/env.sh && make dev`
2. Open http://127.0.0.1:5173
3. Confirm SIMULATED banner, brand, placeholder tabs
4. Toggle light/dark
5. Confirm API health line shows `ok · profile=SIM`
6. `make stop`
