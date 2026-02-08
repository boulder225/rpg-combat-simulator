---
phase: 02-creature-data-monte-carlo
plan: 06
subsystem: output
tags: [markdown, reporting, statistics, difficulty-rating]

# Dependency graph
requires:
  - phase: 02-02
    provides: "Difficulty rating calculator with win rate and TPK risk analysis"
  - phase: 02-04
    provides: "BatchResults with damage breakdown and combat duration metrics"
provides:
  - "Dual output system: terminal summaries and markdown reports"
  - "ReportGenerator class with timestamped markdown files"
  - "Reports directory structure at data/reports/"
affects: [02-07, phase-03]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Dual output pattern (terminal + persistent file)", "Timestamped file naming for reports"]

key-files:
  created:
    - src/output/report_generator.py
    - src/output/__init__.py
    - data/reports/.gitkeep
  modified: []

key-decisions:
  - "Terminal shows top 5 damage sources only, markdown shows all"
  - "Per-run outcomes table limited to first 50 runs in markdown for readability"
  - "Timestamped filenames: YYYY-MM-DD_HH-MM-SS_simulation_report.md"

patterns-established:
  - "Terminal summary: Concise format for immediate DM feedback with win rate, CI, difficulty"
  - "Markdown report: Comprehensive session prep document with per-run outcomes table"
  - "Error handling: Proper OSError handling for directory creation and file writes"

# Metrics
duration: 2min
completed: 2026-02-08
---

# Phase 2 Plan 6: Report Generation Summary

**Dual output system producing terminal summaries and timestamped markdown reports with difficulty ratings and damage breakdown**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-08T16:31:56Z
- **Completed:** 2026-02-08T16:33:59Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Terminal summary generator with win rate, CI bounds, difficulty rating, duration, and top damage sources
- Markdown report generator with full statistics, per-run outcomes table, and difficulty explanation
- Reports directory structure at data/reports/ alongside creatures/ and srd-cache/
- Timestamped report filenames for session prep organization

## Task Commits

Each task was committed atomically:

1. **Task 1: Create report generator with dual output** - `2876e2d` (feat)
2. **Task 2: Create reports directory structure** - `4e08c94` (chore)

## Files Created/Modified

- `src/output/report_generator.py` - ReportGenerator class with terminal and markdown output methods
- `src/output/__init__.py` - Output module initialization
- `data/reports/.gitkeep` - Reports directory tracking

## Decisions Made

**Terminal output design:**
- Show win rate as CI range (69%-77%) for immediate uncertainty visibility
- Include top 5 damage sources only to keep terminal concise
- Format: "Party wins: 69%-77% (95% CI) - Medium difficulty"

**Markdown report structure:**
- Per-run outcomes table limited to first 50 runs for readability (total count shown)
- Include difficulty rating explanation section with threshold definitions
- Full damage breakdown by creature and by ability in separate tables

**File naming:**
- Timestamped format: `YYYY-MM-DD_HH-MM-SS_simulation_report.md`
- Enables chronological sorting and prevents overwrites
- Integrates with DM session prep workflow (Obsidian/markdown editors)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for CLI integration (02-07):**
- ReportGenerator can be instantiated with BatchResults
- Terminal summary ready for display to user
- Markdown report ready for automatic save to data/reports/
- All dependencies (difficulty.py, batch_runner.py) available

**Terminal format matches spec:**
- "Party wins: X%-Y% (95% CI) - [Easy/Medium/Hard/Deadly] difficulty"
- Duration breakdown (wins vs losses)
- Damage attribution

**Markdown reports ready for DM workflow:**
- Timestamped filenames prevent overwrites
- Comprehensive statistics for session prep
- Human-readable format for Obsidian/text editors

---
*Phase: 02-creature-data-monte-carlo*
*Completed: 2026-02-08*
