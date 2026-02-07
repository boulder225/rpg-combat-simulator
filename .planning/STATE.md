# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-07)

**Core value:** A DM can sit down, define creatures in markdown files, run batch simulations, and know within 8 minutes whether an encounter is balanced, deadly, or a TPK — with enough tactical intelligence that the results feel realistic.

**Current focus:** Phase 1 - Foundation & Core Combat

## Current Position

Phase: 1 of 5 (Foundation & Core Combat)
Plan: 1 of TBD in current phase
Status: In progress
Last activity: 2026-02-07 — Completed 01-01-PLAN.md (Foundation Models & Grid System)

Progress: [██░░░░░░░░] 20%

## Performance Metrics

**Velocity:**
- Total plans completed: 1
- Average duration: 6 min
- Total execution time: 0.1 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1     | 1     | 6min  | 6min     |

**Recent Trend:**
- Last 5 plans: 01-01 (6min)
- Trend: Establishing baseline

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
- **[01-01]** Pydantic v2 for creature models: 17x faster than v1, excellent validation, computed fields
- **[01-01]** Chess notation for coordinates: Human-readable (A1, B2), easy to parse, natural for spatial reasoning
- **[01-01]** Immutable combat state: Copy-on-write prevents accidental mutation, enables time-travel debugging
- **[01-01]** python-frontmatter for markdown: Standard library for YAML frontmatter parsing

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

Last session: 2026-02-07T22:14:39Z
Stopped at: Completed 01-01-PLAN.md - Foundation Models & Grid System
Resume file: None
