"""Tests for Pydantic creature models."""

import pytest
from src.domain.creature import (
    Creature,
    Action,
    Attack,
    DamageRoll,
    AbilityScores,
    DeathSaves,
)


def test_ability_scores_defaults():
    """Test that ability scores default to 10."""
    scores = AbilityScores()
    assert scores.str == 10
    assert scores.dex == 10
    assert scores.con == 10
    assert scores.int_ == 10
    assert scores.wis == 10
    assert scores.cha == 10


def test_ability_score_modifiers():
    """Test ability score modifier calculation."""
    assert AbilityScores.modifier(10) == 0
    assert AbilityScores.modifier(16) == 3
    assert AbilityScores.modifier(8) == -1
    assert AbilityScores.modifier(20) == 5
    assert AbilityScores.modifier(3) == -4


def test_ability_scores_get_modifier():
    """Test get_modifier method."""
    scores = AbilityScores(str=16, dex=14, con=10, int_=8)
    assert scores.get_modifier("str") == 3
    assert scores.get_modifier("dex") == 2
    assert scores.get_modifier("con") == 0
    assert scores.get_modifier("int_") == -1


def test_death_saves_frozen():
    """Test that DeathSaves is immutable."""
    saves = DeathSaves(successes=1, failures=2)
    with pytest.raises(Exception):  # Pydantic raises ValidationError
        saves.successes = 3


def test_death_saves_defaults():
    """Test DeathSaves default values."""
    saves = DeathSaves()
    assert saves.successes == 0
    assert saves.failures == 0
    assert saves.stable is False


def test_damage_roll():
    """Test DamageRoll creation."""
    dmg = DamageRoll(dice="1d6+3", damage_type="slashing")
    assert dmg.dice == "1d6+3"
    assert dmg.damage_type == "slashing"


def test_attack_creation():
    """Test Attack creation with all fields."""
    dmg = DamageRoll(dice="1d8+3", damage_type="slashing")
    attack = Attack(
        name="Longsword",
        attack_bonus=5,
        damage=dmg,
        reach=5,
    )
    assert attack.name == "Longsword"
    assert attack.attack_bonus == 5
    assert attack.damage.dice == "1d8+3"
    assert attack.reach == 5
    assert attack.range is None


def test_attack_range_feet_melee():
    """Test that range_feet prefers reach for melee attacks."""
    dmg = DamageRoll(dice="1d8+3", damage_type="slashing")
    attack = Attack(name="Longsword", attack_bonus=5, damage=dmg, reach=5)
    assert attack.range_feet == 5


def test_attack_range_feet_ranged():
    """Test range_feet for ranged attacks."""
    dmg = DamageRoll(dice="1d6+2", damage_type="piercing")
    attack = Attack(name="Shortbow", attack_bonus=4, damage=dmg, range=80)
    assert attack.range_feet == 80


def test_attack_range_feet_both():
    """Test that reach takes precedence when both are set."""
    dmg = DamageRoll(dice="1d6+2", damage_type="piercing")
    attack = Attack(name="Spear", attack_bonus=4, damage=dmg, reach=5, range=20)
    assert attack.range_feet == 5


def test_action_single_attack():
    """Test Action with single attack."""
    dmg = DamageRoll(dice="1d6+2", damage_type="slashing")
    attack = Attack(name="Scimitar", attack_bonus=4, damage=dmg, reach=5)
    action = Action(name="Scimitar", attacks=[attack])
    assert action.is_multiattack is False


def test_action_multiattack():
    """Test Action with multiple attacks."""
    dmg = DamageRoll(dice="1d8+3", damage_type="slashing")
    attack1 = Attack(name="Longsword", attack_bonus=5, damage=dmg, reach=5)
    attack2 = Attack(name="Longsword", attack_bonus=5, damage=dmg, reach=5)
    action = Action(name="Multiattack", attacks=[attack1, attack2])
    assert action.is_multiattack is True
    assert len(action.attacks) == 2


def test_action_description():
    """Test Action description field."""
    action = Action(name="Dash", description="Double movement speed")
    assert action.description == "Double movement speed"
    assert action.attacks == []


def test_creature_full_creation():
    """Test creating a Creature with all fields."""
    scores = AbilityScores(str=16, dex=14, con=12, int_=10, wis=13, cha=8)
    dmg = DamageRoll(dice="1d8+3", damage_type="slashing")
    attack = Attack(name="Longsword", attack_bonus=5, damage=dmg, reach=5)
    action = Action(name="Longsword", attacks=[attack])

    creature = Creature(
        name="Fighter",
        ac=18,
        hp_max=44,
        current_hp=30,
        speed=30,
        initiative_bonus=1,
        team="party",
        position="B2",
        ability_scores=scores,
        actions=[action],
        damage_resistances=["fire"],
        creature_id="fighter_0",
    )

    assert creature.name == "Fighter"
    assert creature.ac == 18
    assert creature.hp_max == 44
    assert creature.current_hp == 30
    assert creature.speed == 30
    assert creature.initiative_bonus == 1
    assert creature.team == "party"
    assert creature.position == "B2"
    assert creature.ability_scores.str == 16
    assert len(creature.actions) == 1
    assert creature.damage_resistances == ["fire"]
    assert creature.creature_id == "fighter_0"


def test_creature_current_hp_defaults_to_max():
    """Test that current_hp defaults to hp_max when not provided."""
    creature = Creature(
        name="Goblin",
        ac=15,
        hp_max=7,
        team="enemies",
    )
    assert creature.current_hp == 7


def test_creature_current_hp_explicit():
    """Test that explicit current_hp is respected."""
    creature = Creature(
        name="Goblin",
        ac=15,
        hp_max=7,
        current_hp=3,
        team="enemies",
    )
    assert creature.current_hp == 3


def test_creature_model_copy():
    """Test that model_copy produces independent copies."""
    original = Creature(
        name="Fighter",
        ac=18,
        hp_max=44,
        current_hp=44,
        team="party",
    )

    # Create a copy with updated hp
    copy = original.model_copy(update={"current_hp": 30})

    assert copy.current_hp == 30
    assert original.current_hp == 44
    assert copy.name == original.name
    assert copy.ac == original.ac
    assert copy is not original


def test_creature_minimal():
    """Test creating a minimal Creature."""
    creature = Creature(
        name="Goblin",
        ac=15,
        hp_max=7,
        team="enemies",
    )
    assert creature.name == "Goblin"
    assert creature.ac == 15
    assert creature.hp_max == 7
    assert creature.current_hp == 7  # defaulted
    assert creature.speed == 30  # defaulted
    assert creature.position == "A1"  # defaulted
    assert creature.actions == []
    assert creature.death_saves.successes == 0


def test_creature_death_saves():
    """Test creature with death saves."""
    saves = DeathSaves(successes=2, failures=1)
    creature = Creature(
        name="Fighter",
        ac=18,
        hp_max=44,
        current_hp=0,
        team="party",
        death_saves=saves,
    )
    assert creature.death_saves.successes == 2
    assert creature.death_saves.failures == 1
    assert creature.current_hp == 0
