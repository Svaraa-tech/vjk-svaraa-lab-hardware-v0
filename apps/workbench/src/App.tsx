import { useEffect, useState } from "react";
import { api } from "./api";
import { DeviceSimulator } from "./components/DeviceSimulator";
import { IntegrationGuide } from "./components/IntegrationGuide";
import { ProjectBoard } from "./components/ProjectBoard";
import { ReferenceGallery } from "./components/ReferenceGallery";
import { applyTheme, readStoredTheme, toggleTheme, type Theme } from "./theme";

type Tab = "board" | "simulator" | "gallery" | "integration";

export default function App() {
  const [theme, setTheme] = useState<Theme>("light");
  const [tab, setTab] = useState<Tab>("board");
  const [apiOk, setApiOk] = useState<boolean | null>(null);

  useEffect(() => {
    const initial = readStoredTheme();
    applyTheme(initial);
    setTheme(initial);
  }, []);

  useEffect(() => {
    let cancelled = false;
    api
      .health()
      .then(() => {
        if (!cancelled) setApiOk(true);
      })
      .catch(() => {
        if (!cancelled) setApiOk(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="shell">
      <div className="banner-sim" role="status">
        Simulated · Profile SIM · notification_provider=mock
      </div>
      <header className="header">
        <div className="brand">
          <h1 className="brand-name">Svaraa V0 Lab</h1>
          <p className="brand-sub">
            Project board · device simulator · BLE integration · references
          </p>
        </div>
        <div className="header-actions">
          <span
            className={apiOk ? "status-ok" : "status-bad"}
            title="Backend connection"
          >
            {apiOk === null ? "API…" : apiOk ? "API connected" : "API down"}
          </span>
          <button
            type="button"
            className="theme-toggle"
            aria-label={
              theme === "dark" ? "Switch to light theme" : "Switch to dark theme"
            }
            onClick={() => setTheme((t) => toggleTheme(t))}
          >
            {theme === "dark" ? "☀︎" : "☾"}
          </button>
        </div>
      </header>

      <nav className="tabs" aria-label="Primary">
        <button
          type="button"
          className="tab"
          aria-current={tab === "board" ? "page" : undefined}
          onClick={() => setTab("board")}
        >
          Project Board
        </button>
        <button
          type="button"
          className="tab"
          aria-current={tab === "simulator" ? "page" : undefined}
          onClick={() => setTab("simulator")}
        >
          Device Simulator
        </button>
        <button
          type="button"
          className="tab"
          aria-current={tab === "integration" ? "page" : undefined}
          onClick={() => setTab("integration")}
        >
          BLE Integration
        </button>
        <button
          type="button"
          className="tab"
          aria-current={tab === "gallery" ? "page" : undefined}
          onClick={() => setTab("gallery")}
        >
          References
        </button>
      </nav>

      <div className="tab-body">
        {tab === "board" ? (
          <ProjectBoard />
        ) : tab === "simulator" ? (
          <DeviceSimulator />
        ) : tab === "integration" ? (
          <IntegrationGuide />
        ) : (
          <ReferenceGallery />
        )}
      </div>
    </div>
  );
}
