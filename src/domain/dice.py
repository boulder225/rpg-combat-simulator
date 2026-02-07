"""D20 dice rolling engine with advantage/disadvantage state machine.

This module provides a ternary state machine for advantage/disadvantage
handling that follows D&D 5e rules: any source of advantage + any source
of disadvantage = complete cancellation to normal (NOT net counting).
"""

from enum import Enum
import d20


class AdvantageState(Enum):
    """Ternary state for advantage/disadvantage in D&D 5e."""

    ADVANTAGE = "advantage"
    NORMAL = "normal"
    DISADVANTAGE = "disadvantage"


def resolve_advantage(
    advantage_sources: list[str], disadvantage_sources: list[str]
) -> AdvantageState:
    """
    Resolve advantage state from multiple sources using D&D 5e rules.

    D&D 5e Rule: If you have ANY advantage source AND ANY disadvantage source,
    they completely cancel to normal. This is NOT a counter subtraction system.

    Args:
        advantage_sources: List of source descriptions (e.g., ["pack tactics", "flanking"])
        disadvantage_sources: List of source descriptions (e.g., ["prone", "restrained"])

    Returns:
        AdvantageState: The resolved advantage state

    Examples:
        >>> resolve_advantage([], [])
        AdvantageState.NORMAL
        >>> resolve_advantage(["flanking"], [])
        AdvantageState.ADVANTAGE
        >>> resolve_advantage([], ["prone"])
        AdvantageState.DISADVANTAGE
        >>> resolve_advantage(["flanking"], ["prone"])
        AdvantageState.NORMAL  # Complete cancellation
        >>> resolve_advantage(["flanking", "pack tactics", "guiding bolt"], ["prone"])
        AdvantageState.NORMAL  # Still cancels completely
    """
    has_advantage = len(advantage_sources) > 0
    has_disadvantage = len(disadvantage_sources) > 0

    if has_advantage and has_disadvantage:
        # Complete cancellation - ternary state machine
        return AdvantageState.NORMAL
    elif has_advantage:
        return AdvantageState.ADVANTAGE
    elif has_disadvantage:
        return AdvantageState.DISADVANTAGE
    else:
        return AdvantageState.NORMAL


def roll_d20(advantage: AdvantageState = AdvantageState.NORMAL) -> tuple[int, str]:
    """
    Roll a d20 with advantage/disadvantage support.

    Args:
        advantage: The advantage state (ADVANTAGE, NORMAL, or DISADVANTAGE)

    Returns:
        tuple[int, str]: (total, string_representation)
            total: The final d20 roll value (1-20)
            string_representation: The detailed roll string from d20 library

    Examples:
        >>> roll_d20(AdvantageState.NORMAL)
        (15, '1d20 (15)')
        >>> roll_d20(AdvantageState.ADVANTAGE)
        (18, '2d20kh1 (18)')  # Keep highest
        >>> roll_d20(AdvantageState.DISADVANTAGE)
        (7, '2d20kl1 (7)')  # Keep lowest
    """
    if advantage == AdvantageState.ADVANTAGE:
        # Advantage: roll 2d20, keep highest
        result = d20.roll("2d20kh1")
    elif advantage == AdvantageState.DISADVANTAGE:
        # Disadvantage: roll 2d20, keep lowest
        result = d20.roll("2d20kl1")
    else:
        # Normal: single d20
        result = d20.roll("1d20")

    return (result.total, str(result))


def roll_damage(dice_expr: str) -> tuple[int, str]:
    """
    Roll damage dice using d20 library.

    Args:
        dice_expr: Dice expression string (e.g., "1d8+3", "2d6", "1d10-1")

    Returns:
        tuple[int, str]: (total, string_representation)
            total: The final damage amount
            string_representation: The detailed roll string from d20 library

    Examples:
        >>> roll_damage("1d8+3")
        (11, '1d8 (8) + 3 = 11')
        >>> roll_damage("2d6")
        (9, '2d6 (3, 6) = 9')
    """
    result = d20.roll(dice_expr)
    return (result.total, str(result))
