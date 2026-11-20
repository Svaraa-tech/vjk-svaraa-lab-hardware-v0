import { useEffect, useState } from "react";
import { api, probeLabApi } from "./api";
import { DeviceSimulator } from "./components/DeviceSimulator";
import { FeatureList } from "./components/FeatureList";
import { HardwareParts } from "./components/HardwareParts";
import { IntegrationGuide } from "./components/IntegrationGuide";
import { ProjectBoard } from "./components/ProjectBoard";
import { ReferenceGallery } from "./components/ReferenceGallery";
import { WokwiLiveEmbed } from "./components/WokwiLiveEmbed";
import { applyTheme, readStoredTheme, toggleTheme, type Theme } from "./theme";

type Tab =
  | "board"
  | "simulator"
  | "gallery"
  | "integration"
  | "wokwi"
  | "hardware"
  | "features";

export default function App() {
  const [theme, setTheme] = useState<Theme>("light");
  const [tab, setTab] = useState<Tab>("board");
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const [staticPages, setStaticPages] = useState(false);

  useEffect(() => {
    const initial = readStoredTheme();
    applyTheme(initial);
    setTheme(initial);
  }, []);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const live = await probeLabApi();
      if (cancelled) return;
      setStaticPages(!live);
      if (!live) {
        setApiOk(false);
        return;
      }
      try {
        await api.health();
        if (!cancelled) setApiOk(true);
      } catch {
        if (!cancelled) setApiOk(false);
      }
    })();
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
            Project board · hardware · features · Wokwi live · simulator · BLE ·
            references
          </p>
        </div>
        <div className="header-actions">
          <span
            className={apiOk ? "status-ok" : "status-bad"}
            title={
              staticPages
                ? "Static GitHub Pages — board uses bundled snapshot; Wokwi Live needs no API"
                : "Backend connection"
            }
          >
            {apiOk === null
              ? "API…"
              : apiOk
                ? "API connected"
                : staticPages
                  ? "Pages · static"
                  : "API down"}
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
          aria-current={tab === "hardware" ? "page" : undefined}
          onClick={() => setTab("hardware")}
        >
          Hardware
        </button>
        <button
          type="button"
          className="tab"
          aria-current={tab === "features" ? "page" : undefined}
          onClick={() => setTab("features")}
        >
          Feature List
        </button>
        <button
          type="button"
          className="tab"
          aria-current={tab === "wokwi" ? "page" : undefined}
          onClick={() => setTab("wokwi")}
        >
          Wokwi Live
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
        ) : tab === "hardware" ? (
          <HardwareParts />
        ) : tab === "features" ? (
          <FeatureList />
        ) : tab === "wokwi" ? (
          <WokwiLiveEmbed />
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
