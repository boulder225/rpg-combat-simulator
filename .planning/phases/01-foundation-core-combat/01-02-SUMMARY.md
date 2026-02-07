---
phase: 01-foundation-core-combat
plan: 02
subsystem: rules-engine
tags: [dice, d20-library, advantage, state-machine, rules]
status: complete
requires: ["01-01"]
provides: ["dice-engine", "advantage-state-machine", "d20-integration"]
affects: ["01-03", "01-04", "01-05"]
tech-stack:
  added: ["d20 library v1.1.2"]
  patterns: ["ternary state machine", "dice expression parsing", "backward compatibility"]
key-files:
  created:
    - src/domain/dice.py
    - tests/test_dice.py
    - tests/test_rules.py
  modified:
    - src/domain/rules.py
decisions:
  - id: "01-02-advantage-ternary"
    title: "Advantage/disadvantage as ternary state machine"
    choice: "ANY advantage + ANY disadvantage = complete cancellation (NORMAL)"
    rationale: "D&D 5e RAW: not a counter system, complete cancellation regardless of source count"
  - id: "01-02-d20-library"
    title: "Use d20 library for all dice rolls"
    choice: "d20.roll() for all d20 and damage rolls with advantage/disadvantage notation"
    rationale: "Industry-standard library, handles 2d20kh1/kl1 notation, tested dice parser"
  - id: "01-02-backward-compat"
    title: "Maintain True/False/None API"
    choice: "Accept AdvantageState OR True/False/None in rules functions"
    rationale: "Existing code uses True/False/None, smooth migration without breaking changes"
metrics:
  duration: "5 min"
  completed: 2026-02-07
  tasks: 2
  commits: 2
  tests-added: 52
  tests-passing: 127
---

# Phase 01 Plan 02: D20 Dice Library Integration Summary

**One-liner:** D20 library integration with ternary advantage state machine (complete cancellation) for all attack/save/damage rolls

## What Was Built

### Dice Engine (src/domain/dice.py)
- **AdvantageState enum:** ADVANTAGE, NORMAL, DISADVANTAGE (ternary state)
- **resolve_advantage():** Ternary state machine - ANY advantage + ANY disadvantage = complete cancellation to NORMAL
- **roll_d20():** Uses d20.roll() with 2d20kh1 (advantage), 2d20kl1 (disadvantage), 1d20 (normal)
- **roll_damage():** Uses d20.roll() for damage expressions, returns (total, string_representation)

### Rules Engine Upgrade (src/domain/rules.py)
- **make_attack_roll():** Now accepts AdvantageState with backward compatibility for True/False/None
- **roll_damage_for_attack():** Uses dice.roll_damage() via d20 library, handles critical hit dice doubling
- **make_saving_throw():** Accepts AdvantageState with backward compatibility
- **make_death_save():** Uses dice.roll_d20(), updated to work with Pydantic v2 DeathSaves model

### Tests
- **tests/test_dice.py:** 22 tests covering advantage resolution state machine, d20 rolling, damage rolling
- **tests/test_rules.py:** 30 comprehensive tests with mocking for all rules functions
- **Backward compatibility verified:** All 127 tests pass

## Decisions Made

### Advantage/Disadvantage as Ternary State Machine
- **Decision:** Implemented as ternary state machine (ADVANTAGE | NORMAL | DISADVANTAGE)
- **NOT counter subtraction:** 3 advantage sources + 1 disadvantage = NORMAL (complete cancellation)
- **Why:** D&D 5e RAW - multiple sources of advantage/disadvantage don't stack or net out
- **Impact:** Prevents common bug where advantage/disadvantage incorrectly accumulates

### D20 Library for All Rolls
- **Decision:** Use d20 library's roll() function for all d20 and damage rolls
- **Benefits:** Industry-standard, tested dice parser, supports complex expressions, string representation
- **Notation:** 2d20kh1 (keep highest), 2d20kl1 (keep lowest)
- **Impact:** More reliable dice rolling, better debugging with string representation

### Backward Compatibility with True/False/None
- **Decision:** Rules functions accept both AdvantageState and legacy True/False/None
- **Conversion:** True → ADVANTAGE, False → DISADVANTAGE, None → NORMAL
- **Why:** Existing simulator code, agents, and tests use True/False/None
- **Impact:** Zero breaking changes, smooth migration path

## Technical Highlights

### Ternary State Machine Implementation
```python
def resolve_advantage(advantage_sources, disadvantage_sources):
    has_advantage = len(advantage_sources) > 0
    has_disadvantage = len(disadvantage_sources) > 0

    if has_advantage and has_disadvantage:
        return AdvantageState.NORMAL  # Complete cancellation
    elif has_advantage:
        return AdvantageState.ADVANTAGE
    elif has_disadvantage:
        return AdvantageState.DISADVANTAGE
    else:
        return AdvantageState.NORMAL
```

### Critical Hit Dice Doubling
```python
# Critical: 1d8+3 → 2d8+3 (doubles dice, not modifier)
if is_critical:
    num_dice, die_size, modifier = parse_dice_expression(damage_dice_str)
    crit_dice_expr = f"{num_dice * 2}d{die_size}"
    if modifier > 0:
        crit_dice_expr += f"+{modifier}"
    damage_total, _ = roll_damage(crit_dice_expr)
```

### Backward Compatibility Pattern
```python
def make_attack_roll(bonus, ac, advantage=None):
    # Convert legacy True/False/None to AdvantageState
    if advantage is True:
        advantage_state = AdvantageState.ADVANTAGE
    elif advantage is False:
        advantage_state = AdvantageState.DISADVANTAGE
    elif advantage is None:
        advantage_state = AdvantageState.NORMAL
    elif isinstance(advantage, AdvantageState):
        advantage_state = advantage
    else:
        advantage_state = AdvantageState.NORMAL

    natural_roll, _ = roll_d20(advantage_state)
```

## Test Coverage

### Dice Module (22 tests)
- Advantage resolution state machine (8 tests)
  - 0/0 sources → NORMAL
  - 1 adv / 0 disadv → ADVANTAGE
  - 0 adv / 1 disadv → DISADVANTAGE
  - 1 adv / 1 disadv → NORMAL (cancellation)
  - 3 adv / 1 disadv → NORMAL (NOT net advantage)
  - 2 adv / 5 disadv → NORMAL (cancellation)
- D20 rolling (7 tests)
  - Normal/advantage/disadvantage valid range (1-20)
  - Return type (int, str)
  - 100 advantage rolls consistency
- Damage rolling (7 tests)
  - Simple/modified/multiple dice expressions
  - Range validation

### Rules Module (30 tests)
- Attack rolls with AdvantageState (10 tests)
  - ADVANTAGE/NORMAL/DISADVANTAGE states
  - Backward compatibility (True/False/None)
  - Natural 20 critical, Natural 1 auto-miss
  - Hit/miss logic
- Damage rolling (5 tests)
  - Normal and critical damage ranges
  - Dice doubling on crit
  - Multiple dice expressions
- Saving throws (6 tests)
  - AdvantageState integration
  - Backward compatibility
  - Success/failure thresholds
- Death saves (3 tests)
  - Dice module integration
  - Natural 20 (restore 1 HP)
  - Natural 1 (2 failures)
- Damage modifiers (3 tests)
  - Immunity/resistance/vulnerability order
- Integration tests (3 tests)
  - AdvantageState passes through to dice module
  - Backward compatibility conversions

## Deviations from Plan

None - plan executed exactly as written.

## Performance

- **Execution time:** 5 minutes
- **Tests added:** 52
- **Total tests passing:** 127
- **Commits:** 2 (one per task)

## Next Phase Readiness

**Ready for 01-03 (Core Combat Wiring):**
- ✅ Dice engine available for simulator loop
- ✅ Advantage/disadvantage ready for tactical agent decisions
- ✅ All rules functions upgraded to use d20 library
- ✅ Backward compatibility maintained for existing code

**Ready for 01-04 (Tactical Agent Upgrade):**
- ✅ AdvantageState available for agent to track and use
- ✅ resolve_advantage() ready for multi-source advantage/disadvantage logic

**No blockers or concerns.**

## Files Modified

### Created
- **src/domain/dice.py** (116 lines) - Dice engine with advantage state machine
- **tests/test_dice.py** (155 lines) - Comprehensive dice module tests
- **tests/test_rules.py** (326 lines) - Comprehensive rules integration tests

### Modified
- **src/domain/rules.py** - Upgraded to use d20 library, added AdvantageState support

## Commit History

1. **ddef42f** - feat(01-02): dice engine with advantage/disadvantage state machine
   - AdvantageState enum, resolve_advantage(), roll_d20(), roll_damage()
   - 22 comprehensive tests

2. **6a31117** - feat(01-02): upgrade rules engine to use d20 library
   - Updated make_attack_roll, roll_damage_for_attack, make_saving_throw, make_death_save
   - Backward compatibility with True/False/None
   - 30 comprehensive tests
   - All 127 tests pass

## Integration Verification

**CLI Test:** `uv run python run.py --party data/creatures/fighter.md --enemies data/creatures/goblin.md --seed 42`

✅ Combat runs successfully
✅ Dice rolls use d20 library
✅ Attack/damage calculations correct
✅ Combat resolution works as expected

**All systems operational.**
