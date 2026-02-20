"""Heuristic combat agent with survival-oriented tactics."""

from .base import AgentAction
from src.domain.distance import (
    manhattan_distance,
    move_toward,
    move_away_from,
    distance_in_feet,
)


def _is_ranged_attack(atk) -> bool:
    """True if attack is ranged (range in feet > typical melee reach)."""
    return atk.range is not None and atk.range_feet > 10


def _is_melee_attack(atk) -> bool:
    """True if attack is melee (has reach)."""
    return atk.reach is not None


class HeuristicAgent:
    """Heuristic agent that picks targets and actions with survival and equipment in mind.

    Decisions are based only on current shape (no ideal state):
    - Uses this turn's HP, position, and available actions from state—never
      assumes full HP or a different position.
    - Strategy is reconsidered every round from current state only (no memory
      of previous rounds).

    - Threat assessment: compares current side HP and numbers; when outmatched,
      prefers ranged, kiting, or moving away.
    - Equipment: uses bow/ranged when fragile or out of melee; uses sword/melee
      when in reach and healthy. Prefers staying at range when low HP.
    """

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
                return AgentAction(
                    action_type="death_save",
                    description="Death save",
                    strategy_summary="Death save.",
                )
            return AgentAction(
                action_type="dodge",
                description="Stable",
                strategy_summary="Stable at 0 HP.",
            )

        # Find living enemies and allies
        enemies = [
            (cid, c)
            for cid, c in state.creatures.items()
            if c.team != creature.team and c.current_hp > 0
        ]
        allies = [
            (cid, c)
            for cid, c in state.creatures.items()
            if c.team == creature.team and c.current_hp > 0
        ]

        if not enemies:
            return AgentAction(
                action_type="dodge",
                description="No enemies",
                strategy_summary="No enemies; dodge.",
            )

        # Threat assessment for survival
        enemy_hp_total = sum(c.current_hp for _, c in enemies)
        ally_hp_total = sum(c.current_hp for _, c in allies)
        outnumbered = len(enemies) > len(allies)
        low_hp = creature.current_hp <= creature.hp_max // 4  # 25% or less
        outmatched_hp = ally_hp_total < enemy_hp_total * 0.6  # we're significantly behind
        prefer_survival = low_hp or (outnumbered and outmatched_hp)

        # Find nearest enemy (primary target)
        target_id, target = sorted(
            enemies,
            key=lambda e: (
                manhattan_distance(creature.position, e[1].position),
                e[1].current_hp,
            ),
        )[0]

        # Determine attack profile (melee vs ranged) for this creature
        has_melee_attacks = any(
            _is_melee_attack(atk)
            for act in creature.actions
            for atk in (act.attacks or [])
        )

        # Pure casters / archers with no melee should strongly prefer staying at range
        if not has_melee_attacks:
            prefer_survival = True

        # AoE: if creature has an AoE action and 2+ enemies, use it with center at first enemy,
        # but avoid blatantly suicidal centers (don't include self in blast if we can help it).
        for act in creature.actions:
            if getattr(act, "is_aoe", False) and len(enemies) >= 2:
                center = target.position
                # Skip AoE if we are inside the blast radius
                if act.radius_squares is not None:
                    if manhattan_distance(creature.position, center) <= act.radius_squares:
                        continue
                return AgentAction(
                    action_type="aoe",
                    attack_name=act.name,
                    target_position=center,
                    strategy_summary=f"AoE {act.name} at {center} to hit multiple enemies.",
                )

        # Choose best action - prefer Multiattack over single attacks,
        # but ignore actions that have no attacks (e.g. pure AoE like Fireball).
        if not creature.actions:
            return AgentAction(
                action_type="dodge",
                description="No actions",
                strategy_summary="No actions available; dodge.",
            )

        attack_actions = [a for a in creature.actions if a.attacks]

        # If there are no attack-based actions but there is an AoE, fall back to AoE
        # (still respecting the "don't hit self" safety).
        if not attack_actions:
            for act in creature.actions:
                if getattr(act, "is_aoe", False):
                    center = target.position
                    if act.radius_squares is not None:
                        if manhattan_distance(creature.position, center) <= act.radius_squares:
                            continue
                    return AgentAction(
                        action_type="aoe",
                        attack_name=act.name,
                        target_position=center,
                        strategy_summary=f"AoE {act.name} at {center} (no other attacks available).",
                    )
            return AgentAction(
                action_type="dodge",
                description="No attacks",
                strategy_summary="No usable attacks; dodge.",
            )

        best_action = None
        for action in attack_actions:
            if action.is_multiattack:
                best_action = action
                break
        if best_action is None:
            best_action = attack_actions[0]

        dist = distance_in_feet(creature.position, target.position)
        speed_squares = creature.speed // 5

        # Build options: find a ranged-only action if any (for survival mode)
        def action_has_ranged_only(act) -> bool:
            if not act.attacks:
                return False
            return all(_is_ranged_attack(atk) for atk in act.attacks)

        ranged_only_action = None
        for action in creature.actions:
            if action_has_ranged_only(action):
                ranged_only_action = action
                break

        melee_attacks = [atk for atk in best_action.attacks if _is_melee_attack(atk)]
        ranged_attacks = [atk for atk in best_action.attacks if _is_ranged_attack(atk)]

        # Survival mode: prefer ranged and kiting; consider moving away when badly outmatched
        if prefer_survival and (ranged_attacks or ranged_only_action):
            # Prefer a ranged-only action (e.g. Shortbow) so we don't close into melee
            action_to_use = best_action
            best_attack = None
            if ranged_only_action:
                for atk in ranged_only_action.attacks:
                    if atk.range_feet >= dist and (
                        best_attack is None or atk.range_feet > best_attack.range_feet
                    ):
                        best_attack = atk
                        action_to_use = ranged_only_action
            if best_attack is None:
                for atk in ranged_attacks:
                    if atk.range_feet >= dist and (
                        best_attack is None or atk.range_feet > best_attack.range_feet
                    ):
                        best_attack = atk
            # If we are in (or very near) melee, try to kite FIRST
            if best_attack and dist <= 10 and speed_squares >= 1:
                new_pos = move_away_from(creature.position, target.position, speed_squares)
                if new_pos != creature.position:
                    return AgentAction(
                        action_type="move",
                        move_to=new_pos,
                        strategy_summary="Survival mode: move away from melee to kite next turn.",
                    )
            # Otherwise, use ranged attacks from distance
            if best_attack and dist <= best_attack.range_feet:
                return AgentAction(
                    action_type="attack",
                    attack_name=action_to_use.name,
                    target_id=target_id,
                    strategy_summary=f"Survival mode: ranged attack ({action_to_use.name}) on nearest, stay at range.",
                )
            # Can't get in ranged range this turn: move toward max range
            if best_attack:
                if dist > best_attack.range_feet:
                    new_pos = move_toward(
                        creature.position, target.position, speed_squares
                    )
                    dist2 = distance_in_feet(new_pos, target.position)
                    if dist2 <= best_attack.range_feet:
                        return AgentAction(
                            action_type="move_and_attack",
                            attack_name=action_to_use.name,
                            target_id=target_id,
                            move_to=new_pos,
                            strategy_summary="Survival mode: close to ranged range then attack.",
                        )
                    return AgentAction(
                        action_type="move",
                        move_to=new_pos,
                        strategy_summary="Survival mode: moving toward ranged range.",
                    )

        # Default: best attack for current distance (prefer ranged when out of melee)
        best_attack = None
        for atk in best_action.attacks:
            if atk.range_feet >= dist:
                if best_attack is None or atk.range_feet > best_attack.range_feet:
                    best_attack = atk
        if best_attack is None:
            best_attack = best_action.attacks[0]

        rng = best_attack.range_feet

        target_name = state.creatures[target_id].name if target_id else "?"
        if dist <= rng:
            return AgentAction(
                action_type="attack",
                attack_name=best_action.name,
                target_id=target_id,
                strategy_summary=f"Attack nearest ({target_name}) with {best_action.name}.",
            )

        # Move into range
        new_pos = move_toward(creature.position, target.position, speed_squares)
        dist2 = distance_in_feet(new_pos, target.position)

        if dist2 <= rng:
            return AgentAction(
                action_type="move_and_attack",
                attack_name=best_action.name,
                target_id=target_id,
                move_to=new_pos,
                strategy_summary=f"Move in and attack {target_name} ({best_action.name}).",
            )

        return AgentAction(
            action_type="move",
            move_to=new_pos,
            strategy_summary="Move closer to target.",
        )
