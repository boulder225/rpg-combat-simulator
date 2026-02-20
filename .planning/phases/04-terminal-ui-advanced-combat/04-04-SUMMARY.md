# Plan 04-04: Fireball AoE — Summary

## Overview
Added Fireball-style sphere AoE: one action type with area shape sphere, radius 4 squares (Manhattan), DEX save, 8d6 fire damage. Simulator resolves all creatures in area; agents can select the action and center cell.

## Deliverables
- **src/domain/creature.py**: Action extended with optional `area_shape` (Literal["sphere"]), `radius_squares`, `save_ability`, `save_dc`, `damage` (DamageRoll); `is_aoe` computed property.
- **src/domain/rules.py**: (existing `make_saving_throw` used)
- **src/simulation/simulator.py**: `_resolve_aoe(state, caster_id, action_obj, center, terrain, logger)` — collect creatures with `manhattan_distance(center, pos) <= radius_squares`, roll damage once, per-target save and full/half damage, apply modifiers; branch in turn loop for `action_type == "aoe"` with `target_position` as center.
- **src/agents/base.py**: `AgentAction.target_position` (Optional[str]) for AoE center.
- **src/agents/heuristic.py**: If creature has action with `is_aoe` and 2+ enemies, return `AgentAction("aoe", attack_name=..., target_position=first_enemy.position)`.
- **src/agents/llm_validator.py**: `_parse_cell()`; for AoE action, validate target as optional cell, return `AgentAction(action_type="aoe", target_position=...)`; `validate_move` allows AoE with target as cell.
- **src/agents/llm_prompt.py**: AoE actions listed with "TARGET = center cell (e.g. D4)"; TARGET line mentions AoE.
- **src/io/markdown.py**: Load action `area_shape`, `radius_squares`, `save_ability`, `save_dc`, `damage` (DamageRoll) from YAML.
- **data/creatures/wizard.md**: Wizard with Fireball (sphere, 4 squares, DEX DC 14, 8d6 fire) and Fire Bolt.
- **tests**: test_action_aoe_fireball (creature), test_aoe_fireball_resolves_damage_in_radius (simulator).

## Verification
- 176 tests pass. Manual: `python run.py --party wizard.md --enemies goblin goblin --seed 42` shows Wizard casting Fireball at A1 and damaging both goblins (and self if in area).

## Issues/Deviations
None. Caster can be in their own AoE (takes save/damage like others).
