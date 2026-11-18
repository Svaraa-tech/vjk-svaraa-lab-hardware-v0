# Svaraa V0 — Wokwi + PlatformIO visual harness

Run the **actual** ESP32-S3 firmware binary in Wokwi with a wired board that mirrors the pendant UI/sensors as far as Wokwi parts allow (like a full Wokwi.com project canvas).

## Open the simulator (like the example image)

1. Install [Wokwi for VS Code](https://docs.wokwi.com/vscode/getting-started).
2. **File → Open Folder** → this directory: `Svaraa_V0_Lab/simulation/wokwi`.
3. Build once (below), then press the Wokwi **play** button (or Command Palette → `Wokwi: Start Simulator`).
4. You should see ESP32-S3, SOS, privacy switch, NeoPixels, buzzer, haptic LED, BMP180, MPU6050 — same style of interactive canvas as Wokwi.com.

Optional: from Lab Device Simulator use **Open folder in VS Code** (`vscode://file…/simulation/wokwi`).

## Build firmware (PlatformIO)

```bash
cd simulation/wokwi
# preferred if registry works:
pio run -e sim
# workspace/offline override:
pio run -e sim -c platformio_local.ini
# or from Lab root:
make wokwi-build
```

Artifacts: `.pio/build/sim/firmware.bin` + `firmware.elf` (referenced by `wokwi.toml`).

## Interact

| Action | Expected |
| --- | --- |
| Hold **S1 SOS** ≥ 2s | All 5 pixels solid red + buzzer/haptic, serial `mock_sos` |
| Alarm phases (Pending / ServerAccepted) | **All lights red** while sound is on |
| Toggle **S2 Privacy** | Serial `privacy` event |
| Serial `{"cmd":"phase","phase":"HumanAck"}` | Drive pixels from Lab bridge |
| Serial `{"cmd":"sensors"}` | BMP/IMU JSON sample |

## Limits (do not over-claim)

No BLE, no I2S, no Nicla target, no GNSS. BMP180 ≠ BMP390; MPU6050 ≠ Nicla BMI270. Lab engine is SOS authority.
