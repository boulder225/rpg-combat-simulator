import random
from src.simulation.victory import is_combat_over, get_winner
from src.io.logger import CombatLogger
from src.domain.combat_state import CombatState
from src.domain import rules


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
            if action.action_type == "attack" and action.target_id:
                target = state.creatures[action.target_id]
                res = rules.make_attack_roll(0, target.ac, None)
                if res.is_hit:
                    rules.apply_damage(target, 1, None)
            if is_combat_over(state):
                break
        if is_combat_over(state):
            break
    winner = get_winner(state)
    logger.log_combat_end(winner, rounds)
    return state, logger
