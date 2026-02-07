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

        # Choose first action
        if not creature.actions:
            return AgentAction(action_type="dodge", description="No actions")

        action = creature.actions[0]

        if not action.attacks:
            return AgentAction(action_type="dodge", description="No attacks")

        rng = action.attacks[0].range_feet
        dist = distance_in_feet(creature.position, target.position)

        # Can attack from current position
        if dist <= rng:
            return AgentAction(
                action_type="attack", attack_name=action.name, target_id=target_id
            )

        # Try to move into range
        new_pos = move_toward(creature.position, target.position, creature.speed // 5)
        dist2 = distance_in_feet(new_pos, target.position)

        if dist2 <= rng:
            return AgentAction(
                action_type="move_and_attack",
                attack_name=action.name,
                target_id=target_id,
                move_to=new_pos,
            )

        # Just move closer
        return AgentAction(action_type="move", move_to=new_pos)
