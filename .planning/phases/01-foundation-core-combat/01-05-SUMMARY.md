---
phase: 01-foundation-core-combat
plan: 05
subsystem: combat
tags: [simulator, combat-loop, multiattack, initiative, logging, d20-rules]

# Dependency graph
requires:
  - phase: 01-01
    provides: Pydantic v2 creature models, combat state, rules engine
  - phase: 01-03
    provides: Heuristic agent, simulator loop, logger
provides:
  - Full turn-based combat with proper initiative logging
  - Multiattack support (processes all attacks in action)
  - Structured combat logging with initiative, rounds, attacks, damage
  - Damage modifiers (resistance/immunity/vulnerability) applied correctly
  - Immutable state management (no mutation)
affects: [simulation, monte-carlo, tactical-ai]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Immutable combat state updates via update_creature"
    - "Structured logging for all combat events (initiative, rounds, attacks, damage, movement)"
    - "Multiattack iteration: process all attacks in action.attacks"

key-files:
  created: []
  modified:
    - src/simulation/simulator.py
    - src/agents/heuristic.py

key-decisions:
  - "Roll and log initiative at combat start instead of using pre-rolled order"
  - "Process all attacks in Multiattack actions (iterate action.attacks)"
  - "Apply damage modifiers before HP reduction (immutable pattern)"
  - "Skip dead creatures (current_hp <= 0) in turn order"
  - "Prefer Multiattack actions in heuristic agent for optimal damage output"

patterns-established:
  - "Initiative: Roll with random.randint, log with logger.log_initiative, sort descending"
  - "Round tracking: logger.log_round at start of each round"
  - "Attack flow: log_attack → roll_damage → apply_damage_modifiers → update HP → log_damage"
  - "Movement logging: logger.log_movement with from/to positions"

# Metrics
duration: 2min
completed: 2026-02-07
---

# Phase 01 Plan 05: Combat Loop Upgrade Summary

**Full turn-based combat with Multiattack support, structured logging, and proper damage modifier application**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-07T22:18:16Z
- **Completed:** 2026-02-07T22:20:04Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- Simulator properly logs initiative rolls and round numbers
- Multiattack actions process all attacks (Fighter Multiattack now executes 2 Longsword attacks)
- Damage modifiers (resistance/immunity/vulnerability) applied before HP reduction
- Immutable state management throughout (no creature mutation)
- Heuristic agent prefers Multiattack over single attacks for optimal damage

## Task Commits

Each task was committed atomically:

1. **Task 1: Upgrade simulator with proper initiative and turn-based loop** - `d0ac833` (feat)
2. **Task 2: Improve heuristic agent** - `3f359be` (feat)
3. **Task 3: Verify CLI runs end-to-end** - (verification only, no commit)

**Plan metadata:** (pending)

## Files Created/Modified
- `src/simulation/simulator.py` - Rewritten combat loop with initiative logging, Multiattack support, structured logging, damage modifiers, immutable updates
- `src/agents/heuristic.py` - Enhanced to prefer Multiattack actions and consider ranged attacks when out of melee range

## Decisions Made

1. **Initiative handling:** Instead of calling roll_initiative and getting pre-rolled results, simulator now rolls initiative directly and logs each roll before sorting. This provides visibility into initiative rolls.

2. **Multiattack iteration:** Changed from using `_find_attack` (returned first attack only) to `_find_action` (returns full Action object). Now iterate over `action.attacks` to process all attacks in Multiattack.

3. **Damage modifier flow:** Applied `apply_damage_modifiers` before HP reduction to properly handle resistance/immunity/vulnerability. Log damage with modifier info for visibility.

4. **Immutable HP updates:** Calculate new HP value first, then update state with `update_creature`. Eliminates creature mutation.

5. **Agent preference:** Heuristic agent now prefers Multiattack actions when available and considers ranged attacks based on distance to target.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all tasks executed smoothly. Tests pass (97/97), CLI runs correctly with and without seed, and combat shows proper initiative, rounds, attacks, damage, and winner declaration.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Combat foundation is complete and battle-tested:**
- Turn-based combat loop with initiative
- Multiattack support
- Structured logging for all events
- Damage modifiers applied correctly
- Immutable state management
- Heuristic agent with tactical improvements

**Ready for:**
- Monte Carlo batch simulations (can run thousands of combats reliably)
- Advanced tactical AI (LLM agents can make multi-attack decisions)
- Statistical analysis (structured logs enable parsing for analytics)

**No blockers.**

---
*Phase: 01-foundation-core-combat*
*Completed: 2026-02-07*
