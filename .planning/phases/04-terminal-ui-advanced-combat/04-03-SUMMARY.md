# Plan 04-03: Opportunity Attacks — Summary

## Overview
Implemented opportunity attacks: when a creature leaves another creature's melee reach during movement, the creature whose reach is left may use its reaction to make one melee attack. Reaction is tracked per round and reset at the start of each new round.

## Deliverables
- **src/domain/combat_state.py**: `reaction_used: frozenset[str]` (creature_ids); `set_reaction_used(creature_id)`; `next_turn()` resets `reaction_used` when advancing to a new round.
- **src/simulation/simulator.py**: `_get_melee_reach(creature)`, `_first_melee_attack(creature)`, `_resolve_opportunity_attacks(state, mover_id, from_pos, to_pos, terrain, logger)`. On move/move_and_attack: call `_resolve_opportunity_attacks` before applying new position; if mover drops to 0 HP from OA, skip position update and attack; advance state with `state.next_turn()` at end of each turn.
- **src/io/logger.py**: `log_opportunity_attack(attacker_name, target_name, attack_name, attack_result)`.

## Verification
- 173 tests pass (including test_reaction_used_default, test_set_reaction_used, test_next_turn_new_round_resets_reaction_used, test_opportunity_attack_on_leave_reach).
- test_opportunity_attack_on_leave_reach: Goblin moves B1→B3 with Fighter at A1; Fighter gets one opportunity attack and reaction_used is set.

## Issues/Deviations
None.
