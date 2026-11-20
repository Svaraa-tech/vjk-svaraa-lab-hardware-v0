/** Svaraa V0 bench / product hardware inventory — from BOM + pinmap + Wokwi harness. */

export type PartStatus = "product" | "sim_standin" | "not_in_wokwi" | "later";

export type HardwarePart = {
  id: string;
  name: string;
  category:
    | "Controllers"
    | "Sensors"
    | "Audio"
    | "UI & feedback"
    | "Power & rails"
    | "Interconnect"
    | "Bench tooling"
    | "Later / gated";
  role: string;
  does: string;
  interface?: string;
  domain?: string;
  status: PartStatus;
  wokwi?: string;
};

export const HARDWARE_PARTS: HardwarePart[] = [
  // Controllers
  {
    id: "B01",
    name: "Arduino Nano ESP32 (ABX00083, with headers)",
    category: "Controllers",
    role: "Main pendant controller",
    does: "Runs SOS qualification, journal, pixels/buzzer/haptic, main I2C, I2S audio, and BLE gateway path. Product MCU is ESP32-S3 — not a classic Nano.",
    interface: "USB-C · Arduino D/A headers",
    domain: "USB_5V + 3V3_NANO",
    status: "sim_standin",
    wokwi: "board-esp32-s3-devkitc-1 stand-in",
  },
  {
    id: "B02",
    name: "Arduino Nicla Voice (ABX00061)",
    category: "Controllers",
    role: "Wake / motion coprocessor",
    does: "Onboard BMI270 IMU, BMM150 magnetometer, wake mic + NDP120 pipeline. Owns private I2C as controller; Nano is target 0x2A. Do not buy a duplicate BMI270.",
    interface: "Micro-USB · ESLOV / private I2C (D3/D4)",
    domain: "NICLA_USB (isolated positives)",
    status: "not_in_wokwi",
    wokwi: "MPU6050 is motion stand-in only — not Nicla target bus",
  },

  // Sensors
  {
    id: "B03",
    name: "Adafruit BMP390 (STEMMA QT)",
    category: "Sensors",
    role: "Barometer / pressure trend",
    does: "Pressure and temperature on the main 3.3 V QT bus (0x77). Used for altitude/trend health — not a direct fall or body-temperature sensor.",
    interface: "I2C main @ 0x77 (A4/A5)",
    domain: "3V3_NANO",
    status: "sim_standin",
    wokwi: "BMP180 stand-in (≠ BMP390)",
  },
  {
    id: "B04",
    name: "SparkFun MAX-M10S Qwiic GNSS (GPS-18037)",
    category: "Sensors",
    role: "Location fix",
    does: "GNSS position for SOS enrichment. Fix is optional and late-arriving — SOS must not wait for a fix. Address 0x42 on main I2C.",
    interface: "I2C main @ 0x42 + antenna",
    domain: "3V3_NANO",
    status: "not_in_wokwi",
  },
  {
    id: "B05",
    name: "Matched L1 GNSS antenna",
    category: "Sensors",
    role: "RF front-end for MAX-M10S",
    does: "Provides the antenna path required by the GNSS module. Connector sex and active/passive must match the board revision.",
    interface: "Matching SMA / module connector",
    status: "not_in_wokwi",
  },

  // Audio
  {
    id: "B06",
    name: "ShillehTek INMP441 (pre-soldered)",
    category: "Audio",
    role: "Conversational PCM microphone",
    does: "External I2S mic for talk/assistant capture. Separate from Nicla’s wake microphone — no ambient upload by default.",
    interface: "I2S BCLK/WS/SD (D5/D6/D7)",
    domain: "3V3_NANO",
    status: "not_in_wokwi",
  },
  {
    id: "B07",
    name: "ShillehTek MAX98357 amp (pre-soldered)",
    category: "Audio",
    role: "Speaker amplifier",
    does: "I2S DAC/amp for playback. Shares BCLK/WS with the mic; DIN on D8. Speaker OUT+/OUT− are differential — neither goes to GND.",
    interface: "I2S BCLK/WS/DIN (D5/D6/D8)",
    domain: "EXT_5V",
    status: "not_in_wokwi",
  },
  {
    id: "B08",
    name: "8 Ω speaker (≥2 W bench)",
    category: "Audio",
    role: "Audible playback transducer",
    does: "Bench speaker for assistant/audio feedback. Volume limited; not a substitute for the independent SOS buzzer.",
    interface: "Amp screw terminals",
    domain: "EXT_5V (via amp)",
    status: "not_in_wokwi",
  },

  // UI & feedback
  {
    id: "B09",
    name: "Adafruit 3630 20-pixel strand (5 logical)",
    category: "UI & feedback",
    role: "Pendant face lights",
    does: "px0 = top status (on/off/recording); px1–px4 = programmable phase bank. Indices 5–19 forced off. During SOS alarm, all five lit solid red.",
    interface: "5 V data via AHCT125 ← Nano D9",
    domain: "EXT_5V pixels / 3V3 logic in",
    status: "sim_standin",
    wokwi: "5× wokwi-neopixel daisy-chain on GPIO18",
  },
  {
    id: "B10",
    name: "TI SN74AHCT125N (PDIP-14)",
    category: "UI & feedback",
    role: "3.3→5 V pixel data buffer",
    does: "Level-shifts Nano pixel GPIO into the 5 V NeoPixel domain. Unused AHCT inputs must be defined; not a generic HC125.",
    interface: "Nano D9 → buffer → pixel DIN",
    domain: "USB_5V VCC · 3V3 OE/logic",
    status: "not_in_wokwi",
  },
  {
    id: "B11",
    name: "Seeed Grove vibration motor",
    category: "UI & feedback",
    role: "Haptic alarm",
    does: "Local vibration feedback during SOS alarm phases. Onboard driver — never wire a bare motor to a GPIO.",
    interface: "Grove SIG ← Nano D12",
    domain: "EXT_5V Grove",
    status: "sim_standin",
    wokwi: "Magenta LED haptic proxy (GPIO14)",
  },
  {
    id: "B12",
    name: "Seeed Grove buzzer",
    category: "UI & feedback",
    role: "Audible local alarm",
    does: "Independent SOS sound path (survives assistant/audio failure). Not Find My–compliant by itself.",
    interface: "Grove SIG ← Nano A0",
    domain: "EXT_5V Grove",
    status: "sim_standin",
    wokwi: "wokwi-buzzer on GPIO1",
  },
  {
    id: "B13",
    name: "NO tactile switch (S1 SOS)",
    category: "UI & feedback",
    role: "Manual SOS",
    does: "Dedicated emergency hold. Debounce ~20 ms; qualify ≥2 s. Held-at-boot must release before arming. Flower-center control on the pendant face.",
    interface: "Nano D2 → GND + 10k pull-up",
    domain: "3V3_NANO",
    status: "product",
    wokwi: "Yellow pushbutton on GPIO5",
  },
  {
    id: "B14",
    name: "Latching SPST/SPDT (S2 Privacy)",
    category: "UI & feedback",
    role: "Software privacy request",
    does: "V0 bench privacy control — stops capture/upload when effective. Not hard mic isolation. Remote unmute cannot override physical privacy-on.",
    interface: "Nano D10 → GND + pull-up",
    domain: "3V3_NANO",
    status: "product",
    wokwi: "Slide switch + orange LED (GPIO21 / GPIO13)",
  },

  // Interconnect
  {
    id: "B15",
    name: "Adafruit passive QT hubs (×2)",
    category: "Interconnect",
    role: "I2C distribution",
    does: "JH1 = main sensor hub (BMP390, GNSS). JH2 = Nicla signal-only adapter hub — V+ unused on Nicla side.",
    interface: "STEMMA QT / Qwiic",
    domain: "3V3_NANO (JH1) · signal-only (JH2)",
    status: "product",
  },
  {
    id: "B16",
    name: "Adafruit QT-to-male cables",
    category: "Interconnect",
    role: "Breakout to breadboard",
    does: "Factory crimped QT → male. Nicla cable V+ lead insulated and unused so positives stay segregated.",
    status: "product",
  },
  {
    id: "B17",
    name: "Adafruit ESLOV-to-QT adapter",
    category: "Interconnect",
    role: "Nicla ESLOV bridge",
    does: "Adapter only — not a voltage converter. Connect through the segregated Nicla hub.",
    status: "product",
  },
  {
    id: "B18",
    name: "Short QT-to-QT cables",
    category: "Interconnect",
    role: "Sensor stubs",
    does: "Hub to barometer / GNSS. Keep short for signal integrity on the main bus.",
    status: "product",
  },
  {
    id: "B19",
    name: "Grove-to-male cables",
    category: "Interconnect",
    role: "Grove SIG/VCC/GND breakout",
    does: "Grove is not Qwiic. Verify SIG/VCC/GND; insulate unused leads.",
    status: "product",
  },
  {
    id: "B20",
    name: "Pixel input pigtail / adapters",
    category: "Interconnect",
    role: "Strand mating",
    does: "Matches Adafruit 3630 polarity and DIN direction — connector shape alone is not enough.",
    status: "product",
  },
  {
    id: "B21",
    name: "Passives (330Ω, 10k, 4.7k, 100nF, 470µF)",
    category: "Interconnect",
    role: "Pull-ups, debounce, decoupling",
    does: "I2C pull-ups, switch pulldowns, pixel data resistor, rail decoupling. Cap polarity matters.",
    status: "product",
  },
  {
    id: "B22",
    name: "830-pt solderless breadboards (×2)",
    category: "Interconnect",
    role: "Bench substrate",
    does: "Solder-free bring-up. Some power rails are split — verify continuity before assuming a continuous rail.",
    status: "product",
  },
  {
    id: "B23",
    name: "M-M / M-F / F-F jumpers",
    category: "Interconnect",
    role: "Signal wiring",
    does: "Factory-crimped jumpers only (no bare-wire soldering). Keep I2S leads short (~10 cm).",
    status: "product",
  },

  // Power
  {
    id: "B24",
    name: "USB-C + Micro-USB data cables",
    category: "Power & rails",
    role: "Host data + power",
    does: "Powers Nano and Nicla independently. Must be data cables — not charge-only.",
    status: "product",
  },
  {
    id: "B25",
    name: "Powered USB data hub",
    category: "Power & rails",
    role: "Port budget",
    does: "Feeds both board USB ports without starving the host. Does not prove battery behavior.",
    status: "product",
  },
  {
    id: "B26",
    name: "Regulated EXT 5 V (≥2 A, fused)",
    category: "Power & rails",
    role: "Load rail",
    does: "Powers amp, pixels, AHCT125 VCC, Grove loads. NEVER tie positive rail to Nano VUSB/3V3. Grounds common; positives segregated.",
    domain: "EXT_5V",
    status: "sim_standin",
    wokwi: "Rail indicator LEDs only",
  },

  // Bench tooling
  {
    id: "B27",
    name: "Multimeter",
    category: "Bench tooling",
    role: "Bring-up safety",
    does: "Continuity and voltage checks before powering assemblies. Instrument ratings must match the measurement.",
    status: "product",
  },
  {
    id: "B28",
    name: "3.3 V USB logic analyzer / power meter (optional)",
    category: "Bench tooling",
    role: "Bus & current debug",
    does: "Recommended for I2C/I2S timing, current draw, and fault diagnosis — not required for SIM profile.",
    status: "product",
  },

  // Later
  {
    id: "B29",
    name: "Nordic nRF9151 DK + SIM (later)",
    category: "Later / gated",
    role: "Cellular data-SOS extension",
    does: "Future modem path. UART/power qualification required; no conventional voice promise.",
    status: "later",
  },
  {
    id: "B30",
    name: "Nordic nRF52840 DK (later)",
    category: "Later / gated",
    role: "Find My / licensed accessory work",
    does: "Independent USB development. Purchase alone is not certification.",
    status: "later",
  },
  {
    id: "B31",
    name: "Protected LiPo + power-path (gated)",
    category: "Later / gated",
    role: "Wearable battery system",
    does: "Matched preassembled charger/gauge/coil only — not an approved ad-hoc battery hookup. Select with a power engineer.",
    status: "later",
  },
  {
    id: "B32",
    name: "Supervisor / wear sensor (V1 PCB, gated)",
    category: "Later / gated",
    role: "Product PCB additions",
    does: "Selected from failure analysis on manufacturer-assembled PCB. Not a vital-sign or medical claim.",
    status: "later",
  },
];

export const HARDWARE_CATEGORIES = [
  "Controllers",
  "Sensors",
  "Audio",
  "UI & feedback",
  "Power & rails",
  "Interconnect",
  "Bench tooling",
  "Later / gated",
] as const;

export const STATUS_LABEL: Record<PartStatus, string> = {
  product: "Bench / product",
  sim_standin: "In Wokwi (stand-in OK)",
  not_in_wokwi: "Not in Wokwi · Lab mock",
  later: "Later / gated",
};
