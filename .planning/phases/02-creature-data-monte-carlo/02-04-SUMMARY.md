---
phase: 02-creature-data-monte-carlo
plan: 04
subsystem: simulation
tags: [monte-carlo, progressive-sampling, batch-execution, statistics, confidence-intervals]

# Dependency graph
requires:
  - phase: 02-01
    provides: SRD API integration for creature data loading
  - phase: 02-02
    provides: Wilson score confidence intervals and progressive sampling stopping criteria
  - phase: 01
    provides: Core combat simulation engine with immutable state

provides:
  - Monte Carlo simulation engine with progressive sampling (100 to 5000 runs)
  - Batch runner with progress tracking and comprehensive result collection
  - Damage breakdown attribution by creature and ability type
  - Combat duration analysis for wins vs losses
  - TPK identification and tracking

affects: [03-llm-agents, 04-textual-tui, batch-simulation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Progressive sampling with confidence-based stopping (adaptive algorithm)"
    - "Fresh creature copies for each simulation run (immutable state pattern)"
    - "Damage attribution via combat log parsing"

key-files:
  created:
    - src/simulation/monte_carlo.py
    - src/simulation/batch_runner.py
  modified: []

key-decisions:
  - "Progressive sampling: Start at 100 runs, check CI every 100 runs, stop when CI width ≤ 0.10 or max 5000 runs"
  - "Sequential execution only (no multiprocessing) for simplicity and deterministic behavior"
  - "Damage breakdown parsed from combat logs rather than instrumented during simulation"
  - "Fresh creature copies via Pydantic model_copy(deep=True) ensures immutable state"

patterns-established:
  - "MonteCarloSimulator: Encapsulates progressive sampling algorithm with configurable parameters"
  - "BatchRunner: Coordinates simulation execution with progress tracking and result analysis"
  - "SimulationResults dataclass: Structured container for simulation outcomes with CI"
  - "DamageBreakdown dataclass: Attribution tracking by creature and ability"

# Metrics
duration: 3min
completed: 2026-02-08
---

# Phase 2 Plan 04: Monte Carlo Engine & Batch Runner Summary

**Progressive sampling Monte Carlo engine (100-5000 runs) with confidence-based stopping and comprehensive batch result analysis**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-08T17:18:51Z
- **Completed:** 2026-02-08T17:21:29Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Monte Carlo simulation engine with adaptive progressive sampling
- Confidence-based stopping (±5% precision, CI width ≤ 0.10)
- Batch runner with damage breakdown, duration analysis, and TPK tracking
- Fresh creature instance creation for immutable state guarantee

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement Monte Carlo simulation engine** - `f9f4704` (feat)
2. **Task 2: Implement batch runner with progress tracking** - `dfd1b08` (feat)

## Files Created/Modified

- `src/simulation/monte_carlo.py` - Progressive sampling Monte Carlo simulator with confidence-based stopping
- `src/simulation/batch_runner.py` - Batch execution coordinator with comprehensive result collection and analysis

## Decisions Made

**1. Progressive sampling algorithm:**
- Start: 100 runs (min_runs)
- Check: Every 100 runs (check_interval)
- Stop: When CI width ≤ 0.10 (±5% precision) OR max 5000 runs
- Rationale: Balances statistical rigor with DM time constraints (8-minute target)

**2. Sequential execution:**
- No multiprocessing or parallelization
- Rationale: Simplicity, deterministic behavior with seeding, easier debugging

**3. Damage breakdown via log parsing:**
- Parse CombatLogger entries to attribute damage
- Build attacker/ability context from attack logs
- Rationale: Non-invasive, doesn't require instrumenting core combat engine

**4. Fresh creature copies:**
- Use Pydantic's `model_copy(deep=True)` for each simulation run
- Reset current_hp to hp_max
- Rationale: Ensures immutable state, prevents cross-simulation contamination

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - implementation proceeded smoothly with existing infrastructure from Phase 1 and Plan 02-02.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for Phase 3 (LLM Agents):**
- Monte Carlo engine can be used to evaluate LLM agent performance
- Batch runner provides comprehensive metrics for comparing agents
- Damage breakdown enables tactical analysis of LLM decisions

**Ready for Phase 4 (Textual TUI):**
- BatchRunner progress tracking integrates with live TUI updates
- Comprehensive results (win rate, CI, damage breakdown, duration) display in results panel

**No blockers or concerns.**

---
*Phase: 02-creature-data-monte-carlo*
*Completed: 2026-02-08*
