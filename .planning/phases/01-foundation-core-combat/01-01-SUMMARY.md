---
phase: 01-foundation-core-combat
plan: 01
subsystem: foundation
tags: [python, pydantic, grid-system, combat-state, markdown-parser]
requires: []
provides:
  - Pydantic v2 creature models with validation
  - Chess-notation grid system with Manhattan distance
  - Immutable combat state with copy-on-write updates
  - Markdown creature file parser
affects:
  - 01-02: Phase tracking and agent integration
  - 01-03: Core combat wiring
  - 02-*: Monte Carlo simulation
  - 03-*: LLM agent integration
tech-stack:
  added:
    - pydantic>=2.12: Validated data models
    - python-frontmatter>=1.1.0: YAML frontmatter parsing
    - d20>=1.1.2: Dice rolling
  patterns:
    - Immutable data structures with copy-on-write
    - Pydantic computed fields for derived properties
    - Chess notation for grid coordinates (A1, B2, etc.)
key-files:
  created:
    - src/domain/creature.py: Pydantic models for creatures, actions, attacks
    - src/domain/combat_state.py: Immutable combat state
    - src/io/markdown.py: Markdown creature file parser
    - tests/test_creature.py: 19 tests for creature models
    - tests/test_distance.py: 20 tests for grid system
    - tests/test_combat_state.py: 13 tests for combat state
    - tests/test_markdown.py: 10 tests for markdown parser
  modified:
    - src/domain/distance.py: Added parse_coordinate, to_coordinate, validation
    - src/agents/heuristic.py: Updated to use Pydantic Creature
    - src/simulation/simulator.py: Updated to use new combat state
    - run.py: Updated to use markdown parser
    - data/creatures/fighter.md: Updated with Multiattack and hp_max=44
    - data/creatures/goblin.md: Added description fields
decisions:
  - decision: Use Pydantic v2 for creature models
    rationale: 17x faster than v1, excellent validation, computed fields
    alternatives: dataclasses (chosen before), attrs
    impact: All creature data validated at parse time, prevents runtime errors
  - decision: Chess notation for coordinates (A1, B2, etc.)
    rationale: Human-readable, simple to parse, natural for spatial reasoning
    alternatives: (x,y) tuples, algebraic notation
    impact: Easy for humans to read logs and define positions in markdown
  - decision: Immutable combat state with copy-on-write
    rationale: Prevents accidental mutation, enables time-travel debugging, safe for concurrency
    alternatives: mutable state
    impact: All state updates return new CombatState instances
  - decision: python-frontmatter for markdown parsing
    rationale: Standard library for YAML frontmatter, well-maintained
    alternatives: manual YAML parsing, custom parser
    impact: Clean separation of metadata and content in creature files
metrics:
  duration: 6
  completed: 2026-02-07
---

# Phase 01 Plan 01: Foundation Models & Grid System Summary

**One-liner:** Pydantic v2 creature models, chess-notation grid with Manhattan distance, immutable combat state, and markdown parser for creature files.

## What Was Built

### Pydantic Creature Models
Created comprehensive Pydantic v2 models replacing the previous dataclass-based system:

- **AbilityScores**: STR/DEX/CON/INT/WIS/CHA with computed modifiers
- **DeathSaves**: Frozen model tracking successes/failures/stable
- **DamageRoll**: Dice notation (e.g., "1d6+3") with damage type
- **Attack**: Attack bonus, damage, reach/range with computed `range_feet` property
- **Action**: Supports single attacks and Multiattack with computed `is_multiattack` property
- **Creature**: Full creature model with validation, defaults, and `model_copy()` support

All models use Pydantic v2 syntax (`@computed_field`, `@model_validator`) for 17x performance improvement over v1.

### Grid System
Upgraded `src/domain/distance.py` with comprehensive coordinate handling:

- `parse_coordinate(str) -> tuple[int, int]`: Parse chess notation (A1, C4) to (x, y)
- `to_coordinate(x, y) -> str`: Convert coordinates to chess notation
- `manhattan_distance(a, b) -> int`: Taxicab distance in grid squares
- `distance_in_feet(a, b) -> int`: Manhattan distance × 5 feet
- `move_toward(from, to, squares) -> str`: Move toward target up to max squares

Full validation ensures files are A-Z, ranks are 1-99, with clear error messages.

### Immutable Combat State
Created frozen dataclass `CombatState` with copy-on-write operations:

- `update_creature(id, **updates)`: Update creature via `model_copy()`, return new state
- `add_log(message)`: Append log entry, return new state
- `next_turn()`: Advance turn/round, return new state
- `end_combat(winner)`: Mark combat over, return new state
- `roll_initiative(creatures, seed)`: Roll initiative with deterministic ordering (descending roll, alphabetical tiebreaker)

### Markdown Parser
Created `src/io/markdown.py` using python-frontmatter:

- `load_creature(filepath)`: Parse YAML frontmatter into Pydantic Creature
- `load_creatures_from_dir(dirpath)`: Load all creatures from directory
- `load_creature_files(filepaths)`: Load specific creature files

Handles ability scores, actions, attacks, damage rolls, resistances/immunities/vulnerabilities.

### Integration & Testing
- Updated `src/agents/heuristic.py` to use Pydantic Creature
- Updated `src/simulation/simulator.py` to use immutable CombatState
- Updated `run.py` CLI to use markdown parser
- Fixed existing tests to use new Creature API
- Added 62 new tests (19 creature, 20 distance, 13 combat state, 10 markdown)
- **All 75 tests pass**

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test failures in test_rules_basic.py**
- **Found during:** Task 2 - running all tests
- **Issue:** Five tests were using old dataclass API (max_hp instead of hp_max, id instead of no id field, setting attributes after creation)
- **Fix:** Updated tests to use Pydantic model API (hp_max, pass fields in constructor, use damage_resistances parameter)
- **Files modified:** tests/test_rules_basic.py
- **Commit:** Included in Task 2 commit (5c13954)

**2. [Rule 2 - Missing Critical] Added description fields to creature markdown files**
- **Found during:** Task 1 - updating creature files
- **Issue:** Pydantic Action model expects description field but goblin.md had no descriptions
- **Fix:** Added description="Melee weapon attack" and description="Ranged weapon attack" to goblin actions
- **Files modified:** data/creatures/goblin.md
- **Commit:** Included in Task 1 commit (a0c215d)

## Technical Highlights

### Pydantic v2 Performance
Using modern Pydantic v2 features:
- `@computed_field` for derived properties (range_feet, is_multiattack)
- `@model_validator(mode="after")` for cross-field validation (current_hp defaults to hp_max)
- `model_copy(update={...})` for copy-on-write updates
- Frozen models where appropriate (DeathSaves)

### Grid System Validation
Comprehensive input validation prevents invalid coordinates:
- Case-insensitive file parsing (a1 → A1)
- Range validation (files A-Z, ranks 1-99)
- Clear error messages for debugging

### Initiative Ordering
Deterministic initiative with proper tiebreaking:
1. Higher roll wins
2. Ties broken alphabetically by creature_id
3. Seed parameter enables reproducible simulations

### Test Coverage
- 75 total tests passing
- Unit tests for all core functionality
- Integration test verifies end-to-end CLI
- All verification checks pass

## Verification Results

✅ All 75 tests pass
✅ Creature import works
✅ Markdown parser loads goblin: AC 15, HP 7
✅ Manhattan distance A1→C4 = 5 squares
✅ CLI runs end-to-end: `uv run python run.py --party data/creatures/fighter.md --enemies data/creatures/goblin.md --seed 42`

Sample output:
```
Fighter attacks Goblin with Multiattack: Miss. (rolled 9+5=14 vs AC 15)
Goblin attacks Fighter with Scimitar: Miss. (rolled 8+4=12 vs AC 18)
...
Combat Over. Winner: party in 4 rounds
```

## Next Phase Readiness

**Ready to proceed:** ✅

**What's unlocked:**
- Phase 1 Plan 2: Can now add combat phases (movement, reactions, bonus actions)
- Phase 1 Plan 3: Can wire up complete combat loop with initiative
- Phase 2: Can run Monte Carlo simulations with deterministic seeds
- Phase 3: Can define LLM agent action format using Pydantic models

**Blockers:** None

**Notes:**
- Current implementation mutates creature HP in rules.apply_damage() - should be refactored to immutable pattern in future plans
- Death saves tracked in DeathSaves model but death save logic in rules.py still uses old attributes - needs alignment
- Consider adding Position type alias for coordinate strings to improve type hints
