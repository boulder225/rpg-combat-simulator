"""Statistical utilities for Monte Carlo simulation analysis.

Provides functions for:
- Wilson score confidence intervals (accurate for small samples and extreme proportions)
- Progressive sampling stopping criteria based on confidence interval width
"""

from typing import Tuple
from scipy.stats import binomtest


def calculate_win_rate_ci(
    wins: int, total: int, confidence_level: float = 0.95
) -> Tuple[float, float, float]:
    """Calculate Wilson score confidence interval for win rate.

    Uses scipy.stats.binomtest with proportion_ci method for accurate
    confidence intervals, especially for small sample sizes and extreme
    proportions (near 0% or 100%).

    Args:
        wins: Number of wins (successes)
        total: Total number of trials
        confidence_level: Confidence level (default 0.95 for 95% CI)

    Returns:
        Tuple of (lower_bound, upper_bound, point_estimate)
        All values are proportions in [0, 1]

    Raises:
        ValueError: If total < 0, wins < 0, wins > total, or confidence_level not in (0, 1)

    Examples:
        >>> calculate_win_rate_ci(70, 100)
        (0.6024..., 0.7857..., 0.70)

        >>> calculate_win_rate_ci(0, 10)  # All losses
        (0.0, 0.3084..., 0.0)

        >>> calculate_win_rate_ci(10, 10)  # All wins
        (0.6915..., 1.0, 1.0)
    """
    # Validate inputs
    if total < 0:
        raise ValueError(f"total must be non-negative, got {total}")
    if wins < 0:
        raise ValueError(f"wins must be non-negative, got {wins}")
    if wins > total:
        raise ValueError(f"wins ({wins}) cannot exceed total ({total})")
    if not 0 < confidence_level < 1:
        raise ValueError(f"confidence_level must be in (0, 1), got {confidence_level}")

    # Handle edge case: no trials yet
    if total == 0:
        return (0.0, 1.0, 0.5)  # Maximum uncertainty

    # Calculate point estimate
    point_estimate = wins / total

    # Use binomial test to get Wilson score confidence interval
    # binomtest.proportion_ci uses the Wilson score method by default
    result = binomtest(wins, total, alternative="two-sided")
    ci = result.proportion_ci(confidence_level=confidence_level, method="wilson")

    return (ci.low, ci.high, point_estimate)


def progressive_sampling_stopping_criteria(
    wins: int, total: int, target_precision: float = 0.05, confidence_level: float = 0.95
) -> bool:
    """Check if progressive sampling can stop based on confidence interval width.

    Stopping criteria: CI width ≤ 2 × target_precision
    (e.g., for ±5% precision, CI width should be ≤ 0.10)

    Args:
        wins: Number of wins so far
        total: Total trials run so far
        target_precision: Target precision as proportion (default 0.05 for ±5%)
        confidence_level: Confidence level for CI (default 0.95)

    Returns:
        True if sampling can stop (target precision achieved)
        False if more samples needed

    Examples:
        >>> progressive_sampling_stopping_criteria(500, 1000, target_precision=0.05)
        True  # CI width ~0.06, close to target

        >>> progressive_sampling_stopping_criteria(5, 10, target_precision=0.05)
        False  # CI width ~0.58, far from target
    """
    if total == 0:
        return False  # Need at least some samples

    lower, upper, _ = calculate_win_rate_ci(wins, total, confidence_level)
    ci_width = upper - lower

    # CI width should be ≤ 2 × target_precision
    # (e.g., ±5% means width of 0.10)
    max_width = 2 * target_precision

    return ci_width <= max_width
