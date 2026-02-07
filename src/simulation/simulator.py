"""Combat simulator engine."""

import random
from src.simulation.victory import is_combat_over, get_winner
from src.io.logger import CombatLogger
from src.domain.combat_state import CombatState, roll_initiative
from src.domain import rules


def _find_attack(creature, attack_name):
    """Find an attack by name in creature's actions."""
    for action in creature.actions:
        if action.name == attack_name:
            return action.attacks[0] if action.attacks else None
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

    # Roll initiative
    initiative_order = roll_initiative(creatures, seed)

    # Create initial combat state
    state = CombatState(creatures=creatures, initiative_order=initiative_order)
    logger = CombatLogger(verbose=verbose)

    rounds = 0
    for r in range(max_rounds):
        rounds += 1

        for cid in state.initiative_order:
            c = state.creatures[cid]
            action = agent.choose_action(state, cid)

            if action.action_type in ("attack", "move_and_attack") and action.target_id:
                # Handle movement
                if action.move_to:
                    state = state.update_creature(cid, position=action.move_to)
                    c = state.creatures[cid]

                # Handle attack
                target = state.creatures[action.target_id]
                atk = _find_attack(c, action.attack_name)

                if atk:
                    # Make attack roll
                    res = rules.make_attack_roll(atk.attack_bonus, target.ac, None)
                    logger.log(
                        f"  {c.name} attacks {target.name} with {action.attack_name}: "
                        f"{res.description}"
                    )

                    if res.is_hit:
                        # Roll damage
                        dmg = rules.roll_damage_for_attack(
                            atk.damage.dice, res.is_critical
                        )
                        # Apply damage (mutates target)
                        rules.apply_damage(target, dmg, atk.damage.damage_type)
                        # Update state with damaged creature
                        state = state.update_creature(
                            action.target_id, current_hp=target.current_hp
                        )
                        logger.log(
                            f"    {dmg} {atk.damage.damage_type} damage -> "
                            f"{target.name} HP: {target.current_hp}"
                        )

            elif action.action_type == "move" and action.move_to:
                state = state.update_creature(cid, position=action.move_to)

            # Check for combat end
            if is_combat_over(state):
                break

        if is_combat_over(state):
            break

    winner = get_winner(state)
    logger.log_combat_end(winner, rounds)

    return state, logger
