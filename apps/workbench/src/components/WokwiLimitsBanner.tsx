import { useEffect, useState } from "react";
import { api, type WokwiDoctor } from "../api";

export function WokwiLimitsBanner() {
  const [doctor, setDoctor] = useState<WokwiDoctor | null>(null);

  useEffect(() => {
    void api.wokwi
      .doctor()
      .then(setDoctor)
      .catch(() => setDoctor(null));
  }, []);

  const embedReady = Boolean(doctor?.embed?.available);
  const phaseCount = doctor?.phases?.count ?? 0;
  const fwOk = Boolean(doctor?.firmware?.present);
  const doctorOk = doctor?.ok;

  return (
    <div className="wokwi-limits-banner" role="status">
      <div>
        <strong>Wokwi visual subset</strong>
        <span aria-hidden="true"> · </span>
        no BLE · no I2S · no Nicla I2C target · mock notifications ·
        evidence_profile=Wokwi
      </div>
      <div className="wokwi-doctor-strip" aria-label="Wokwi doctor readiness">
        <span className={doctorOk ? "chip chip-ok" : "chip chip-miss"}>
          doctor {doctorOk == null ? "…" : doctorOk ? "ok" : "fail"}
        </span>
        <span className={fwOk ? "chip chip-ok" : "chip chip-miss"}>
          firmware {fwOk ? (doctor?.firmware?.sha256 ?? "").slice(0, 8) + "…" : "missing"}
        </span>
        <span className={phaseCount >= 6 ? "chip chip-ok" : "chip chip-miss"}>
          phases {phaseCount || "—"}
        </span>
        <span className={embedReady ? "chip chip-ok" : "chip"}>
          embed {embedReady ? "ready" : "local-only"}
        </span>
      </div>
    </div>
  );
}
