import { jsPDF } from "jspdf";
import {
  HARDWARE_CATEGORIES,
  HARDWARE_PARTS,
  STATUS_LABEL,
  type HardwarePart,
} from "../data/hardwareParts";
import {
  ACTOR_LABEL,
  FEATURE_LIST,
  MATURITY_LABEL,
  PILLAR_META,
  PILLAR_ORDER,
  featureActors,
  featureSvaraas,
  type FeatureItem,
} from "../data/featureList";

const MARGIN = 14;
const PAGE_W = 210;
const PAGE_H = 297;
const CONTENT_W = PAGE_W - MARGIN * 2;
const FOOTER_Y = PAGE_H - 10;

type DocState = {
  doc: jsPDF;
  y: number;
  page: number;
};

function ensureSpace(s: DocState, need: number) {
  if (s.y + need <= FOOTER_Y - 4) return;
  drawFooter(s);
  s.doc.addPage();
  s.page += 1;
  s.y = MARGIN;
}

function drawFooter(s: DocState) {
  s.doc.setFont("helvetica", "normal");
  s.doc.setFontSize(8);
  s.doc.setTextColor(120);
  s.doc.text(
    `Svaraa V0 Lab · Hardware + Features · page ${s.page}`,
    MARGIN,
    FOOTER_Y,
  );
  s.doc.text("svaraa.ai", PAGE_W - MARGIN, FOOTER_Y, { align: "right" });
  s.doc.setTextColor(0);
}

function wrap(doc: jsPDF, text: string, fontSize: number, maxW = CONTENT_W) {
  doc.setFontSize(fontSize);
  return doc.splitTextToSize(text.replace(/\s+/g, " ").trim(), maxW) as string[];
}

function heading(s: DocState, title: string, size = 14) {
  ensureSpace(s, size + 6);
  s.doc.setFont("helvetica", "bold");
  s.doc.setFontSize(size);
  s.doc.setTextColor(40, 20, 60);
  s.doc.text(title, MARGIN, s.y);
  s.y += size * 0.55 + 3;
  s.doc.setTextColor(0);
}

function subheading(s: DocState, title: string) {
  ensureSpace(s, 10);
  s.doc.setFont("helvetica", "bold");
  s.doc.setFontSize(11);
  s.doc.setTextColor(90, 60, 20);
  s.doc.text(title, MARGIN, s.y);
  s.y += 6;
  s.doc.setTextColor(0);
}

function para(s: DocState, text: string, size = 9, leading = 4.2) {
  const lines = wrap(s.doc, text, size);
  ensureSpace(s, lines.length * leading + 2);
  s.doc.setFont("helvetica", "normal");
  s.doc.setFontSize(size);
  s.doc.setTextColor(30);
  for (const line of lines) {
    ensureSpace(s, leading);
    s.doc.text(line, MARGIN, s.y);
    s.y += leading;
  }
  s.y += 1.5;
}

function labeled(s: DocState, label: string, text: string, size = 8.5) {
  const labelW = 28;
  const lines = wrap(s.doc, text, size, CONTENT_W - labelW);
  const leading = 3.9;
  ensureSpace(s, Math.max(1, lines.length) * leading + 1);
  s.doc.setFont("helvetica", "bold");
  s.doc.setFontSize(size);
  s.doc.setTextColor(100);
  s.doc.text(label, MARGIN, s.y);
  s.doc.setFont("helvetica", "normal");
  s.doc.setTextColor(30);
  for (let i = 0; i < lines.length; i++) {
    if (i > 0) ensureSpace(s, leading);
    s.doc.text(lines[i], MARGIN + labelW, s.y);
    s.y += leading;
  }
  s.y += 1;
}

function rule(s: DocState) {
  ensureSpace(s, 4);
  s.doc.setDrawColor(200);
  s.doc.setLineWidth(0.2);
  s.doc.line(MARGIN, s.y, PAGE_W - MARGIN, s.y);
  s.y += 4;
}

function writeHardware(s: DocState) {
  heading(s, "1. Hardware tools (V0 bench BOM)", 16);
  para(
    s,
    `Complete inventory of ${HARDWARE_PARTS.length} parts used or planned for Svaraa V0 solder-free bring-up. Positives stay segregated (Nano USB / Nicla USB / EXT 5V); grounds common.`,
    9,
  );

  for (const cat of HARDWARE_CATEGORIES) {
    const parts = HARDWARE_PARTS.filter((p) => p.category === cat);
    if (!parts.length) continue;
    subheading(s, `${cat} (${parts.length})`);
    for (const p of parts) {
      writePart(s, p);
    }
  }
}

function writePart(s: DocState, p: HardwarePart) {
  ensureSpace(s, 22);
  s.doc.setFont("helvetica", "bold");
  s.doc.setFontSize(10);
  s.doc.setTextColor(20, 40, 80);
  s.doc.text(`${p.id}  ${p.name}`, MARGIN, s.y);
  s.y += 5;
  s.doc.setFont("helvetica", "normal");
  s.doc.setFontSize(8);
  s.doc.setTextColor(110);
  s.doc.text(
    `${p.role}  ·  ${STATUS_LABEL[p.status]}`,
    MARGIN,
    s.y,
  );
  s.y += 4.5;
  labeled(s, "Does", p.does);
  if (p.interface) labeled(s, "Interface", p.interface);
  if (p.domain) labeled(s, "Domain", p.domain);
  if (p.wokwi) labeled(s, "Wokwi/SIM", p.wokwi);
  rule(s);
}

function writeFeatures(s: DocState) {
  heading(s, "2. Feature list — 7 Svaraas + Platform", 16);
  const subCount = FEATURE_LIST.reduce(
    (n, f) => n + (f.subFeatures?.length ?? 0),
    0,
  );
  para(
    s,
    `${FEATURE_LIST.length} features and ${subCount} sub-features for elder care on svaraa.ai. Wearers ↔ caretakers/guardians are many-to-many. Each feature lists primary Svaraa, cross-links, actors, maturity, hardware IDs, and sub-features.`,
    9,
  );

  for (const pillar of PILLAR_ORDER) {
    const feats = FEATURE_LIST.filter((f) => f.pillar === pillar);
    if (!feats.length) continue;
    const meta = PILLAR_META[pillar];
    subheading(
      s,
      `${meta.num}  ${pillar} — ${meta.tagline}  (${feats.length})`,
    );
    for (const f of feats) {
      writeFeature(s, f);
    }
  }
}

function writeFeature(s: DocState, f: FeatureItem) {
  ensureSpace(s, 28);
  s.doc.setFont("helvetica", "bold");
  s.doc.setFontSize(10);
  s.doc.setTextColor(20, 40, 80);
  s.doc.text(`${f.id}  ${f.name}`, MARGIN, s.y);
  s.y += 5;

  const svaraas = featureSvaraas(f)
    .map((p) => {
      const mark = p === f.pillar ? "primary" : "also";
      return `${PILLAR_META[p].num} ${p} (${mark})`;
    })
    .join(" · ");
  const actors = featureActors(f)
    .map((a) => ACTOR_LABEL[a])
    .join(" · ");

  s.doc.setFont("helvetica", "normal");
  s.doc.setFontSize(8);
  s.doc.setTextColor(110);
  const metaLine = wrap(
    s.doc,
    `Svaraa: ${svaraas}  |  Actors: ${actors}  |  ${MATURITY_LABEL[f.maturity]}`,
    8,
  );
  for (const line of metaLine) {
    ensureSpace(s, 3.8);
    s.doc.text(line, MARGIN, s.y);
    s.y += 3.8;
  }
  s.y += 1;

  labeled(s, "Summary", f.summary);
  labeled(s, "Why elders", f.elderWhy);
  labeled(s, "How", f.how);
  labeled(s, "Hardware", f.hardware.join(", "));
  if (f.tags?.length) labeled(s, "Tags", f.tags.join(", "));

  if (f.subFeatures?.length) {
    ensureSpace(s, 6);
    s.doc.setFont("helvetica", "bold");
    s.doc.setFontSize(8.5);
    s.doc.setTextColor(90, 60, 20);
    s.doc.text("Sub-features", MARGIN, s.y);
    s.y += 4;
    for (const sub of f.subFeatures) {
      const who = sub.actors?.map((a) => ACTOR_LABEL[a]).join(" · ");
      labeled(
        s,
        sub.id,
        `${sub.name} — ${sub.summary}${who ? ` [${who}]` : ""}`,
        8,
      );
    }
  }
  rule(s);
}

function writeToc(s: DocState) {
  heading(s, "Contents", 14);
  para(s, "1. Hardware tools (V0 bench BOM)", 10);
  para(s, "2. Feature list — 7 Svaraas + Platform + M:N care graph", 10);
  para(
    s,
    "Notes: Non-clinical — no vital-sign medical device claims. SOS does not wait for GNSS. Privacy latch overrides remote unmute. Cellular / Find My / LiPo remain gated.",
    8.5,
  );
  s.y += 4;
}

/** Build and download the combined Hardware + Features PDF. */
export async function downloadCatalogPdf(): Promise<void> {
  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const s: DocState = { doc, y: MARGIN, page: 1 };

  // Cover
  s.doc.setFont("helvetica", "bold");
  s.doc.setFontSize(22);
  s.doc.setTextColor(40, 20, 60);
  s.doc.text("Svaraa V0 Lab", MARGIN, 40);
  s.doc.setFontSize(16);
  s.doc.text("Hardware tools + Feature catalogue", MARGIN, 52);
  s.doc.setFont("helvetica", "normal");
  s.doc.setFontSize(11);
  s.doc.setTextColor(80);
  s.doc.text("Elder-care wearable platform · 7 Svaraas", MARGIN, 62);
  s.doc.setFontSize(9);
  const stamped = new Date().toISOString().slice(0, 10);
  s.doc.text(`Generated ${stamped}  ·  https://www.svaraa.ai/`, MARGIN, 70);
  s.doc.text(
    `${HARDWARE_PARTS.length} hardware parts  ·  ${FEATURE_LIST.length} features`,
    MARGIN,
    76,
  );
  s.y = 90;
  writeToc(s);
  drawFooter(s);

  doc.addPage();
  s.page += 1;
  s.y = MARGIN;
  writeHardware(s);
  drawFooter(s);

  doc.addPage();
  s.page += 1;
  s.y = MARGIN;
  writeFeatures(s);
  drawFooter(s);

  doc.save(`svaraa-v0-hardware-features-${stamped}.pdf`);
}
