export type Theme = "light" | "dark";

const KEY = "svaraa-v0-lab-theme";

export function readStoredTheme(): Theme {
  const v = localStorage.getItem(KEY);
  return v === "dark" ? "dark" : "light";
}

export function applyTheme(theme: Theme): void {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem(KEY, theme);
}

export function toggleTheme(current: Theme): Theme {
  const next: Theme = current === "light" ? "dark" : "light";
  applyTheme(next);
  return next;
}
