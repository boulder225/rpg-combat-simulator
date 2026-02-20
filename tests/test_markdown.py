"""Tests for markdown creature parser."""

from pathlib import Path
import pytest
from src.io.markdown import load_creature, load_creatures_from_dir


def test_load_creature_goblin():
    """Test loading the goblin creature file."""
    filepath = Path("data/creatures/goblin.md")
    creature_id, creature = load_creature(filepath)

    assert creature_id == "goblin"
    assert creature.name == "Goblin"
    assert creature.ac == 15
    assert creature.hp_max == 7
    assert creature.current_hp == 7  # defaults to max
    assert creature.speed == 30
    assert creature.initiative_bonus == 2
    assert creature.team == "enemies"
    assert creature.position == "E5"


def test_load_creature_goblin_ability_scores():
    """Test that goblin ability scores are parsed."""
    filepath = Path("data/creatures/goblin.md")
    _, creature = load_creature(filepath)

    assert creature.ability_scores.str == 8
    assert creature.ability_scores.dex == 14
    assert creature.ability_scores.con == 10
    assert creature.ability_scores.int_ == 10
    assert creature.ability_scores.wis == 8
    assert creature.ability_scores.cha == 8


def test_load_creature_goblin_actions():
    """Test that goblin actions are parsed."""
    filepath = Path("data/creatures/goblin.md")
    _, creature = load_creature(filepath)

    assert len(creature.actions) == 2

    # Scimitar
    scimitar = creature.actions[0]
    assert scimitar.name == "Scimitar"
    assert scimitar.description == "Melee weapon attack"
    assert len(scimitar.attacks) == 1
    assert scimitar.attacks[0].name == "Scimitar"
    assert scimitar.attacks[0].attack_bonus == 4
    assert scimitar.attacks[0].damage.dice == "1d6+2"
    assert scimitar.attacks[0].damage.damage_type == "slashing"
    assert scimitar.attacks[0].reach == 5
    assert scimitar.attacks[0].range is None

    # Shortbow
    shortbow = creature.actions[1]
    assert shortbow.name == "Shortbow"
    assert len(shortbow.attacks) == 1
    assert shortbow.attacks[0].attack_bonus == 4
    assert shortbow.attacks[0].damage.dice == "1d6+2"
    assert shortbow.attacks[0].damage.damage_type == "piercing"
    assert shortbow.attacks[0].range == 80


def test_load_creature_fighter():
    """Test loading the fighter creature file."""
    filepath = Path("data/creatures/fighter.md")
    creature_id, creature = load_creature(filepath)

    assert creature_id == "fighter"
    assert creature.name == "Fighter"
    assert creature.ac == 18
    assert creature.hp_max == 44
    assert creature.speed == 30
    assert creature.initiative_bonus == 1
    assert creature.team == "party"
    assert creature.position == "B2"


def test_load_creature_bio_from_body():
    """Test that body content after frontmatter is loaded as creature bio."""
    filepath = Path("data/creatures/fighter.md")
    _, creature = load_creature(filepath)
    assert creature.bio is not None
    assert "sturdy" in creature.bio
    assert "fighter" in creature.bio


def test_load_creature_fighter_multiattack():
    """Test that fighter Multiattack is parsed correctly."""
    filepath = Path("data/creatures/fighter.md")
    _, creature = load_creature(filepath)

    # Should have Multiattack and single Longsword actions
    assert len(creature.actions) == 2

    multiattack = creature.actions[0]
    assert multiattack.name == "Multiattack"
    assert len(multiattack.attacks) == 2
    assert multiattack.is_multiattack is True

    longsword = creature.actions[1]
    assert longsword.name == "Longsword"
    assert len(longsword.attacks) == 1
    assert longsword.is_multiattack is False


def test_load_creature_resistances():
    """Test loading damage resistances/immunities/vulnerabilities."""
    filepath = Path("data/creatures/goblin.md")
    _, creature = load_creature(filepath)

    assert creature.damage_resistances == []
    assert creature.damage_immunities == []
    assert creature.damage_vulnerabilities == []


def test_load_creature_sets_creature_id():
    """Test that creature_id is set from filename."""
    filepath = Path("data/creatures/goblin.md")
    creature_id, creature = load_creature(filepath)

    assert creature.creature_id == "goblin"


def test_load_creatures_from_dir():
    """Test loading all creatures from directory."""
    dirpath = Path("data/creatures")
    creatures = load_creatures_from_dir(dirpath)

    assert "goblin" in creatures
    assert "fighter" in creatures
    assert creatures["goblin"].name == "Goblin"
    assert creatures["fighter"].name == "Fighter"


def test_load_creature_file_not_found():
    """Test that loading non-existent file raises error."""
    filepath = Path("data/creatures/nonexistent.md")

    with pytest.raises(FileNotFoundError):
        load_creature(filepath)
