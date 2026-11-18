# Execution — SV0-11.01

## What changed
- Wokwi adapter project under `simulation/wokwi/` with GPIO map
- PlatformIO `env:sim` firmware (button + NeoPixels + Serial JSON)
- Lab bridge + API + Device Simulator Wokwi panel (WB-011…013)

## Honest limits
- Separate raw GPIO map; no BLE / I2S / Nicla I2C target simulation
- Behavioral SOS authority remains Lab SimEngine
