"""Basic tests for D&D 5e rules implementation."""
import random
from src.domain.rules import (
    make_attack_roll,
    roll_damage_for_attack,
    apply_damage,
    parse_dice_expression,
    apply_damage_modifiers,
)
from src.domain.combat_state import Creature


def test_attack_roll_hit():
    """Test that attack roll with high enough total hits."""
    random.seed(42)
    # With seed 42, first roll should be deterministic
    result = make_attack_roll(bonus=5, ac=15, advantage=None)
    assert result.total == result.natural_roll + 5
    assert result.ac == 15
    # Check hit logic
    if result.total >= 15:
        assert result.is_hit


def test_natural_20_always_hits():
    """Test that natural 20 always hits regardless of AC."""
    # Brute force: keep rolling until we get a nat 20
    for i in range(1000):
        random.seed(i)
        result = make_attack_roll(bonus=0, ac=99, advantage=None)
        if result.natural_roll == 20:
            assert result.is_critical
            assert result.is_hit
            assert "Critical" in result.description or "Natural 20" in result.description
            break
    else:
        # If we didn't find a nat 20 in 1000 tries, something is wrong
        assert False, "Failed to roll natural 20 in 1000 attempts"


def test_natural_1_always_misses():
    """Test that natural 1 always misses regardless of bonus."""
    # Brute force: keep rolling until we get a nat 1
    for i in range(1000):
        random.seed(i)
        result = make_attack_roll(bonus=99, ac=5, advantage=None)
        if result.natural_roll == 1:
            assert result.is_auto_miss
            assert not result.is_hit
            assert "Natural 1" in result.description or "miss" in result.description.lower()
            break
    else:
        assert False, "Failed to roll natural 1 in 1000 attempts"


def test_parse_dice_expression():
    """Test dice expression parsing."""
    assert parse_dice_expression("1d8+3") == (1, 8, 3)
    assert parse_dice_expression("2d6") == (2, 6, 0)
    assert parse_dice_expression("1d10-1") == (1, 10, -1)
    assert parse_dice_expression("3d6+5") == (3, 6, 5)


def test_damage_calculation():
    """Test basic damage rolling from dice string."""
    random.seed(100)
    # Roll 1d8+3 multiple times, verify it's in valid range
    for _ in range(10):
        damage = roll_damage_for_attack("1d8+3", is_critical=False)
        # 1d8+3 should be between 4 and 11
        assert 4 <= damage <= 11


def test_critical_damage_doubles_dice():
    """Test that critical hits double dice, not modifier."""
    random.seed(200)
    # For 1d8+3:
    # Normal: 1d8+3 = 1-8 + 3 = 4-11
    # Critical: 2d8+3 = 2-16 + 3 = 5-19
    damage = roll_damage_for_attack("1d8+3", is_critical=True)
    # Should be in critical range
    assert 5 <= damage <= 19


def test_resistance_halves_damage():
    """Test that resistance halves damage (rounded down)."""
    creature = Creature(
        id="test",
        name="Test",
        team="enemy",
        position="A1",
        max_hp=20,
        current_hp=20,
        ac=15,
        speed=30,
    )
    creature.damage_resistances = ["fire"]

    # 10 fire damage with resistance should be 5
    final_damage, modifier = apply_damage_modifiers(10, "fire", creature)
    assert final_damage == 5
    assert modifier == "resistance"

    # 11 fire damage with resistance should be 5 (floor division)
    final_damage, modifier = apply_damage_modifiers(11, "fire", creature)
    assert final_damage == 5
    assert modifier == "resistance"


def test_immunity_zeroes_damage():
    """Test that immunity reduces damage to 0."""
    creature = Creature(
        id="test",
        name="Test",
        team="enemy",
        position="A1",
        max_hp=20,
        current_hp=20,
        ac=15,
        speed=30,
    )
    creature.damage_immunities = ["poison"]

    final_damage, modifier = apply_damage_modifiers(100, "poison", creature)
    assert final_damage == 0
    assert modifier == "immunity"


def test_vulnerability_doubles_damage():
    """Test that vulnerability doubles damage."""
    creature = Creature(
        id="test",
        name="Test",
        team="enemy",
        position="A1",
        max_hp=20,
        current_hp=20,
        ac=15,
        speed=30,
    )
    creature.damage_vulnerabilities = ["cold"]

    final_damage, modifier = apply_damage_modifiers(10, "cold", creature)
    assert final_damage == 20
    assert modifier == "vulnerability"


def test_apply_damage_reduces_hp():
    """Test that applying damage reduces HP correctly."""
    creature = Creature(
        id="test",
        name="Test",
        team="enemy",
        position="A1",
        max_hp=20,
        current_hp=20,
        ac=15,
        speed=30,
    )

    apply_damage(creature, 5, "slashing")
    assert creature.current_hp == 15

    apply_damage(creature, 20, "slashing")
    # HP should be clamped at 0
    assert creature.current_hp == 0


def test_hp_clamped_at_zero():
    """Test that HP doesn't go below zero."""
    creature = Creature(
        id="test",
        name="Test",
        team="enemy",
        position="A1",
        max_hp=10,
        current_hp=5,
        ac=15,
        speed=30,
    )

    apply_damage(creature, 100, "slashing")
    assert creature.current_hp == 0
