# ADR-0002 — Lab UI theme from svaraa.ai

Status: **accepted** (owner amendment 2026-11-17 with SV0-01.01 v0.2)  
Date: 2026-11-17

## Context

Lab needs a coherent light/dark visual identity aligned with the product site without sacrificing engineering legibility.

## Decision

Use https://www.svaraa.ai/ CSS custom properties for light (`:root`) and dark (`[data-theme="dark"]`) as the Lab theme basis. Recorded in `docs/architecture/ui_theme_svaraa.md`. Implement in WB-002.

## Consequences

- Plum primary on light; gold primary on dark (site behavior).
- Marketing serif headlines allowed; board/traces prefer sans/mono when clearer.
- Theme preference may use localStorage; product state remains server-authoritative.
