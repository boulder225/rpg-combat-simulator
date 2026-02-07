# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-07)

**Core value:** A DM can sit down, define creatures in markdown files, run batch simulations, and know within 8 minutes whether an encounter is balanced, deadly, or a TPK — with enough tactical intelligence that the results feel realistic.

**Current focus:** Phase 1 - Foundation & Core Combat

## Current Position

Phase: 1 of 5 (Foundation & Core Combat)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-02-07 — Roadmap created with 5 phases covering 46 requirements

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: — min
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: None yet
- Trend: Not established

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Python as language: Best ecosystem for D&D APIs, LLM clients, Textual TUI
- Markdown files for all data: Fits DM workflow (Obsidian/text editors), human-readable
- Chess-notation coordinates (A1): Simple spatial reasoning without graphical complexity
- Manhattan distance: Good approximation for D&D 5ft-square movement
- Strict LLM output format: Prevents hallucinated abilities, enables reliable parsing
- Textual for TUI: Rich terminal UI framework with live updates

### Pending Todos

None yet.

### Blockers/Concerns

**Phase 1:**
- Spatial model decision required: Full grid pathfinding vs discrete zones (benchmark both approaches for runtime vs accuracy tradeoff)
- Advantage/disadvantage implementation: Must use ternary state machine, NOT counters (multiple sources cancel completely per 5e rules)

**Phase 2:**
- Monte Carlo sample size: Need progressive sampling (run 500, check CI width, continue if needed for ±5% confidence)
- SRD API mapping: Schema validation required for edge cases (spellcasters, legendary creatures, swarms)

**Phase 3:**
- LLM prompt engineering: Balance context detail vs 2k-4k token budget for 7B models
- Validation schema: Must reject illegal moves with error feedback to LLM

## Session Continuity

Last session: 2026-02-07 (roadmap creation)
Stopped at: Roadmap and STATE.md created, ready to plan Phase 1
Resume file: None
