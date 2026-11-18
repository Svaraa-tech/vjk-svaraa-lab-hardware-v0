# Execution — WB-011

## What changed
- Copied/adapted pack starter → `simulation/wokwi/`
- `GPIO_MAP.md`, enhanced `src/main.cpp` (hold SOS + Serial JSON)
- `pio run -e sim` → `.pio/build/sim/firmware.bin`

## Limitations
- Visual ESP32-S3 DevKit starter ≠ product Nano pinout identity; map documented
- BLE/I2S/Nicla target not simulated
