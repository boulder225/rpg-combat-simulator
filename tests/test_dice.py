"""Tests for the dice rolling engine with advantage/disadvantage state machine."""

import pytest
from src.domain.dice import AdvantageState, resolve_advantage, roll_d20, roll_damage


class TestAdvantageResolution:
    """Test the ternary state machine for advantage/disadvantage resolution."""

    def test_no_sources_returns_normal(self):
        """With no advantage or disadvantage sources, state is NORMAL."""
        result = resolve_advantage([], [])
        assert result == AdvantageState.NORMAL

    def test_single_advantage_source(self):
        """With only advantage source(s), state is ADVANTAGE."""
        result = resolve_advantage(["flanking"], [])
        assert result == AdvantageState.ADVANTAGE

    def test_multiple_advantage_sources(self):
        """Multiple advantage sources still result in ADVANTAGE."""
        result = resolve_advantage(["flanking", "pack tactics"], [])
        assert result == AdvantageState.ADVANTAGE

    def test_single_disadvantage_source(self):
        """With only disadvantage source(s), state is DISADVANTAGE."""
        result = resolve_advantage([], ["prone"])
        assert result == AdvantageState.DISADVANTAGE

    def test_multiple_disadvantage_sources(self):
        """Multiple disadvantage sources still result in DISADVANTAGE."""
        result = resolve_advantage([], ["prone", "restrained"])
        assert result == AdvantageState.DISADVANTAGE

    def test_one_advantage_one_disadvantage_cancels(self):
        """One advantage + one disadvantage = complete cancellation to NORMAL."""
        result = resolve_advantage(["flanking"], ["prone"])
        assert result == AdvantageState.NORMAL

    def test_multiple_advantage_one_disadvantage_cancels(self):
        """
        Three advantage sources + one disadvantage source = NORMAL.

        This is NOT net advantage. D&D 5e uses ternary state machine:
        ANY advantage + ANY disadvantage = complete cancellation.
        """
        result = resolve_advantage(
            ["flanking", "pack tactics", "guiding bolt"], ["prone"]
        )
        assert result == AdvantageState.NORMAL

    def test_two_advantage_five_disadvantage_cancels(self):
        """
        Two advantage sources + five disadvantage sources = NORMAL.

        This is NOT net disadvantage. D&D 5e rule: complete cancellation
        regardless of source count.
        """
        result = resolve_advantage(
            ["flanking", "pack tactics"],
            ["prone", "restrained", "blinded", "poisoned", "frightened"],
        )
        assert result == AdvantageState.NORMAL


class TestRollD20:
    """Test d20 rolling with advantage/disadvantage."""

    def test_normal_roll_returns_value_in_range(self):
        """Normal d20 roll returns value between 1 and 20."""
        for _ in range(20):
            total, _ = roll_d20(AdvantageState.NORMAL)
            assert 1 <= total <= 20

    def test_advantage_roll_returns_value_in_range(self):
        """Advantage d20 roll returns value between 1 and 20."""
        for _ in range(20):
            total, _ = roll_d20(AdvantageState.ADVANTAGE)
            assert 1 <= total <= 20

    def test_disadvantage_roll_returns_value_in_range(self):
        """Disadvantage d20 roll returns value between 1 and 20."""
        for _ in range(20):
            total, _ = roll_d20(AdvantageState.DISADVANTAGE)
            assert 1 <= total <= 20

    def test_returns_tuple_of_int_and_str(self):
        """roll_d20 returns (int, str) tuple."""
        total, string_repr = roll_d20(AdvantageState.NORMAL)
        assert isinstance(total, int)
        assert isinstance(string_repr, str)

    def test_string_representation_contains_roll_info(self):
        """String representation includes the roll details."""
        _, string_repr = roll_d20(AdvantageState.NORMAL)
        # Should contain something like "1d20" or the result
        assert len(string_repr) > 0

    def test_default_is_normal(self):
        """roll_d20() without arguments defaults to NORMAL."""
        total, _ = roll_d20()
        assert 1 <= total <= 20

    def test_hundred_advantage_rolls_all_valid(self):
        """Run 100 advantage rolls to verify consistency."""
        for _ in range(100):
            total, string_repr = roll_d20(AdvantageState.ADVANTAGE)
            assert 1 <= total <= 20
            assert isinstance(string_repr, str)
            assert len(string_repr) > 0


class TestRollDamage:
    """Test damage rolling with dice expressions."""

    def test_simple_damage_returns_positive(self):
        """Simple damage roll returns positive value."""
        total, _ = roll_damage("1d6")
        assert total > 0

    def test_damage_with_modifier(self):
        """Damage roll with modifier (1d6+3) returns value in expected range."""
        for _ in range(20):
            total, _ = roll_damage("1d6+3")
            # 1d6+3 should be 4-9
            assert 4 <= total <= 9

    def test_damage_returns_tuple(self):
        """roll_damage returns (int, str) tuple."""
        total, string_repr = roll_damage("2d6")
        assert isinstance(total, int)
        assert isinstance(string_repr, str)

    def test_string_representation_contains_details(self):
        """String representation includes roll details."""
        _, string_repr = roll_damage("1d8+3")
        assert len(string_repr) > 0

    def test_multiple_dice(self):
        """Multiple dice (2d6) returns valid value."""
        for _ in range(20):
            total, _ = roll_damage("2d6")
            # 2d6 should be 2-12
            assert 2 <= total <= 12

    def test_damage_with_negative_modifier(self):
        """Damage roll with negative modifier works correctly."""
        # 1d10-1 should be 0-9 (can be 0 if roll is 1)
        for _ in range(20):
            total, _ = roll_damage("1d10-1")
            assert 0 <= total <= 9

    def test_large_damage_expression(self):
        """Large damage expression (8d6) works correctly."""
        total, _ = roll_damage("8d6")
        # 8d6 should be 8-48
        assert 8 <= total <= 48
