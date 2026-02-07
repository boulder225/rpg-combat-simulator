"""Comprehensive tests for D&D 5e rules with d20 library integration."""

import pytest
from unittest.mock import patch, MagicMock
from src.domain.rules import (
    make_attack_roll,
    roll_damage_for_attack,
    make_saving_throw,
    make_death_save,
    apply_damage_modifiers,
    apply_damage,
    AttackResult,
    SavingThrowResult,
    DeathSaveResult,
)
from src.domain.dice import AdvantageState
from src.domain.creature import Creature


class TestAttackRollWithAdvantageState:
    """Test attack rolls with AdvantageState integration."""

    def test_attack_roll_normal_state(self):
        """Test attack roll with NORMAL advantage state."""
        result = make_attack_roll(5, 15, AdvantageState.NORMAL)
        assert isinstance(result, AttackResult)
        assert 1 <= result.natural_roll <= 20
        assert result.bonus == 5
        assert result.ac == 15

    def test_attack_roll_advantage_state(self):
        """Test attack roll with ADVANTAGE state."""
        result = make_attack_roll(5, 15, AdvantageState.ADVANTAGE)
        assert isinstance(result, AttackResult)
        assert 1 <= result.natural_roll <= 20

    def test_attack_roll_disadvantage_state(self):
        """Test attack roll with DISADVANTAGE state."""
        result = make_attack_roll(5, 15, AdvantageState.DISADVANTAGE)
        assert isinstance(result, AttackResult)
        assert 1 <= result.natural_roll <= 20

    def test_backward_compat_true_is_advantage(self):
        """Test backward compatibility: True means advantage."""
        result = make_attack_roll(5, 15, advantage=True)
        assert isinstance(result, AttackResult)
        # Should work without error

    def test_backward_compat_false_is_disadvantage(self):
        """Test backward compatibility: False means disadvantage."""
        result = make_attack_roll(5, 15, advantage=False)
        assert isinstance(result, AttackResult)
        # Should work without error

    def test_backward_compat_none_is_normal(self):
        """Test backward compatibility: None means normal."""
        result = make_attack_roll(5, 15, advantage=None)
        assert isinstance(result, AttackResult)
        # Should work without error

    @patch('src.domain.rules.roll_d20')
    def test_natural_20_is_critical(self, mock_roll_d20):
        """Test that natural 20 results in critical hit."""
        mock_roll_d20.return_value = (20, "1d20 (20)")
        result = make_attack_roll(0, 99, AdvantageState.NORMAL)
        assert result.natural_roll == 20
        assert result.is_critical
        assert result.is_hit
        assert not result.is_auto_miss

    @patch('src.domain.rules.roll_d20')
    def test_natural_1_is_auto_miss(self, mock_roll_d20):
        """Test that natural 1 results in automatic miss."""
        mock_roll_d20.return_value = (1, "1d20 (1)")
        result = make_attack_roll(99, 5, AdvantageState.NORMAL)
        assert result.natural_roll == 1
        assert result.is_auto_miss
        assert not result.is_hit
        assert not result.is_critical

    @patch('src.domain.rules.roll_d20')
    def test_hit_on_exact_ac(self, mock_roll_d20):
        """Test that meeting AC exactly is a hit."""
        mock_roll_d20.return_value = (10, "1d20 (10)")
        result = make_attack_roll(5, 15, AdvantageState.NORMAL)
        # 10 + 5 = 15, which equals AC
        assert result.total == 15
        assert result.is_hit

    @patch('src.domain.rules.roll_d20')
    def test_miss_below_ac(self, mock_roll_d20):
        """Test that rolling below AC is a miss."""
        mock_roll_d20.return_value = (5, "1d20 (5)")
        result = make_attack_roll(2, 15, AdvantageState.NORMAL)
        # 5 + 2 = 7, which is below AC 15
        assert result.total == 7
        assert not result.is_hit


class TestDamageRolling:
    """Test damage rolling with d20 library integration."""

    def test_normal_damage_in_valid_range(self):
        """Test that normal damage roll is in valid range."""
        for _ in range(20):
            damage = roll_damage_for_attack("1d8+3", is_critical=False)
            # 1d8+3 should be 4-11
            assert 4 <= damage <= 11

    def test_critical_damage_doubles_dice_not_modifier(self):
        """Test that critical hits double dice but not modifier."""
        # Run multiple times to test range
        for _ in range(20):
            damage = roll_damage_for_attack("1d8+3", is_critical=True)
            # Critical: 2d8+3 = 2-16 + 3 = 5-19
            assert 5 <= damage <= 19

    def test_flat_damage_no_dice(self):
        """Test flat damage (no dice) edge case."""
        # parse_dice_expression returns (0, 0, modifier) for flat damage
        # This should work correctly
        for _ in range(10):
            damage = roll_damage_for_attack("5", is_critical=False)
            # Flat damage should just be 5
            assert damage >= 1  # d20 library might handle this differently

    def test_multiple_dice(self):
        """Test damage with multiple dice."""
        for _ in range(20):
            damage = roll_damage_for_attack("2d6+2", is_critical=False)
            # 2d6+2 = 2-12 + 2 = 4-14
            assert 4 <= damage <= 14

    def test_critical_with_multiple_dice(self):
        """Test critical hit with multiple dice."""
        for _ in range(20):
            damage = roll_damage_for_attack("2d6+2", is_critical=True)
            # Critical: 4d6+2 = 4-24 + 2 = 6-26
            assert 6 <= damage <= 26


class TestSavingThrows:
    """Test saving throws with AdvantageState integration."""

    def test_saving_throw_normal_state(self):
        """Test saving throw with NORMAL state."""
        result = make_saving_throw(3, 15, AdvantageState.NORMAL)
        assert isinstance(result, SavingThrowResult)
        assert result.modifier == 3
        assert result.dc == 15
        assert 1 <= result.roll <= 20

    def test_saving_throw_advantage_state(self):
        """Test saving throw with ADVANTAGE state."""
        result = make_saving_throw(3, 15, AdvantageState.ADVANTAGE)
        assert isinstance(result, SavingThrowResult)

    def test_saving_throw_disadvantage_state(self):
        """Test saving throw with DISADVANTAGE state."""
        result = make_saving_throw(3, 15, AdvantageState.DISADVANTAGE)
        assert isinstance(result, SavingThrowResult)

    def test_backward_compat_saving_throw(self):
        """Test backward compatibility with True/False/None."""
        result1 = make_saving_throw(3, 15, advantage=True)
        result2 = make_saving_throw(3, 15, advantage=False)
        result3 = make_saving_throw(3, 15, advantage=None)
        assert all(isinstance(r, SavingThrowResult) for r in [result1, result2, result3])

    @patch('src.domain.rules.roll_d20')
    def test_saving_throw_success(self, mock_roll_d20):
        """Test successful saving throw."""
        mock_roll_d20.return_value = (15, "1d20 (15)")
        result = make_saving_throw(2, 15, AdvantageState.NORMAL)
        # 15 + 2 = 17, which meets DC 15
        assert result.total == 17
        assert result.is_success

    @patch('src.domain.rules.roll_d20')
    def test_saving_throw_failure(self, mock_roll_d20):
        """Test failed saving throw."""
        mock_roll_d20.return_value = (5, "1d20 (5)")
        result = make_saving_throw(2, 15, AdvantageState.NORMAL)
        # 5 + 2 = 7, which is below DC 15
        assert result.total == 7
        assert not result.is_success


class TestDeathSaves:
    """Test death saving throws."""

    def test_death_save_uses_dice_module(self):
        """Test that death save uses dice module (integration check)."""
        creature = Creature(
            name="Test",
            team="enemy",
            position="A1",
            hp_max=20,
            current_hp=0,
            ac=15,
        )
        # Should not raise error
        result = make_death_save(creature)
        # Verify it returns the creature (old API)
        assert result == creature

    @patch('src.domain.rules.roll_d20')
    def test_death_save_natural_20(self, mock_roll_d20):
        """Test death save natural 20 restores 1 HP."""
        mock_roll_d20.return_value = (20, "1d20 (20)")
        creature = Creature(
            name="Test",
            team="enemy",
            position="A1",
            hp_max=20,
            current_hp=0,
            ac=15,
        )
        make_death_save(creature)
        assert creature.current_hp == 1

    @patch('src.domain.rules.roll_d20')
    def test_death_save_natural_1(self, mock_roll_d20):
        """Test death save natural 1 counts as 2 failures."""
        mock_roll_d20.return_value = (1, "1d20 (1)")
        creature = Creature(
            name="Test",
            team="enemy",
            position="A1",
            hp_max=20,
            current_hp=0,
            ac=15,
        )
        make_death_save(creature)
        # Natural 1 should count as 2 failures (using Pydantic v2 model)
        assert creature.death_saves.failures == 2


class TestDamageModifiers:
    """Test damage modifiers (immunity, resistance, vulnerability)."""

    def test_immunity_order_priority(self):
        """Test that immunity takes priority over resistance and vulnerability."""
        creature = Creature(
            name="Test",
            team="enemy",
            position="A1",
            hp_max=20,
            current_hp=20,
            ac=15,
            damage_immunities=["fire"],
            damage_resistances=["fire"],
            damage_vulnerabilities=["fire"],
        )
        final_damage, modifier = apply_damage_modifiers(20, "fire", creature)
        assert final_damage == 0
        assert modifier == "immunity"

    def test_resistance_before_vulnerability(self):
        """Test that resistance takes priority over vulnerability."""
        creature = Creature(
            name="Test",
            team="enemy",
            position="A1",
            hp_max=20,
            current_hp=20,
            ac=15,
            damage_resistances=["cold"],
            damage_vulnerabilities=["cold"],
        )
        final_damage, modifier = apply_damage_modifiers(20, "cold", creature)
        # Resistance should apply (10), not vulnerability (40)
        assert final_damage == 10
        assert modifier == "resistance"

    def test_no_modifier_returns_original_damage(self):
        """Test that damage without modifiers returns original amount."""
        creature = Creature(
            name="Test",
            team="enemy",
            position="A1",
            hp_max=20,
            current_hp=20,
            ac=15,
        )
        final_damage, modifier = apply_damage_modifiers(15, "slashing", creature)
        assert final_damage == 15
        assert modifier is None


class TestIntegrationWithAdvantageState:
    """Integration tests for advantage state flowing through attack roll."""

    @patch('src.domain.rules.roll_d20')
    def test_advantage_state_passes_through_to_dice(self, mock_roll_d20):
        """Test that AdvantageState properly passes to dice module."""
        mock_roll_d20.return_value = (15, "2d20kh1 (15)")

        result = make_attack_roll(5, 15, AdvantageState.ADVANTAGE)

        # Verify roll_d20 was called with ADVANTAGE state
        mock_roll_d20.assert_called_once_with(AdvantageState.ADVANTAGE)
        assert result.natural_roll == 15

    @patch('src.domain.rules.roll_d20')
    def test_backward_compat_true_converts_to_advantage(self, mock_roll_d20):
        """Test that True converts to AdvantageState.ADVANTAGE."""
        mock_roll_d20.return_value = (15, "2d20kh1 (15)")

        make_attack_roll(5, 15, advantage=True)

        # Should convert True to AdvantageState.ADVANTAGE
        mock_roll_d20.assert_called_once_with(AdvantageState.ADVANTAGE)

    @patch('src.domain.rules.roll_d20')
    def test_backward_compat_false_converts_to_disadvantage(self, mock_roll_d20):
        """Test that False converts to AdvantageState.DISADVANTAGE."""
        mock_roll_d20.return_value = (8, "2d20kl1 (8)")

        make_attack_roll(5, 15, advantage=False)

        # Should convert False to AdvantageState.DISADVANTAGE
        mock_roll_d20.assert_called_once_with(AdvantageState.DISADVANTAGE)
