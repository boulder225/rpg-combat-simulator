import random
import re
from src.simulation.victory import is_combat_over, get_winner
from src.io.logger import CombatLogger
from src.domain.combat_state import CombatState
from src.domain import rules


def _find_attack(creature, attack_name):
    for action in creature.actions:
        if action.name == attack_name:
            return action.attacks[0] if action.attacks else None
    return None


def _roll_damage(dice_str: str) -> int:
    m = re.match(r"(\d+)d(\d+)([+-]\d+)?", dice_str)
    if not m:
        return 1
    count, sides, mod = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    return sum(random.randint(1, sides) for _ in range(count)) + mod


def run_combat(creatures: dict, agent, seed=None, max_rounds=100, verbose=True):
    if seed is not None:
        random.seed(seed)
    order = list(creatures.keys())
    state = CombatState(creatures, order)
    logger = CombatLogger(verbose=verbose)
    rounds = 0
    for r in range(max_rounds):
        rounds += 1
        for cid in state.initiative_order:
            c = state.creatures[cid]
            action = agent.choose_action(state, cid)
            if action.action_type in ("attack", "move_and_attack") and action.target_id:
                if action.move_to:
                    c = state.creatures[cid]
                    from dataclasses import replace as _replace
                    state = state.update_creature(cid, _replace(c, position=action.move_to))
                target = state.creatures[action.target_id]
                atk = _find_attack(state.creatures[cid], action.attack_name)
                bonus = atk.attack_bonus if atk else 0
                res = rules.make_attack_roll(bonus, target.ac, None)
                logger.log(f"  {state.creatures[cid].name} attacks {target.name} with {action.attack_name}: "
                           f"roll {res.total} vs AC {target.ac} -> {'HIT' if res.is_hit else 'MISS'}")
                if res.is_hit:
                    dmg = _roll_damage(atk.damage_dice) if atk else 1
                    rules.apply_damage(target, dmg, atk.damage_type if atk else None)
                    logger.log(f"    {dmg} {atk.damage_type if atk else ''} damage -> {target.name} HP: {target.current_hp}")
            elif action.action_type == "move" and action.move_to:
                c = state.creatures[cid]
                from dataclasses import replace as _replace
                state = state.update_creature(cid, _replace(c, position=action.move_to))
            if is_combat_over(state):
                break
        if is_combat_over(state):
            break
    winner = get_winner(state)
    logger.log_combat_end(winner, rounds)
    return state, logger
