"""Heuristic combat agent."""

from .base import AgentAction
from src.domain.distance import manhattan_distance, move_toward, distance_in_feet


class HeuristicAgent:
    """Simple heuristic agent that attacks nearest enemy."""

    def choose_action(self, state, creature_id: str) -> AgentAction:
        """Choose action for a creature.

        Args:
            state: Current CombatState
            creature_id: ID of creature choosing action

        Returns:
            AgentAction to execute
        """
        creature = state.creatures[creature_id]

        # If at 0 HP, handle death saves or stable state
        if creature.current_hp <= 0:
            if not creature.death_saves.stable:
                return AgentAction(action_type="death_save", description="Death save")
            return AgentAction(action_type="dodge", description="Stable")

        # Find living enemies
        enemies = [
            (cid, c)
            for cid, c in state.creatures.items()
            if c.team != creature.team and c.current_hp > 0
        ]

        if not enemies:
            return AgentAction(action_type="dodge", description="No enemies")

        # Find nearest enemy
        target_id, target = sorted(
            enemies,
            key=lambda e: (
                manhattan_distance(creature.position, e[1].position),
                e[1].current_hp,
            ),
        )[0]

        # Choose best action - prefer Multiattack over single attacks
        if not creature.actions:
            return AgentAction(action_type="dodge", description="No actions")

        # Find Multiattack action first, otherwise use first action
        best_action = None
        for action in creature.actions:
            if action.is_multiattack:
                best_action = action
                break

        if best_action is None:
            best_action = creature.actions[0]

        if not best_action.attacks:
            return AgentAction(action_type="dodge", description="No attacks")

        # Consider ranged attacks when out of melee range
        dist = distance_in_feet(creature.position, target.position)

        # Find best attack for current distance (prefer longer range if out of melee)
        best_attack = None
        for atk in best_action.attacks:
            if atk.range_feet >= dist:
                if best_attack is None or atk.range_feet > best_attack.range_feet:
                    best_attack = atk

        # If no attack can reach, use first attack and try to close distance
        if best_attack is None:
            best_attack = best_action.attacks[0]

        rng = best_attack.range_feet

        # Can attack from current position
        if dist <= rng:
            return AgentAction(
                action_type="attack", attack_name=best_action.name, target_id=target_id
            )

        # Try to move into range
        new_pos = move_toward(creature.position, target.position, creature.speed // 5)
        dist2 = distance_in_feet(new_pos, target.position)

        if dist2 <= rng:
            return AgentAction(
                action_type="move_and_attack",
                attack_name=best_action.name,
                target_id=target_id,
                move_to=new_pos,
            )

        # Just move closer
        return AgentAction(action_type="move", move_to=new_pos)
