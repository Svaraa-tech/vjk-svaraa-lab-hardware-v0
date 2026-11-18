# ADR-0001 — Lab stack selection

Status: **proposed** (awaiting owner approval with roadmap P0-v0.1)  
Date: 2026-11-17

## Context

Fresh workspace with pack contracts in Python/C++ and a required two-tab web workbench. Local Mac currently lacks Xcode CLT, Node, and Homebrew.

## Decision (proposed)

Adopt README default: React + TypeScript + Vite frontend; FastAPI + SQLite backend; C++17 JSON-lines bridge to `sos_core.hpp`; Playwright + retained pack host tests. Pin versions during SV0-01.02.

## Consequences

- Single reducer authority remains C++ until a future parity ADR.
- Toolchain bootstrap becomes part of SV0-01.02, not SV0-01.01.
- Incomplete OpenAPI schemas must be frozen before client codegen (SC-002).
