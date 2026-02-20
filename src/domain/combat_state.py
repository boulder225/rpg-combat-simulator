"""Immutable combat state with copy-on-write updates."""

import random
from dataclasses import dataclass, field, replace
from src.domain.creature import Creature


@dataclass(frozen=True)
class CombatState:
    """Immutable combat state snapshot.

    All updates return new CombatState instances (copy-on-write).
    """

    creatures: dict[str, Creature]
    initiative_order: list[str]
    current_turn: int = 0
    round: int = 1
    combat_log: list[str] = field(default_factory=list)
    is_over: bool = False
    winner: str | None = None
    reaction_used: frozenset[str] = field(default_factory=frozenset)

    def update_creature(self, creature_id: str, **updates) -> "CombatState":
        """Update a creature and return new CombatState.

        Args:
            creature_id: ID of creature to update
            **updates: Fields to update via model_copy

        Returns:
            New CombatState with updated creature
        """
        creature = self.creatures[creature_id]
        updated_creature = creature.model_copy(update=updates)
        new_creatures = dict(self.creatures)
        new_creatures[creature_id] = updated_creature
        return replace(self, creatures=new_creatures)

    def add_log(self, message: str) -> "CombatState":
        """Add a log message and return new CombatState.

        Args:
            message: Log message to add

        Returns:
            New CombatState with appended log
        """
        new_log = self.combat_log + [message]
        return replace(self, combat_log=new_log)

    def set_reaction_used(self, creature_id: str) -> "CombatState":
        """Mark a creature as having used its reaction this round."""
        new_set = frozenset(self.reaction_used) | {creature_id}
        return replace(self, reaction_used=new_set)

    def next_turn(self) -> "CombatState":
        """Advance to next turn and return new CombatState.

        Returns:
            New CombatState with incremented turn/round
        """
        next_turn_idx = self.current_turn + 1
        if next_turn_idx >= len(self.initiative_order):
            # New round: reset reactions
            return replace(self, current_turn=0, round=self.round + 1, reaction_used=frozenset())
        else:
            return replace(self, current_turn=next_turn_idx)

    def end_combat(self, winner: str | None = None) -> "CombatState":
        """Mark combat as ended and return new CombatState.

        Args:
            winner: Team that won (e.g., "party", "enemies") or None for draw

        Returns:
            New CombatState with is_over=True
        """
        return replace(self, is_over=True, winner=winner)


def roll_initiative(creatures: dict[str, Creature], seed: int | None = None) -> list[str]:
    """Roll initiative for all creatures and return ordered list of IDs.

    Args:
        creatures: Dict of creature_id -> Creature
        seed: Optional random seed for deterministic results

    Returns:
        List of creature IDs sorted by initiative (descending), alphabetically on ties
    """
    if seed is not None:
        random.seed(seed)

    rolls = {}
    for creature_id, creature in creatures.items():
        roll = random.randint(1, 20) + creature.initiative_bonus
        rolls[creature_id] = roll

    # Sort by roll descending, then by creature_id alphabetically
    sorted_ids = sorted(
        rolls.keys(),
        key=lambda cid: (-rolls[cid], cid)
    )

    return sorted_ids
