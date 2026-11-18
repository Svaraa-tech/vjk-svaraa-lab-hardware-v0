# Lab UI theme basis — svaraa.ai light & dark

Source: https://www.svaraa.ai/ inspected 2026-11-17  
Evidence screenshots: `evidence/SV0-01.01/theme/svaraa-light.png`, `svaraa-dark.png`  
Owner decision: Lab web views use this light/dark basis (SV0-01.01 v0.2).

## Typography

| Role | Family |
| --- | --- |
| Sans / UI | Inter, Noto Sans Devanagari, ui-sans-serif, system-ui |
| Serif / display | Newsreader, Noto Serif Devanagari, Georgia |
| Mono | ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas |

Engineering surfaces (board tables, traces, charts) stay high-contrast and may prefer sans/mono even when marketing pages use serif headlines.

## Theme toggle

Site uses `data-theme="light" | "dark"` on `<html>` with a header control (`Switch to light theme` / moon for dark). Lab should mirror explicit light/dark (plus optional `system` later) without implying a third product theme.

## Light mode tokens (`:root`)

| Token | Value | Role |
| --- | --- | --- |
| `--c-canvas` | `#fbf7f2` | Page background |
| `--c-heading` | `#4a1532` | Display headings (plum) |
| `--c-ink` | `#3a3340` | Body text |
| `--c-muted` | `#6b6474` | Secondary text |
| `--c-subtle` | `#9a93a1` | Tertiary |
| `--c-primary` | `#6f1d47` | Primary actions / brand |
| `--c-primary-hover` | `#5a173a` | Primary hover |
| `--c-on-primary` | `#fff8f2` | Text on primary |
| `--c-accent` | `#c8505b` | Accent |
| `--c-gold` | `#b88a44` | Gold accent / labels |
| `--c-tint` | `#fbefee` | Soft tint |
| `--c-line` | `#6e1d471f` | Borders |
| `--c-glass` | `#ffffff80` | Glass panel |
| `--c-glass-border` | `#ffffffbf` | Glass edge |
| `--c-glass-strong` | `#ffffffc7` | Strong glass |
| `--c-shadow` | `#4a153233` | Shadow |
| `--c-success` | `#1f9d55` | Success |
| `--c-success-soft` | `#e5f6ec` | Success soft |
| `--c-warn` | `#b7791f` | Warning |
| `--c-warn-soft` | `#fbf1dc` | Warning soft |
| `--c-danger` | `#c53030` | Danger |
| `--c-danger-soft` | `#fdecec` | Danger soft |
| `--c-blob-1/2/3` | `#f4bbc873` / `#d6c4f066` / `#f6d6ac59` | Atmosphere blobs |

## Dark mode tokens (`[data-theme="dark"]`)

| Token | Value | Role |
| --- | --- | --- |
| `--c-canvas` | `#18171a` | Page background |
| `--c-heading` | `#f5efe7` | Display headings |
| `--c-ink` | `#e9e3dc` | Body text |
| `--c-muted` | `#b3aab3` | Secondary |
| `--c-subtle` | `#847c86` | Tertiary |
| `--c-primary` | `#e2bd72` | Primary (gold on dark) |
| `--c-primary-hover` | `#edcb86` | Primary hover |
| `--c-on-primary` | `#22180c` | Text on primary |
| `--c-accent` | `#e6bf74` | Accent |
| `--c-gold` | `#d9b065` | Gold |
| `--c-tint` | `#e2bd7217` | Soft tint |
| `--c-line` | `#ffffff1a` | Borders |
| `--c-glass` | `#2422268c` | Glass panel |
| `--c-glass-border` | `#ffffff14` | Glass edge |
| `--c-glass-strong` | `#28262bd9` | Strong glass |
| `--c-shadow` | `#0000008c` | Shadow |
| `--c-success` | `#4ccf80` | Success |
| `--c-success-soft` | `#4ccf8024` | Success soft |
| `--c-warn` | `#e8b34f` | Warning |
| `--c-warn-soft` | `#e8b34f24` | Warning soft |
| `--c-danger` | `#f07272` | Danger |
| `--c-danger-soft` | `#f0727224` | Danger soft |
| `--c-blob-1/2/3` | `#e2bd721a` / `#6f1d4738` / `#e2bd720f` | Atmosphere |

## Lab application notes

- Default Lab chrome: support both themes; remember preference in localStorage only.
- Mark **SIMULATED** prominently in both themes.
- Do not reduce engineering density for marketing aesthetics; charts/logs must remain readable.
- Pendant appearance follows product design (seven-petal where supported); board/simulator remain tool UIs.
- Implementation of tokens lands in WB-002; this document freezes the basis only.
