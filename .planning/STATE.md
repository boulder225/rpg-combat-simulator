# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-07)

**Core value:** A DM can sit down, define creatures in markdown files, run batch simulations, and know within 8 minutes whether an encounter is balanced, deadly, or a TPK — with enough tactical intelligence that the results feel realistic.

**Current focus:** Phase 1 complete. Ready for Phase 2 - Creature Data & Monte Carlo Engine.

## Current Position

Phase: 2 of 5 (Creature Data & Monte Carlo Engine) — IN PROGRESS
Plan: 2 of 3 in phase 2
Status: Statistical analysis utilities complete
Last activity: 2026-02-08 — Completed 02-02-PLAN.md (Wilson score CI & difficulty ratings)

Progress: [██░░░░░░░░] 67% (Phase 2: 2/3 plans)
Overall:  [████░░░░░░] 40% (2/5 phases with partial progress)

## Performance Metrics

**Velocity:**
- Total plans completed: 7
- Average duration: ~3.5 min
- Total execution time: ~0.4 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1     | 5     | ~20min | ~4min   |
| 2     | 2     | ~6min  | ~3min   |

**Recent Trend:**
- Last 5 plans: 01-04 (2min), 01-05 (2min), 02-01 (3min), 02-02 (3min)
- Trend: Maintaining fast execution with established patterns

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
- **[01-01]** Immutable combat state: Copy-on-write prevents accidental mutation, enables time-travel debugging
- **[01-01]** python-frontmatter for markdown: Standard library for YAML frontmatter parsing
- **[01-02]** Advantage/disadvantage as ternary state machine: ANY adv + ANY disadv = NORMAL
- **[01-02]** D20 library for all rolls: Industry-standard dice library with 2d20kh1/kl1 notation
- **[01-04]** Full D&D 5e rules engine: attacks, damage with resistance/immunity/vulnerability, death saves, saving throws
- **[01-05]** Multiattack support: Fighter executes 2 attacks per turn via Multiattack action
- **[02-02]** Wilson score over normal approximation: More accurate for small samples and extreme proportions
- **[02-02]** Combined difficulty metrics: Win rate AND TPK risk, label by worse indicator
- **[02-02]** Party-size-adjusted thresholds: 4-player baseline, ±2.5% per player difference

### Pending Todos

None yet.

### Blockers/Concerns

**Phase 1:** ✓ All resolved
- ~~Advantage/disadvantage~~ ✓ Ternary state machine implemented
- ~~Spatial model~~ Using Manhattan distance, pathfinding deferred

**Phase 2:**
- ✓ Progressive sampling: Implemented stopping criteria (CI width ≤ 0.10 for ±5% precision)
- SRD API mapping: Schema validation required for edge cases (spellcasters, legendary creatures, swarms)

**Phase 3:**
- LLM prompt engineering: Balance context detail vs 2k-4k token budget for 7B models
- Validation schema: Must reject illegal moves with error feedback to LLM

## Session Continuity

Last session: 2026-02-08
Stopped at: Completed 02-02-PLAN.md (Statistical analysis utilities)
Resume file: None
