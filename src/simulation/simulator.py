"""Combat simulator engine."""

import random
from typing import Optional

from src.simulation.victory import is_combat_over, get_winner
from src.io.logger import CombatLogger
from src.domain.combat_state import CombatState, roll_initiative
from src.domain import rules
from src.domain.cover import get_cover
from src.domain.terrain import Terrain
from src.domain.distance import distance_in_feet, manhattan_distance


def _find_action(creature, action_name):
    """Find an action by name in creature's actions."""
    for action in creature.actions:
        if action.name == action_name:
            return action
    return None


def _get_melee_reach(creature) -> int:
    """Get melee reach in feet from first melee attack (default 5)."""
    for action in creature.actions:
        for atk in action.attacks:
            if atk.reach is not None:
                return atk.reach
            if atk.range is None:
                return 5
    return 5


def _first_melee_attack(creature):
    """Return (action, attack) for first melee attack, or (None, None)."""
    for action in creature.actions:
        for atk in action.attacks:
            if atk.reach is not None or atk.range is None:
                return action, atk
    return None, None


def _resolve_opportunity_attacks(state: CombatState, mover_id: str, from_pos: str, to_pos: str, terrain, logger: CombatLogger):
    """If moving from_pos -> to_pos triggers leave-reach, resolve opportunity attacks. Return updated state."""
    mover = state.creatures[mover_id]
    for enemy_id in state.initiative_order:
        if enemy_id == mover_id:
            continue
        enemy = state.creatures[enemy_id]
        if enemy.current_hp <= 0 or enemy.team == mover.team:
            continue
        if enemy_id in state.reaction_used:
            continue
        reach_ft = _get_melee_reach(enemy)
        if distance_in_feet(from_pos, enemy.position) > reach_ft:
            continue
        if distance_in_feet(to_pos, enemy.position) <= reach_ft:
            continue
        action_obj, atk = _first_melee_attack(enemy)
        if action_obj is None or atk is None:
            continue
        # Resolve one melee attack: enemy -> mover
        target = state.creatures[mover_id]
        cover_bonus = 0
        if terrain is not None:
            cover = get_cover(enemy.position, target.position, terrain)
            cover_bonus = 2 if cover == "half" else 5 if cover == "three-quarters" else 0
        res = rules.make_attack_roll(atk.attack_bonus, target.ac, None, cover_bonus=cover_bonus)
        logger.log_opportunity_attack(enemy.name, target.name, atk.name, res)
        state = state.set_reaction_used(enemy_id)
        if res.is_hit:
            dmg = rules.roll_damage_for_attack(atk.damage.dice, res.is_critical)
            final_damage, modifier_applied = rules.apply_damage_modifiers(
                dmg, atk.damage.damage_type, target
            )
            new_hp = max(0, target.current_hp - final_damage)
            state = state.update_creature(mover_id, current_hp=new_hp)
            logger.log_damage(target.name, final_damage, atk.damage.damage_type, modifier_applied, new_hp)
            if new_hp <= 0:
                logger.log_death(
                    target.name, target.team, atk.damage.damage_type,
                    killer_name=enemy.name, killer_team=enemy.team,
                )
            logger.record_attack_use(enemy.name, action_obj.name, atk.name, final_damage, is_aoe=False)
        if state.creatures[mover_id].current_hp <= 0 or is_combat_over(state):
            break
    return state


def _resolve_aoe(state: CombatState, caster_id: str, action_obj, center: str, terrain: Optional[Terrain], logger: CombatLogger) -> CombatState:
    """Resolve sphere AoE: all creatures within radius_squares (Manhattan) of center make save, take full/half damage."""
    if not action_obj.is_aoe or action_obj.area_shape != "sphere" or not action_obj.damage:
        return state
    radius = action_obj.radius_squares
    save_ability = (action_obj.save_ability or "dex").lower()
    save_dc = action_obj.save_dc or 14
    caster = state.creatures[caster_id]
    dice_expr = action_obj.damage.dice
    damage_type = action_obj.damage.damage_type

    # Collect all creatures in sphere (excluding caster if desired; include enemies and allies in area)
    targets = []
    for cid, cr in state.creatures.items():
        if cr.current_hp <= 0:
            continue
        if manhattan_distance(center, cr.position) <= radius:
            targets.append(cid)

    if not targets:
        logger.log(f"  {caster.name} casts {action_obj.name} at {center}: no creatures in area.")
        return state

    logger.log(f"  {caster.name} casts {action_obj.name} at {center} (radius {radius} squares).")
    roll_total = rules.roll_damage_for_attack(dice_expr, False)
    cover_bonus = 0
    aoe_total_damage = 0
    for tid in targets:
        target = state.creatures[tid]
        if terrain is not None:
            cover = get_cover(center, target.position, terrain)
            cover_bonus = 2 if cover == "half" else 5 if cover == "three-quarters" else 0
        mod = target.ability_scores.get_modifier(save_ability)
        save_result = rules.make_saving_throw(mod, save_dc, None, cover_bonus=cover_bonus)
        half = save_result.is_success
        damage_this = roll_total // 2 if half else roll_total
        final_damage, modifier_applied = rules.apply_damage_modifiers(
            damage_this, damage_type, target
        )
        aoe_total_damage += final_damage
        new_hp = max(0, target.current_hp - final_damage)
        state = state.update_creature(tid, current_hp=new_hp)
        save_str = "saved (half)" if half else "failed"
        mod_str = f" ({modifier_applied})" if modifier_applied else ""
        logger.log(f"    {target.name} {save_str}: {final_damage} {damage_type} damage{mod_str} -> HP: {new_hp}")
        if new_hp <= 0:
            logger.log_death(
                target.name, target.team, damage_type,
                killer_name=caster.name, killer_team=caster.team,
            )
    logger.record_aoe_use(caster.name, action_obj.name, aoe_total_damage)
    return state


def _round_shape_summary(state: CombatState) -> str:
    """Return a short summary of party and enemy shape (name, HP, AC, position) for start of round."""
    party = [c for c in state.creatures.values() if c.team == "party" and c.current_hp > 0]
    enemies = [c for c in state.creatures.values() if c.team == "enemy" and c.current_hp > 0]
    lines = []
    if party:
        parts = [f"{c.name} {c.current_hp}/{c.hp_max} HP AC {c.ac} {c.position}" for c in party]
        lines.append("Party: " + " | ".join(parts))
    if enemies:
        parts = [f"{c.name} {c.current_hp}/{c.hp_max} HP AC {c.ac} {c.position}" for c in enemies]
        lines.append("Enemies: " + " | ".join(parts))
    return "\n".join(lines) if lines else ""


def run_combat(
    creatures: dict,
    agent,
    seed=None,
    max_rounds=100,
    verbose=True,
    terrain: Optional[Terrain] = None,
    lang: str = "en",
    pause_between_rounds: bool = False,
):
    """Run a complete combat simulation.

    Args:
        creatures: Dict of creature_id -> Creature
        agent: Agent that chooses actions
        seed: Random seed for reproducibility
        max_rounds: Maximum rounds before ending combat
        verbose: Whether to log to stdout
        terrain: Optional terrain for cover (half/three-quarters)
        lang: Language for strategy evolution and round labels ("en", "it")
        pause_between_rounds: If True, print round shape summary and wait for Enter each round (LLM mode)

    Returns:
        Tuple of (final_state, logger)
    """
    if seed is not None:
        random.seed(seed)
    
    # Reset circuit breaker for LLM agents between combat runs
    if hasattr(agent, 'reset_circuit_breaker'):
        agent.reset_circuit_breaker()
    
    # Reset circuit breaker for LLM agents between combat runs
    if hasattr(agent, 'reset_circuit_breaker'):
        agent.reset_circuit_breaker()

    # Roll initiative and log results
    logger = CombatLogger(verbose=verbose, lang=lang)

    # Collect initiative rolls for logging
    initiative_rolls = {}
    for creature_id, creature in creatures.items():
        roll = random.randint(1, 20)
        bonus = creature.initiative_bonus
        total = roll + bonus
        initiative_rolls[creature_id] = (roll, bonus, total)
        logger.log_initiative(creature.name, roll, bonus, total)

    # Create sorted initiative order
    initiative_order = sorted(
        initiative_rolls.keys(),
        key=lambda cid: (-initiative_rolls[cid][2], cid)
    )

    # Create initial combat state
    state = CombatState(creatures=creatures, initiative_order=initiative_order)

    rounds = 0
    for r in range(max_rounds):
        rounds += 1
        logger.log_round(rounds)
        # Strategy evolution at beginning of round (previous round's plans), then actions below
        logger.log_strategy_evolution_for_round(rounds - 1)

        if pause_between_rounds and verbose:
            summary = _round_shape_summary(state)
            if summary:
                print(summary)
            try:
                input("Press Enter to proceed...")
            except EOFError:
                pass

        for cid in state.initiative_order:
            c = state.creatures[cid]

            # Skip dead creatures
            if c.current_hp <= 0:
                continue

            action = agent.choose_action(state, cid)
            if getattr(action, "strategy_summary", None):
                logger.log_turn_strategy(rounds, c.name, action.strategy_summary)

            if action.action_type == "aoe" and action.attack_name:
                center = action.target_position or c.position
                action_obj = _find_action(c, action.attack_name)
                if action_obj and action_obj.is_aoe:
                    state = _resolve_aoe(state, cid, action_obj, center, terrain, logger)
                    state = state.next_turn()
                    if is_combat_over(state):
                        break
                    continue

            if action.action_type in ("attack", "move_and_attack") and action.target_id:
                # Handle movement (opportunity attacks before applying new position)
                if action.move_to:
                    old_pos = c.position
                    state = _resolve_opportunity_attacks(state, cid, old_pos, action.move_to, terrain, logger)
                    if is_combat_over(state):
                        break
                    if state.creatures[cid].current_hp <= 0:
                        continue  # Mover dropped by OA; move does not complete
                    state = state.update_creature(cid, position=action.move_to)
                    c = state.creatures[cid]
                    logger.log_movement(c.name, old_pos, action.move_to)

                # Handle attack - find the action (which may contain multiple attacks)
                target = state.creatures[action.target_id]
                action_obj = _find_action(c, action.attack_name)

                if action_obj and action_obj.attacks:
                    # Process ALL attacks in the action (supports Multiattack)
                    for atk in action_obj.attacks:
                        # Re-fetch target in case it was updated
                        target = state.creatures[action.target_id]

                        # Skip if target is already dead
                        if target.current_hp <= 0:
                            break

                        # Cover: effective AC = AC + cover bonus
                        cover_bonus = 0
                        if terrain is not None:
                            cover = get_cover(c.position, target.position, terrain)
                            cover_bonus = 2 if cover == "half" else 5 if cover == "three-quarters" else 0
                        res = rules.make_attack_roll(
                            atk.attack_bonus, target.ac, None, cover_bonus=cover_bonus
                        )
                        logger.log_attack(c.name, target.name, atk.name, res)

                        if res.is_hit:
                            # Roll damage
                            dmg = rules.roll_damage_for_attack(
                                atk.damage.dice, res.is_critical
                            )

                            # Apply damage modifiers (resistance/immunity/vulnerability)
                            final_damage, modifier_applied = rules.apply_damage_modifiers(
                                dmg, atk.damage.damage_type, target
                            )

                            # Calculate new HP (immutable update)
                            new_hp = max(0, target.current_hp - final_damage)

                            # Update state with new HP
                            state = state.update_creature(
                                action.target_id, current_hp=new_hp
                            )

                            # Log damage with modifier info
                            logger.log_damage(
                                target.name,
                                final_damage,
                                atk.damage.damage_type,
                                modifier_applied,
                                new_hp
                            )
                            if new_hp <= 0:
                                logger.log_death(
                                    target.name, target.team, atk.damage.damage_type,
                                    killer_name=c.name, killer_team=c.team,
                                )
                            logger.record_attack_use(c.name, action_obj.name, atk.name, final_damage, is_aoe=False)

            elif action.action_type == "move" and action.move_to:
                old_pos = c.position
                state = _resolve_opportunity_attacks(state, cid, old_pos, action.move_to, terrain, logger)
                if is_combat_over(state):
                    break
                if state.creatures[cid].current_hp <= 0:
                    continue
                state = state.update_creature(cid, position=action.move_to)
                logger.log_movement(c.name, old_pos, action.move_to)

            # Advance turn (resets reaction_used when new round starts)
            state = state.next_turn()

            # Check for combat end
            if is_combat_over(state):
                break

        if is_combat_over(state):
            break

    winner = get_winner(state)
    logger.log_combat_end(winner, rounds)

    return state, logger
