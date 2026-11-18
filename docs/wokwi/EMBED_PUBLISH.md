# Wokwi embed.json publish checklist (WB-026)

Lab Device Simulator stays the SOS authority. Publishing to Wokwi.com only enables an optional elements iframe.

## Prerequisites

1. Open `simulation/wokwi` in VS Code with **Wokwi for VS Code**.
2. Confirm `diagram.json`, `wokwi.toml`, and a successful `pio run -e sim` (`make wokwi-build` or `scripts/wokwi_build.sh`).
3. Start the Wokwi simulator locally and smoke-check SOS button + 5 NeoPixels.

## Publish

1. In Wokwi for VS Code: **Share / Save to Wokwi.com** (account required).
2. Copy the numeric **project ID** from the published URL (`https://wokwi.com/projects/<id>`).
3. Edit `simulation/wokwi/embed.json`:
   - Set `"project_id": "<id>"` (string or number).
   - Keep `"height_px"` sensible (default 360).
   - Leave limits honest: `ble`, `i2s`, `nicla_target` remain false.
4. Reload Device Simulator → Wokwi panel should show the iframe.
5. Verify `GET /lab/v1/wokwi/embed` → `elements_embed.available: true`.

## Rollback / local-only

Set `"project_id": null` (or remove the field). Panel falls back to Lab-synced visual subset; no iframe.

## Do not claim

- Embed ≠ full product harness (no BLE / I2S / Nicla target).
- Embed ≠ Lab engine authority. Use **Sync from engine** after any visual preview.
- Evidence profile for Wokwi artifacts remains `Wokwi`, not product HW.
