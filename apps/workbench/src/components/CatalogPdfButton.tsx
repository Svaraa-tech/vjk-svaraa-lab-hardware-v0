import { useState } from "react";
import { downloadCatalogPdf } from "../lib/catalogPdf";

type Props = {
  className?: string;
};

export function CatalogPdfButton({ className }: Props) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  return (
    <span className={className ?? "feat-pdf-wrap"}>
      <button
        type="button"
        className="btn-secondary feat-pdf-btn"
        disabled={busy}
        onClick={() => {
          setErr(null);
          setBusy(true);
          void downloadCatalogPdf()
            .catch((e: unknown) => {
              setErr(e instanceof Error ? e.message : "PDF export failed");
            })
            .finally(() => setBusy(false));
        }}
      >
        {busy ? "Building PDF…" : "Download PDF · hardware + features"}
      </button>
      {err ? (
        <span className="feat-pdf-err" role="alert">
          {err}
        </span>
      ) : null}
    </span>
  );
}
