# Plan 04-02: Cover in Combat Resolution and CLI --terrain — Summary

## Overview
Wired cover into combat resolution: rules accept cover_bonus, simulator computes cover from terrain and passes it to attack rolls, CLI --terrain loads terrain and passes it through single and batch runs.

## Deliverables
- `src/domain/rules.py`: make_attack_roll(..., cover_bonus=0) uses effective_ac = ac + cover_bonus; make_saving_throw(..., cover_bonus=0) adds cover to save total
- `src/simulation/simulator.py`: run_combat(..., terrain=None); before each attack, get_cover(attacker, target, terrain), cover_bonus 0/2/5, passed to make_attack_roll
- `src/simulation/monte_carlo.py`: run_simulation(..., terrain=None), passed to run_combat
- `src/simulation/batch_runner.py`: run_batch(..., terrain=None), passed to run_simulation
- `src/cli/batch_args.py`: --terrain optional, BatchArgs.terrain
- `run.py`: load terrain via TerrainLoader when args.terrain; pass to run_single_combat and run_batch_simulation
- `data/terrain/arena.md`: sample terrain for manual testing
- `tests/test_rules.py`: test_cover_bonus_increases_effective_ac

## Verification
- 170 tests pass (including new cover_bonus test)
- `python run.py --party fighter.md --enemies goblin --terrain arena` runs and prints "Terrain: Arena"

## Issues/Deviations
None.
