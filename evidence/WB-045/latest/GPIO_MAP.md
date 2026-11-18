# Wokwi visual hardware harness — GPIO map

ESP32-S3 DevKitC-1 stands in for the product Nano ESP32. Arduino D-numbers are product labels; Wokwi uses raw GPIOs in `diagram.json`.

| Role | Arduino (product) | Wokwi GPIO | Part | Notes |
| --- | --- | --- | --- | --- |
| SOS button S1 | D2 | **5** | `sos` pushbutton | Hold ≥2s → visual Pending |
| Privacy S2 | D10 | **21** | `privacy` slide switch + orange LED | Software privacy, not hard mic isolation |
| Pixel DIN | D9 | **18** | `px0`…`px4` NeoPixels | 5 V domain; AHCT125 buffer **not** modeled |
| Buzzer | A0 | **1** | `buzzer` | Grove piezo stand-in |
| Haptic | D12 / GPIO47 | **14** | magenta LED | Vibration motor not in Wokwi — LED proxy |
| I2C SDA | A4 | **11** | BMP180 + MPU6050 | Shared main sensor bus |
| I2C SCL | A5 | **12** | BMP180 + MPU6050 | 100 kHz class |

## Stand-ins (honest)

| Product | Wokwi part | Claim |
| --- | --- | --- |
| BMP390 @ 0x77 | `board-bmp180` | Pressure/temp stand-in only |
| Nicla BMI270 | `wokwi-mpu6050` | Motion stand-in — **not** Nicla private bus |
| Grove vibration | LED | Visual proxy |

## Not simulated (Lab typed mocks)

- BLE gateway / ownership
- I2S mic + amp (INMP441)
- Nicla as I2C **target** 0x2A
- MAX-M10S GNSS
- AHCT125 level/buffer IC
- Segregated USB positives (rails shown as indicator LEDs only)

**Lab engine remains SOS authority.** This harness is a visual/behavioral subset for Wokwi + PlatformIO.
