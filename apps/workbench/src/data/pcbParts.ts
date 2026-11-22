/** Production PCB part catalog (P##) — from Svaraa_Feature_Priority_Hardware.xlsx */

export type PcbPart = {
  id: string;
  function: string;
  item: string;
  phase: string;
  interface: string;
  notes: string;
};

export const PCB_PARTS: Record<string, PcbPart> = {
  "P01": {
    id: "P01",
    function: "MCU + BLE",
    item: "Nordic nRF5340 SoC",
    phase: "V0 / P1",
    interface: "BLE 2.4 GHz; QSPI; I²S; I²C/SPI; GPIO",
    notes: "Dual-core app+network; low-power radio, secure boot; no Wi-Fi/embedded LLM. QFN/WLCSP packaging DFM.",
  },
  "P02": {
    id: "P02",
    function: "Always-on voice",
    item: "Syntiant NDP120",
    phase: "V0 / P1 proof",
    interface: "I²S audio from P04; IRQ/SPI/I²C to P01",
    notes: "Optional power-gated wake/keyword/audio processor; integration/licensing/models and I²S bridge must be proven.",
  },
  "P03": {
    id: "P03",
    function: "Microphone",
    item: "Infineon IM73A135V01",
    phase: "V0 / P1 selected",
    interface: "Analog differential OUT+/OUT- → P04 ADC",
    notes: "User-selected 4×3×1.2mm analog bottom-port MEMS, NOT a digital PDM/I²S mic; microphone acoustic port gasket needed.",
  },
  "P04": {
    id: "P04",
    function: "Mic analog ADC",
    item: "TI TLV320ADC3120",
    phase: "V0 / P1",
    interface: "Differential analog input; I²C control; I²S/TDM to P01 and/or P02",
    notes: "3×3mm low-power audio ADC to digitize P03; rail/clock/digital routing must be validated.",
  },
  "P05": {
    id: "P05",
    function: "Speaker amp",
    item: "ADI MAX98357A",
    phase: "V0 / P1",
    interface: "I²S digital input; class-D BTL receiver output",
    notes: "Bare IC replaces ShillehTek MAX98357 board. Peak 1.2W with real 8Ω receiver needs supply/SPL/thermal verification.",
  },
  "P06": {
    id: "P06",
    function: "Speaker/receiver",
    item: "1.2 W compact wearable receiver",
    phase: "V0 / P1 selected",
    interface: "Driven by P05; 4Ω/8Ω TBD",
    notes: "Use exact 1.2W receiver footprint from manufacturer STEP/datasheet; reserve acoustic chamber and metal mesh.",
  },
  "P07": {
    id: "P07",
    function: "Motion and fall candidate",
    item: "ST LSM6DSV16X",
    phase: "V0 / P1",
    interface: "I²C/SPI + motion IRQ",
    notes: "2.5×3mm 6-axis IMU with on-chip FSM/MLC; proposed replacement for Nicla motion path; BMI270 reuse alternate.",
  },
  "P08": {
    id: "P08",
    function: "Pressure sensor",
    item: "Bosch BMP390",
    phase: "V0 / P3 enrichment",
    interface: "I²C/SPI",
    notes: "2×2mm pressure IC in place of QT breakout; isolate from sealed acoustic/vibration cavity.",
  },
  "P09": {
    id: "P09",
    function: "Haptic",
    item: "TI DRV2605L + miniature LRA",
    phase: "V0 / P1",
    interface: "I²C / GPIO; low-voltage actuator",
    notes: "Replaces Grove vibration motor breakout; 6–8 mm actuator size illustrative pending thickness/battery clearance.",
  },
  "P10": {
    id: "P10",
    function: "Lighting",
    item: "5× 2020 RGB LED + NXP PCA9955B",
    phase: "V0 / P1",
    interface: "I²C current driver; 15 of 16 channels",
    notes: "Exact layout: 1 top status + 4 lower LEDs. RGB red SOS, green ACK and gold indicator; NO 20-pixel strand / 5V buffer.",
  },
  "P11": {
    id: "P11",
    function: "Nonvolatile storage",
    item: "64–128 Mbit QSPI NOR flash",
    phase: "V0 / P1",
    interface: "QSPI to P01",
    notes: "Store compressed prayer/audio packs and encrypted SOS/reminder event queue; 8–16 MB not equivalent to 8–16 hours of audio.",
  },
  "P12": {
    id: "P12",
    function: "Battery PMIC",
    item: "Nordic nPM1300 + protected custom LiPo",
    phase: "V0 / P1",
    interface: "Battery + NTC; 5V input; I²C to P01; buck/load switches",
    notes: "Charger, fuel gauge, regulator, ship mode and watchdog; protected cell and thermals mandatory. 845mAh battery candidate does NOT fit 46mm circular disc as dimensioned.",
  },
  "P13": {
    id: "P13",
    function: "Wireless charge Rx",
    item: "TI BQ51013B + custom Qi coil/ferrite",
    phase: "V0 / P1 mechanical",
    interface: "Qi Rx DC out → P12 charge input",
    notes: "Magnet-aligned back puck UX; Qi coil/ferrite spacing and heat tune for metal pendant. Not certified Apple Watch/MagSafe compatible.",
  },
  "P14": {
    id: "P14",
    function: "Center switch",
    item: "Sealed flush momentary tactile switch",
    phase: "V0 / P1",
    interface: "GPIO + pullup/RC + interrupt",
    notes: "One front gold button: short tap secondary; hold ≥2s SOS; firmware release-before-arm boot guard.",
  },
  "P15": {
    id: "P15",
    function: "Privacy hard stop",
    item: "Hardware-latching MIC/ADC supply disconnect",
    phase: "V0 / P1 UX conflict",
    interface: "Hard-switched P03/P04 power rails + state sense",
    notes: "No software/remote override. Existing enclosure constraint says no side control; choose fold-mechanism latch or integrated front control without breaking SOS.",
  },
  "P16": {
    id: "P16",
    function: "GNSS optional",
    item: "u-blox MAX-M10S + matched L1 antenna",
    phase: "P2 / optional",
    interface: "UART or I²C; RF antenna; high-current duty cycle",
    notes: "9.7×10.1×2.5mm module, plus antenna/keepout; phone location first and never block SOS.",
  },
  "P17": {
    id: "P17",
    function: "Cellular upgrade",
    item: "Nordic nRF9151 SiP + LTE antenna/eSIM",
    phase: "P3 / PCB redesign",
    interface: "UART/SPI to P01; LTE-M/NB-IoT; dedicated RF",
    notes: "Data-only SOS when phone absent after carrier coverage, battery, antenna, regulatory feasibility; not a voice-call guarantee.",
  },
  "P18": {
    id: "P18",
    function: "Finding ecosystem",
    item: "Certified/licensed Find My-compatible design",
    phase: "P3 / licensed",
    interface: "BLE radio/security integration per ecosystem rules",
    notes: "No direct replacement for nRF52840 DK or implied certification; begin ecosystem/license qualification.",
  },
  "P19": {
    id: "P19",
    function: "Wear detection optional",
    item: "Skin-contact / capacitive sensor TBD",
    phase: "P3",
    interface: "I²C/analog/GPIO",
    notes: "Off-body gate for false fall escalation. Must validate wearing positions/necklace fabric/skin and opt-in.",
  },
  "P20": {
    id: "P20",
    function: "BLE RF antenna",
    item: "Matched 2.4 GHz antenna + RF filter/matching",
    phase: "V0 / P1",
    interface: "RF50Ω to P01",
    notes: "Antenna keep-out, metal body, neck, coil and battery detuning; RF certification tests.",
  },
  "P21": {
    id: "P21",
    function: "Independent SOS sounder",
    item: "Miniature piezo sounder + driver TBD",
    phase: "V0 / P1",
    interface: "GPIO/timer to protected sounder driver",
    notes: "Independent from music amp for alarm availability, per RX-02 requirement; must actually be audible on worn device.",
  },
  "P22": {
    id: "P22",
    function: "Two-disc interconnect",
    item: "Two rigid circular PCB islands + fatigue-rated flex",
    phase: "V0 / P1",
    interface: "Flex FPC/rigid-flex between discs",
    notes: "Separates logic/audio/button from back charging/battery; folding bridge fatigue, strain relief and EMI need DFM.",
  },
  "P23": {
    id: "P23",
    function: "Factory debug",
    item: "SWD and current-measurement test pads",
    phase: "V0 / EVT",
    interface: "SWD+RESET+GND and gated current test points",
    notes: "Production fixture features only; no user-facing USB port or bench wires, protect test pad exposure.",
  },
};

export function pcbPart(id: string): PcbPart | undefined {
  return PCB_PARTS[id];
}

/** Short capsule label: part number + concise IC/function. */
export function pcbCapsuleLabel(id: string, fallbackDetail?: string): string {
  const p = PCB_PARTS[id];
  if (p) {
    const item = p.item.split(/[,(+]/)[0]?.trim() ?? p.item;
    const short = item.length > 28 ? item.slice(0, 26) + "…" : item;
    return `${id} · ${short}`;
  }
  if (fallbackDetail) {
    const cleaned = fallbackDetail.replace(new RegExp(`^${id}\\s*`), "").trim();
    const short = cleaned.length > 32 ? cleaned.slice(0, 30) + "…" : cleaned;
    return short ? `${id} · ${short}` : id;
  }
  return id;
}

export type PendantPcbCapsule = {
  id: string;
  /** Short display under the P## id (IC / function). */
  title: string;
  /** Full tooltip / accessibility text. */
  detail: string;
  /** Primary SoC (P01). */
  primary: boolean;
  /** Later / gated phase. */
  later: boolean;
};

export type PendantPcbParsed = {
  capsules: PendantPcbCapsule[];
  /** Remaining prose after the part list (implementation note). */
  note?: string;
};

/**
 * Parse Excel “Microcontroller equivalent” text into P## capsules + optional note.
 * Handles `;`, `+`, and `.` separators used in the filled workbook.
 */
export function parsePendantPcb(raw: string): PendantPcbParsed {
  const text = raw.replace(/^MCU:\s*/i, "").trim();
  if (!text) return { capsules: [] };

  const idMatches = [...text.matchAll(/\bP(\d{2})\b/g)];
  if (!idMatches.length) return { capsules: [], note: text };

  const capsules: PendantPcbCapsule[] = [];
  const seen = new Set<string>();

  for (let i = 0; i < idMatches.length; i++) {
    const match = idMatches[i];
    const id = `P${match[1]}`;
    const start = match.index ?? 0;
    const nextStart =
      i + 1 < idMatches.length ? (idMatches[i + 1].index ?? text.length) : text.length;
    let segment = text.slice(start, nextStart).trim();
    // Drop trailing separators before the next part
    segment = segment.replace(/[\s;,+]+$/u, "").trim();
    // For the last part, peel trailing narrative after ". " (sentence start)
    if (i === idMatches.length - 1) {
      const cut = segment.search(/\.\s+(?=[A-Z])/);
      if (cut > 0) {
        const maybeNote = segment.slice(cut + 1).trim();
        if (maybeNote && !/^\s*P\d{2}\b/.test(maybeNote)) {
          segment = segment.slice(0, cut).trim();
        }
      }
    }

    if (seen.has(id)) {
      // Same P## mentioned twice — keep first capsule, append detail later via note skip
      continue;
    }
    seen.add(id);

    const catalog = PCB_PARTS[id];
    const afterId = segment.replace(new RegExp(`^${id}\\s*`), "").trim();
    const itemShort = catalog
      ? (catalog.item.split(/[,(+]/)[0]?.trim() ?? catalog.item)
      : afterId.split(/[\s;]/).filter(Boolean).slice(0, 3).join(" ");
    const title = catalog?.function
      ? itemShort
      : itemShort || afterId.slice(0, 28) || id;

    const detailParts = [
      catalog ? `${id} — ${catalog.function}: ${catalog.item}` : id,
      afterId && afterId !== itemShort ? afterId : null,
      catalog?.phase ? `Phase: ${catalog.phase}` : null,
    ].filter(Boolean);

    capsules.push({
      id,
      title: title.length > 34 ? `${title.slice(0, 32)}…` : title,
      detail: detailParts.join(" · "),
      primary: id === "P01",
      later: /later|P3|optional|licensed/i.test(
        `${catalog?.phase ?? ""} ${afterId}`,
      ),
    });
  }

  // Note = prose after the last part’s sentence boundary (not another P## token)
  let note: string | undefined;
  const last = idMatches[idMatches.length - 1];
  const lastStart = last.index ?? 0;
  const afterLastId = text.slice(lastStart);
  const cut = afterLastId.search(/\.\s+(?=[A-Z])/);
  if (cut > 0) {
    const maybe = afterLastId.slice(cut + 1).trim();
    if (maybe && !/^\s*P\d{2}\b/.test(maybe)) note = maybe;
  }

  return { capsules, note };
}

