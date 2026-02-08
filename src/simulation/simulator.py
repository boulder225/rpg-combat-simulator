"""Combat simulator engine."""

import random
from src.simulation.victory import is_combat_over, get_winner
from src.io.logger import CombatLogger
from src.domain.combat_state import CombatState, roll_initiative
from src.domain import rules


def _find_action(creature, action_name):
    """Find an action by name in creature's actions."""
    for action in creature.actions:
        if action.name == action_name:
            return action
    return None


def run_combat(creatures: dict, agent, seed=None, max_rounds=100, verbose=True):
    """Run a complete combat simulation.

    Args:
        creatures: Dict of creature_id -> Creature
        agent: Agent that chooses actions
        seed: Random seed for reproducibility
        max_rounds: Maximum rounds before ending combat
        verbose: Whether to log to stdout

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
    logger = CombatLogger(verbose=verbose)

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

        for cid in state.initiative_order:
            c = state.creatures[cid]

            # Skip dead creatures
            if c.current_hp <= 0:
                continue

            action = agent.choose_action(state, cid)

            if action.action_type in ("attack", "move_and_attack") and action.target_id:
                # Handle movement
                if action.move_to:
                    old_pos = c.position
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

                        # Make attack roll
                        res = rules.make_attack_roll(atk.attack_bonus, target.ac, None)
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

            elif action.action_type == "move" and action.move_to:
                old_pos = c.position
                state = state.update_creature(cid, position=action.move_to)
                logger.log_movement(c.name, old_pos, action.move_to)

            # Check for combat end
            if is_combat_over(state):
                break

        if is_combat_over(state):
            break

    winner = get_winner(state)
    logger.log_combat_end(winner, rounds)

    return state, logger
