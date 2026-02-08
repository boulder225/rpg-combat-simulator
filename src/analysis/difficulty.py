"""D&D 5e difficulty rating calculator for encounter analysis.

Maps simulation results (win rate, TPK risk, duration) to D&D difficulty labels
(Easy/Medium/Hard/Deadly) based on D&D 5e XP guidelines and design expectations.
"""

from typing import Literal

DifficultyRating = Literal["Easy", "Medium", "Hard", "Deadly"]


def calculate_difficulty_rating(
    win_rate: float,
    ci_width: float,
    tpk_risk: float,
    avg_duration: float,
    party_size: int = 4,
) -> DifficultyRating:
    """Calculate D&D difficulty rating from simulation results.

    Uses a combined metric that considers both party win rate AND TPK risk,
    labeling by the worse indicator. Duration is used as a tiebreaker within
    the same difficulty category.

    Thresholds are based on D&D 5e XP guidelines:
    - Easy: win_rate > 80% AND TPK risk < 5%
    - Medium: win_rate 60-80% AND TPK risk < 15%
    - Hard: win_rate 40-60% OR TPK risk 15-30%
    - Deadly: win_rate < 40% OR TPK risk > 30%

    Args:
        win_rate: Party win rate as proportion [0, 1]
        ci_width: Confidence interval width (for future use in uncertainty handling)
        tpk_risk: Total party kill risk as proportion [0, 1]
        avg_duration: Average combat duration in rounds
        party_size: Number of party members (default 4, affects threshold adjustments)

    Returns:
        Difficulty rating: "Easy", "Medium", "Hard", or "Deadly"

    Raises:
        ValueError: If win_rate or tpk_risk not in [0, 1], or party_size < 1

    Examples:
        >>> calculate_difficulty_rating(0.85, 0.08, 0.03, 4)
        'Easy'

        >>> calculate_difficulty_rating(0.70, 0.08, 0.10, 6)
        'Medium'

        >>> calculate_difficulty_rating(0.50, 0.12, 0.20, 8)
        'Hard'

        >>> calculate_difficulty_rating(0.30, 0.12, 0.40, 8)
        'Deadly'
    """
    # Validate inputs
    if not 0 <= win_rate <= 1:
        raise ValueError(f"win_rate must be in [0, 1], got {win_rate}")
    if not 0 <= tpk_risk <= 1:
        raise ValueError(f"tpk_risk must be in [0, 1], got {tpk_risk}")
    if party_size < 1:
        raise ValueError(f"party_size must be at least 1, got {party_size}")

    # Adjust thresholds for party size (smaller parties need easier encounters)
    # Baseline is 4 players
    size_adjustment = (party_size - 4) * 0.025  # +/-2.5% per player difference

    # Adjusted thresholds
    easy_win_threshold = 0.80 + size_adjustment
    medium_win_threshold = 0.60 + size_adjustment
    hard_win_threshold = 0.40 + size_adjustment

    easy_tpk_threshold = 0.05
    medium_tpk_threshold = 0.15
    hard_tpk_threshold = 0.30

    # Duration factor: longer fights feel more challenging
    # Base thresholds assume 4-6 round combat
    # For very long fights (10+ rounds), shift difficulty up one level
    duration_penalty = 0.0
    if avg_duration >= 10:
        duration_penalty = 0.05  # Make it slightly harder to reach "Easy"

    # Determine difficulty by the WORSE of win rate and TPK risk
    # (Most conservative assessment for DM planning)

    # Check for Deadly (either metric indicates deadly)
    if win_rate < hard_win_threshold or tpk_risk > hard_tpk_threshold:
        return "Deadly"

    # Check for Hard (either metric indicates hard)
    if (
        hard_win_threshold <= win_rate < medium_win_threshold
        or medium_tpk_threshold <= tpk_risk <= hard_tpk_threshold
    ):
        return "Hard"

    # Check for Medium
    if (
        medium_win_threshold <= win_rate < easy_win_threshold - duration_penalty
        or easy_tpk_threshold <= tpk_risk < medium_tpk_threshold
    ):
        return "Medium"

    # Everything else is Easy
    # (High win rate AND low TPK risk)
    return "Easy"
