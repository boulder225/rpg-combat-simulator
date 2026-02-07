from .base import AgentAction
from src.domain.distance import manhattan_distance, move_toward, distance_in_feet


class HeuristicAgent:
    def choose_action(self, state, creature_id: str) -> AgentAction:
        creature = state.creatures[creature_id]
        if creature.current_hp <= 0:
            if not creature.stable:
                return AgentAction(action_type="death_save", description="Death save")
            return AgentAction(action_type="dodge", description="Stable")
        enemies = [(cid, c) for cid, c in state.creatures.items() if c.team != creature.team and c.current_hp > 0]
        if not enemies:
            return AgentAction(action_type="dodge", description="No enemies")
        # nearest enemy
        target_id, target = sorted(
            enemies,
            key=lambda e: (manhattan_distance(creature.position, e[1].position), e[1].current_hp),
        )[0]
        # choose attack
        action = creature.actions[0]
        rng = action.attacks[0].range_feet
        dist = distance_in_feet(creature.position, target.position)
        if dist <= rng:
            return AgentAction(action_type="attack", attack_name=action.name, target_id=target_id)
        # move
        new_pos = move_toward(creature.position, target.position, creature.speed // 5)
        dist2 = distance_in_feet(new_pos, target.position)
        if dist2 <= rng:
            return AgentAction(action_type="move_and_attack", attack_name=action.name, target_id=target_id, move_to=new_pos)
        return AgentAction(action_type="move", move_to=new_pos)
