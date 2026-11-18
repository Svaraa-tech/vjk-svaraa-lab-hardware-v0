import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages project site: https://svaraa-tech.github.io/vjk-svaraa-lab-hardware-v0/
const base = process.env.VITE_BASE ?? "/";

export default defineConfig({
  base,
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    // Lab API port (avoid stale :8000 sessions that predate Wokwi routes)
    proxy: {
      "/v1": {
        target: "http://127.0.0.1:18001",
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on("error", (_err, _req, res) => {
            if (res && !res.headersSent && "writeHead" in res) {
              (res as import("http").ServerResponse).writeHead(502, {
                "Content-Type": "application/json",
              });
              (res as import("http").ServerResponse).end(
                JSON.stringify({
                  detail:
                    "Lab API unreachable on :18000 — run scripts/dev.sh",
                }),
              );
            }
          });
        },
      },
      "/lab": {
        target: "http://127.0.0.1:18001",
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on("error", (_err, _req, res) => {
            if (res && !res.headersSent && "writeHead" in res) {
              (res as import("http").ServerResponse).writeHead(502, {
                "Content-Type": "application/json",
              });
              (res as import("http").ServerResponse).end(
                JSON.stringify({
                  detail:
                    "Lab API unreachable on :18000 — run scripts/dev.sh",
                }),
              );
            }
          });
        },
      },
    },
  },
});
