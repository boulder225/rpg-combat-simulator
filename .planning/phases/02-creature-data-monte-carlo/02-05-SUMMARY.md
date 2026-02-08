---
phase: 02-creature-data-monte-carlo
plan: 05
subsystem: cli
tags: [argparse, cli, batch-simulation, creature-loader, monte-carlo]

# Dependency graph
requires:
  - phase: 02-03
    provides: CreatureLoader with SRD API integration and caching
  - phase: 02-04
    provides: MonteCarloSimulator and BatchRunner for batch execution
provides:
  - Unified CLI entry point supporting single and batch simulation modes
  - Argument parsing with support for local files and SRD creature names
  - Progress tracking and comprehensive result display
affects: [03-llm-agents, phase-3, future-cli-enhancements]

# Tech tracking
tech-stack:
  added: [argparse-dataclasses]
  patterns: [dual-mode-cli, srd-name-resolution]

key-files:
  created:
    - src/cli/__init__.py
    - src/cli/batch_args.py
  modified:
    - run.py

key-decisions:
  - "Dual-mode CLI: single combat (no --runs) shows detailed logs, batch mode shows statistics"
  - "Argument parser returns dataclass for type safety and clarity"
  - "Creature name resolution: .md extension = local file, no extension = SRD lookup"
  - "Average wins and losses duration for difficulty rating calculation"

patterns-established:
  - "CLI argument parsing pattern: parse_batch_args returns BatchArgs dataclass"
  - "Creature loading pattern: CreatureLoader handles both local and SRD with auto-numbering"
  - "Results display pattern: win rate, CI, TPK rate, difficulty, duration, damage breakdown"

# Metrics
duration: 3min
completed: 2026-02-08
---

# Phase 2 Plan 5: CLI Integration Summary

**CLI entry point with batch simulation support, SRD creature resolution, and dual-mode operation (single combat vs batch statistics)**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-08T16:31:28Z
- **Completed:** 2026-02-08T16:34:29Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Created CLI argument parser with comprehensive help text and validation
- Integrated CreatureLoader for seamless SRD and local file support
- Implemented dual-mode CLI: single combat with logs vs batch with statistics
- Enabled exact DM workflow: `python run.py --party fighter.md --enemies goblin goblin goblin --runs 500`

## Task Commits

Each task was committed atomically:

1. **Task 1: Create CLI argument parser for batch simulation** - `fc2fe98` (feat)
2. **Task 2: Update main CLI entry point** - `df44fe1` (feat)

## Files Created/Modified

- `src/cli/__init__.py` - CLI module initialization
- `src/cli/batch_args.py` - Argument parsing with BatchArgs dataclass, comprehensive help text
- `run.py` - Main entry point with dual-mode support, creature loading, batch execution

## Decisions Made

**Dual-mode CLI operation**
- Single combat (no --runs): Shows detailed round-by-round logs for tactical analysis
- Batch simulation (with --runs): Shows aggregated statistics with confidence intervals

**Creature name resolution strategy**
- Names with .md extension → Load from local file (e.g., fighter.md)
- Names without extension → SRD API lookup (e.g., goblin)
- CreatureLoader handles three-tier priority: local > SRD cache > API

**Average duration calculation**
- Use average of wins and losses duration for difficulty rating
- Provides balanced view when one outcome dominates

**BatchArgs dataclass**
- Type-safe argument container instead of argparse Namespace
- Makes downstream code clearer with explicit types

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed calculate_difficulty_rating call signature**
- **Found during:** Task 2 (batch simulation result display)
- **Issue:** Missing ci_width and avg_duration parameters in function call
- **Fix:** Added ci_width calculation and avg_duration from win/loss averages
- **Files modified:** run.py
- **Verification:** Batch simulation runs successfully with difficulty rating displayed
- **Committed in:** df44fe1 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Essential fix to call difficulty rating function correctly. No scope creep.

## Issues Encountered

None - plan executed smoothly with one signature mismatch auto-fixed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for Phase 3 (LLM Agents):**
- CLI supports both local creature files and SRD lookups
- Batch simulation with Monte Carlo engine fully operational
- Progress tracking and comprehensive result display implemented
- DM workflow validated: `python run.py --party fighter.md --enemies goblin goblin goblin --runs 500`

**Blockers/Concerns:**
- None

**What's validated:**
- SRD creature names resolve correctly (goblin, orc)
- Local files override SRD data when both exist
- Auto-numbering handles duplicate creatures (goblin_0, goblin_1, goblin_2)
- Batch simulation runs with configurable run counts
- Results include win rate, CI, TPK rate, difficulty rating, duration, and damage breakdown

---
*Phase: 02-creature-data-monte-carlo*
*Completed: 2026-02-08*
