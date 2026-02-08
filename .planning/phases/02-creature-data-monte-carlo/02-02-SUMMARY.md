---
phase: 02-creature-data-monte-carlo
plan: 02
subsystem: analysis
tags: [scipy, statistics, monte-carlo, confidence-intervals, difficulty-rating]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: Core combat engine and creature models
provides:
  - Wilson score confidence interval calculator for win rates
  - Progressive sampling stopping criteria for adaptive Monte Carlo
  - D&D 5e difficulty rating system (Easy/Medium/Hard/Deadly)
  - Statistical analysis utilities for simulation results
affects: [03-simulation-engine, 04-batch-analysis]

# Tech tracking
tech-stack:
  added: [scipy>=1.11.0]
  patterns:
    - Wilson score method for accurate confidence intervals
    - Combined metrics (win rate AND TPK risk) for difficulty assessment
    - Party-size-adjusted difficulty thresholds

key-files:
  created:
    - src/analysis/__init__.py
    - src/analysis/statistics.py
    - src/analysis/difficulty.py
  modified:
    - pyproject.toml

key-decisions:
  - "Wilson score over normal approximation for CI accuracy with small samples"
  - "Combined win rate AND TPK risk for difficulty (label by worse indicator)"
  - "Party-size-adjusted thresholds (4-player baseline, ±2.5% per player)"
  - "Duration penalty for fights 10+ rounds (shifts difficulty up)"

patterns-established:
  - "Statistical utilities use scipy.stats for accuracy"
  - "Difficulty thresholds align with D&D 5e XP guidelines"
  - "Progressive sampling enables adaptive Monte Carlo (stop when CI width ≤ target)"

# Metrics
duration: 3min
completed: 2026-02-08
---

# Phase 02 Plan 02: Statistical Analysis Utilities Summary

**Wilson score confidence intervals and D&D-aligned difficulty ratings for Monte Carlo simulation analysis**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-08T16:18:03Z
- **Completed:** 2026-02-08T16:20:49Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Implemented Wilson score confidence interval calculator accurate for small samples and extreme proportions
- Created progressive sampling stopping criteria for adaptive Monte Carlo (target ±5% precision)
- Built D&D 5e difficulty rating system combining win rate, TPK risk, and combat duration
- Established statistical analysis foundation for Phase 3 simulation engine

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement Wilson score confidence interval calculator** - `00fc7a4` (feat)
2. **Task 2: Implement D&D difficulty rating calculator** - `045effa` (feat)

## Files Created/Modified

- `src/analysis/__init__.py` - Module exports for statistical utilities
- `src/analysis/statistics.py` - Wilson score CI and progressive sampling criteria
- `src/analysis/difficulty.py` - D&D 5e difficulty rating calculator
- `pyproject.toml` - Added scipy>=1.11.0 dependency

## Decisions Made

**1. Wilson score over normal approximation**
- Wilson score method is more accurate for small sample sizes and extreme proportions (near 0% or 100%)
- Used scipy.stats.binomtest with proportion_ci method="wilson"

**2. Combined metrics for difficulty assessment**
- Labels encounters by the WORSE of win rate OR TPK risk (conservative for DM planning)
- Examples: 60% win rate with 35% TPK risk → Deadly (TPK risk dominates)

**3. Party-size-adjusted thresholds**
- Baseline: 4 players
- Adjustment: ±2.5% per player difference
- Smaller parties need easier encounters to maintain same difficulty feeling

**4. Duration as difficulty factor**
- Fights 10+ rounds get +5% penalty to "Easy" threshold
- Longer combats of same difficulty feel more challenging

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added scipy dependency**
- **Found during:** Task 1 (Wilson score CI implementation)
- **Issue:** scipy not in pyproject.toml dependencies, import failing
- **Fix:** Added scipy>=1.11.0 to dependencies, ran uv sync
- **Files modified:** pyproject.toml, uv.lock
- **Verification:** Import succeeded, function ran correctly
- **Committed in:** 00fc7a4 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking dependency)
**Impact on plan:** Essential dependency for statistical functions. No scope creep.

## Issues Encountered

None - plan executed smoothly after dependency installation.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for Phase 3 (Monte Carlo Simulation Engine):**
- Wilson score CI calculator ready for win rate analysis
- Progressive sampling criteria enable adaptive simulation stopping
- Difficulty rating system ready to label simulation results
- All success criteria passed (CI accuracy, difficulty thresholds)

**Key integration points:**
- Simulation engine will call calculate_win_rate_ci() for results
- Progressive sampling will use progressive_sampling_stopping_criteria() to decide when to stop
- Batch analysis will use calculate_difficulty_rating() to label encounters

**No blockers or concerns.**

---
*Phase: 02-creature-data-monte-carlo*
*Completed: 2026-02-08*
