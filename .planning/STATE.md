# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-07)

**Core value:** A DM can sit down, define creatures in markdown files, run batch simulations, and know within 8 minutes whether an encounter is balanced, deadly, or a TPK — with enough tactical intelligence that the results feel realistic.

**Current focus:** Phase 2 complete. Ready for Phase 3 - LLM Tactical Agents.

## Current Position

Phase: 3 of 5 (LLM Tactical Agents) — COMPLETE
Plan: 3 of 3 in phase 3
Status: Phase 3 verified and complete (6/6 success criteria passed)
Last activity: 2026-02-08 — Phase 3 verified and complete

Progress: [██████████] 100% (Phase 3)
Overall:  [██████░░░░] 60% (3/5 phases)

## Performance Metrics

**Velocity:**
- Total plans completed: 14
- Average duration: ~2.5 min
- Total execution time: ~0.7 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1     | 5     | ~20min | ~4min   |
| 2     | 6     | ~15min | ~2.5min |
| 3     | 3     | ~8min  | ~2.7min |

**Recent Trend:**
- Last 5 plans: 02-04 (3min), 02-05 (2min), 02-06 (2min), 03-01 (3min), 03-02 (2min), 03-03 (3min)
- Trend: Excellent velocity (Phase 3 averaging 2.7min per plan)

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
- **[02-01]** Exponential backoff for SRD API: 1s, 2s, 4s retry timing (balances responsiveness with API courtesy)
- **[02-01]** Multiattack structure: Multiattack action first, then individual attacks (matches D&D stat block convention)
- **[02-01]** Initiative from DEX: Calculate initiative_bonus from dexterity modifier (standard D&D 5e rule)
- **[02-02]** Wilson score over normal approximation: More accurate for small samples and extreme proportions
- **[02-02]** Combined difficulty metrics: Win rate AND TPK risk, label by worse indicator
- **[02-02]** Party-size-adjusted thresholds: 4-player baseline, ±2.5% per player difference
- **[02-03]** Local files always override SRD: DM customizations take precedence over SRD API data
- **[02-03]** Auto-number duplicate creatures: Support multiple instances (goblin_0, goblin_1) in same encounter
- **[02-03]** Cache SRD as markdown: Human-readable, version-controllable creature data
- **[02-04]** Progressive sampling: Start 100 runs, check CI every 100, stop when CI width ≤ 0.10 or max 5000 runs
- **[02-04]** Sequential execution: No multiprocessing for simplicity and deterministic behavior
- **[02-04]** Damage breakdown via log parsing: Non-invasive attribution without instrumenting combat engine
- **[02-06]** Terminal shows top 5 damage sources only: Keeps output concise, markdown has complete breakdown
- **[02-06]** Per-run outcomes limited to 50 rows: Balance detail vs readability in markdown reports
- **[02-06]** Timestamped report filenames: YYYY-MM-DD_HH-MM-SS format prevents overwrites, enables chronological sorting

### Pending Todos

None yet.

### Blockers/Concerns

**Phase 1:** ✓ All resolved
- ~~Advantage/disadvantage~~ ✓ Ternary state machine implemented
- ~~Spatial model~~ Using Manhattan distance, pathfinding deferred

**Phase 2:** ✓ COMPLETE
- ✓ Progressive sampling: Implemented stopping criteria (CI width ≤ 0.10 for ±5% precision)
- ✓ SRD API mapping: Validated with goblin and orc, cache-first loader handles edge cases gracefully
- ✓ Monte Carlo engine: Adaptive sampling with confidence-based stopping complete
- ✓ Batch runner: Progress tracking and comprehensive result collection complete
- ✓ Report generation: Dual output (terminal + markdown) with difficulty ratings and damage breakdown

**Phase 3:**
- LLM prompt engineering: Balance context detail vs 2k-4k token budget for 7B models
- Validation schema: Must reject illegal moves with error feedback to LLM

## Session Continuity

Last session: 2026-02-08
Stopped at: Completed 02-06-PLAN.md (Report generation with dual output) - Phase 2 COMPLETE
Resume file: None
