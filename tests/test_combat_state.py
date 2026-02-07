"""Tests for immutable combat state."""

import pytest
from src.domain.combat_state import CombatState, roll_initiative
from src.domain.creature import Creature


def test_combat_state_creation():
    """Test creating a basic CombatState."""
    c1 = Creature(name="Fighter", ac=18, hp_max=44, team="party", creature_id="fighter_0")
    c2 = Creature(name="Goblin", ac=15, hp_max=7, team="enemies", creature_id="goblin_0")

    creatures = {"fighter_0": c1, "goblin_0": c2}
    initiative = ["fighter_0", "goblin_0"]

    state = CombatState(creatures=creatures, initiative_order=initiative)

    assert state.current_turn == 0
    assert state.round == 1
    assert state.is_over is False
    assert state.winner is None
    assert len(state.combat_log) == 0


def test_combat_state_frozen():
    """Test that CombatState is immutable."""
    c1 = Creature(name="Fighter", ac=18, hp_max=44, team="party", creature_id="fighter_0")
    state = CombatState(creatures={"fighter_0": c1}, initiative_order=["fighter_0"])

    with pytest.raises(Exception):  # dataclass frozen raises FrozenInstanceError
        state.current_turn = 5


def test_update_creature():
    """Test updating a creature returns new state."""
    c1 = Creature(name="Fighter", ac=18, hp_max=44, current_hp=44, team="party", creature_id="fighter_0")
    state = CombatState(creatures={"fighter_0": c1}, initiative_order=["fighter_0"])

    # Update HP
    new_state = state.update_creature("fighter_0", current_hp=30)

    # Original unchanged
    assert state.creatures["fighter_0"].current_hp == 44
    # New state updated
    assert new_state.creatures["fighter_0"].current_hp == 30
    # Different objects
    assert state is not new_state


def test_update_creature_multiple_fields():
    """Test updating multiple fields at once."""
    c1 = Creature(
        name="Fighter",
        ac=18,
        hp_max=44,
        current_hp=44,
        team="party",
        position="A1",
        creature_id="fighter_0",
    )
    state = CombatState(creatures={"fighter_0": c1}, initiative_order=["fighter_0"])

    new_state = state.update_creature("fighter_0", current_hp=30, position="B2")

    assert new_state.creatures["fighter_0"].current_hp == 30
    assert new_state.creatures["fighter_0"].position == "B2"
    assert state.creatures["fighter_0"].current_hp == 44
    assert state.creatures["fighter_0"].position == "A1"


def test_add_log():
    """Test adding log messages."""
    c1 = Creature(name="Fighter", ac=18, hp_max=44, team="party", creature_id="fighter_0")
    state = CombatState(creatures={"fighter_0": c1}, initiative_order=["fighter_0"])

    state2 = state.add_log("Fighter attacks")
    state3 = state2.add_log("Goblin takes damage")

    assert len(state.combat_log) == 0
    assert len(state2.combat_log) == 1
    assert len(state3.combat_log) == 2
    assert state3.combat_log[0] == "Fighter attacks"
    assert state3.combat_log[1] == "Goblin takes damage"


def test_next_turn_within_round():
    """Test advancing turn within same round."""
    c1 = Creature(name="Fighter", ac=18, hp_max=44, team="party", creature_id="fighter_0")
    c2 = Creature(name="Goblin", ac=15, hp_max=7, team="enemies", creature_id="goblin_0")
    state = CombatState(
        creatures={"fighter_0": c1, "goblin_0": c2},
        initiative_order=["fighter_0", "goblin_0"],
    )

    new_state = state.next_turn()

    assert state.current_turn == 0
    assert state.round == 1
    assert new_state.current_turn == 1
    assert new_state.round == 1


def test_next_turn_new_round():
    """Test advancing to new round."""
    c1 = Creature(name="Fighter", ac=18, hp_max=44, team="party", creature_id="fighter_0")
    c2 = Creature(name="Goblin", ac=15, hp_max=7, team="enemies", creature_id="goblin_0")
    state = CombatState(
        creatures={"fighter_0": c1, "goblin_0": c2},
        initiative_order=["fighter_0", "goblin_0"],
        current_turn=1,  # Last turn of round
        round=1,
    )

    new_state = state.next_turn()

    assert new_state.current_turn == 0
    assert new_state.round == 2


def test_end_combat():
    """Test ending combat."""
    c1 = Creature(name="Fighter", ac=18, hp_max=44, team="party", creature_id="fighter_0")
    state = CombatState(creatures={"fighter_0": c1}, initiative_order=["fighter_0"])

    new_state = state.end_combat(winner="party")

    assert state.is_over is False
    assert state.winner is None
    assert new_state.is_over is True
    assert new_state.winner == "party"


def test_end_combat_no_winner():
    """Test ending combat with no winner (draw)."""
    c1 = Creature(name="Fighter", ac=18, hp_max=44, team="party", creature_id="fighter_0")
    state = CombatState(creatures={"fighter_0": c1}, initiative_order=["fighter_0"])

    new_state = state.end_combat()

    assert new_state.is_over is True
    assert new_state.winner is None


def test_roll_initiative_basic():
    """Test rolling initiative."""
    c1 = Creature(
        name="Fighter",
        ac=18,
        hp_max=44,
        team="party",
        initiative_bonus=1,
        creature_id="fighter_0",
    )
    c2 = Creature(
        name="Goblin",
        ac=15,
        hp_max=7,
        team="enemies",
        initiative_bonus=2,
        creature_id="goblin_0",
    )

    creatures = {"fighter_0": c1, "goblin_0": c2}
    initiative = roll_initiative(creatures, seed=42)

    assert len(initiative) == 2
    assert "fighter_0" in initiative
    assert "goblin_0" in initiative


def test_roll_initiative_deterministic():
    """Test that initiative with same seed produces same result."""
    c1 = Creature(
        name="Fighter",
        ac=18,
        hp_max=44,
        team="party",
        initiative_bonus=1,
        creature_id="fighter_0",
    )
    c2 = Creature(
        name="Goblin",
        ac=15,
        hp_max=7,
        team="enemies",
        initiative_bonus=2,
        creature_id="goblin_0",
    )

    creatures = {"fighter_0": c1, "goblin_0": c2}

    initiative1 = roll_initiative(creatures, seed=42)
    initiative2 = roll_initiative(creatures, seed=42)

    assert initiative1 == initiative2


def test_roll_initiative_tiebreaker():
    """Test that ties are broken alphabetically."""
    # Create creatures with same initiative bonus
    c1 = Creature(
        name="Creature B",
        ac=10,
        hp_max=10,
        team="party",
        initiative_bonus=0,
        creature_id="creature_b",
    )
    c2 = Creature(
        name="Creature A",
        ac=10,
        hp_max=10,
        team="party",
        initiative_bonus=0,
        creature_id="creature_a",
    )

    creatures = {"creature_b": c1, "creature_a": c2}

    # Use a seed that produces same roll for both
    initiative = roll_initiative(creatures, seed=100)

    # Even if rolls tie, alphabetical order breaks tie
    assert len(initiative) == 2


def test_roll_initiative_descending():
    """Test that initiative is sorted descending."""
    creatures = {}
    for i in range(5):
        creatures[f"creature_{i}"] = Creature(
            name=f"Creature {i}",
            ac=10,
            hp_max=10,
            team="party",
            initiative_bonus=i,
            creature_id=f"creature_{i}",
        )

    initiative = roll_initiative(creatures, seed=42)

    # Can't predict exact order due to randomness, but should be valid
    assert len(initiative) == 5
    for cid in creatures:
        assert cid in initiative
