"""Monte Carlo simulation engine with progressive sampling.

Implements adaptive sampling that starts with minimum runs and progressively
increases sample size until target confidence interval precision is achieved.
"""

import random
from dataclasses import dataclass
from typing import Tuple, Optional, TYPE_CHECKING
from src.simulation.simulator import run_combat

if TYPE_CHECKING:
    from src.domain.terrain import Terrain
from src.analysis.statistics import calculate_win_rate_ci, progressive_sampling_stopping_criteria
from src.simulation.victory import get_winner


@dataclass
class SimulationResults:
    """Results from a Monte Carlo simulation run.

    Attributes:
        wins: Number of party victories
        total_runs: Total number of simulations executed
        win_rate: Point estimate of win rate (wins / total_runs)
        confidence_interval: Tuple of (lower_bound, upper_bound) at 95% confidence
        final_states: List of final CombatState objects from each run
        loggers: List of CombatLogger objects from each run
    """
    wins: int
    total_runs: int
    win_rate: float
    confidence_interval: Tuple[float, float]
    final_states: list
    loggers: list


class MonteCarloSimulator:
    """Monte Carlo simulator with progressive sampling and confidence-based stopping.

    Implements adaptive algorithm:
    1. Start with min_runs simulations
    2. Check confidence interval width every check_interval runs
    3. Stop when CI width <= 2 * target_precision OR max_runs reached

    This ensures statistical rigor while respecting DM time constraints.
    """

    def __init__(
        self,
        min_runs: int = 100,
        max_runs: int = 5000,
        target_precision: float = 0.05,
        check_interval: int = 100,
        confidence_level: float = 0.95
    ):
        """Initialize Monte Carlo simulator with progressive sampling parameters.

        Args:
            min_runs: Minimum number of simulations before first CI check
            max_runs: Maximum simulations (hard stop)
            target_precision: Target precision as proportion (0.05 = ±5%)
            check_interval: Run additional simulations between CI checks
            confidence_level: Confidence level for CI calculation (default 0.95)

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        if min_runs <= 0:
            raise ValueError(f"min_runs must be positive, got {min_runs}")
        if max_runs <= 0:
            raise ValueError(f"max_runs must be positive, got {max_runs}")
        if min_runs > max_runs:
            raise ValueError(f"min_runs ({min_runs}) cannot exceed max_runs ({max_runs})")
        if not 0 < target_precision < 1:
            raise ValueError(f"target_precision must be in (0, 1), got {target_precision}")
        if check_interval <= 0:
            raise ValueError(f"check_interval must be positive, got {check_interval}")
        if not 0 < confidence_level < 1:
            raise ValueError(f"confidence_level must be in (0, 1), got {confidence_level}")

        self.min_runs = min_runs
        self.max_runs = max_runs
        self.target_precision = target_precision
        self.check_interval = check_interval
        self.confidence_level = confidence_level

    def run_simulation(
        self,
        creatures: dict,
        agent,
        seed: Optional[int] = None,
        max_rounds: int = 100,
        verbose: bool = False,
        terrain: Optional["Terrain"] = None,
        on_progress=None,
        lang: str = "en",
    ) -> SimulationResults:
        """Run Monte Carlo simulation with progressive sampling.

        Creates fresh creature instances for each run to ensure immutable state.
        Runs simulations until confidence interval achieves target precision or
        max_runs is reached.

        Args:
            creatures: Dict of creature_id -> Creature (template instances)
            agent: Agent that chooses actions
            seed: Random seed for reproducibility (None for random)
            max_rounds: Maximum rounds per combat
            verbose: Whether to print logs (False recommended for batch)
            lang: Language for combat log ("en", "it")

        Returns:
            SimulationResults with wins, total_runs, win_rate, CI, and detailed results
        """
        if seed is not None:
            random.seed(seed)

        wins = 0
        total_runs = 0
        final_states = []
        loggers = []

        # Phase 1: Run minimum simulations
        for run_idx in range(self.min_runs):
            # Create fresh creature copies for immutable state
            fresh_creatures = self._create_fresh_creatures(creatures)

            # Run single combat
            final_state, logger = run_combat(
                fresh_creatures,
                agent,
                seed=None,  # Let random state flow through
                max_rounds=max_rounds,
                verbose=verbose,
                terrain=terrain,
                lang=lang,
            )

            # Track results
            final_states.append(final_state)
            loggers.append(logger)
            winner = get_winner(final_state)
            if winner == "party":
                wins += 1
            total_runs += 1

            # Progress callback after each run
            if on_progress is not None:
                try:
                    on_progress(total_runs, self.max_runs, wins)
                except Exception:
                    # Progress callbacks must not break the simulation loop
                    pass

        # Phase 2: Progressive sampling with CI checks
        while total_runs < self.max_runs:
            # Check stopping criteria
            should_stop = progressive_sampling_stopping_criteria(
                wins, total_runs, self.target_precision, self.confidence_level
            )

            if should_stop:
                break

            # Run check_interval more simulations
            runs_to_do = min(self.check_interval, self.max_runs - total_runs)

            for run_idx in range(runs_to_do):
                # Create fresh creature copies
                fresh_creatures = self._create_fresh_creatures(creatures)

                # Run single combat
                final_state, logger = run_combat(
                    fresh_creatures,
                    agent,
                    seed=None,
                    max_rounds=max_rounds,
                    verbose=verbose,
                    terrain=terrain,
                    lang=lang,
                )

                # Track results
                final_states.append(final_state)
                loggers.append(logger)
                winner = get_winner(final_state)
                if winner == "party":
                    wins += 1
                total_runs += 1

                if on_progress is not None:
                    try:
                        on_progress(total_runs, self.max_runs, wins)
                    except Exception:
                        pass

        # Calculate final statistics
        win_rate = wins / total_runs
        lower, upper, _ = calculate_win_rate_ci(
            wins, total_runs, self.confidence_level
        )

        return SimulationResults(
            wins=wins,
            total_runs=total_runs,
            win_rate=win_rate,
            confidence_interval=(lower, upper),
            final_states=final_states,
            loggers=loggers
        )

    def _create_fresh_creatures(self, template_creatures: dict) -> dict:
        """Create fresh creature instances from templates.

        Uses Pydantic's model_copy() to create deep copies with reset HP.
        This ensures each simulation starts with clean state.

        Args:
            template_creatures: Dict of creature_id -> Creature templates

        Returns:
            Dict of creature_id -> Creature with fresh copies
        """
        fresh = {}
        for cid, creature in template_creatures.items():
            # Use Pydantic's model_copy for deep copy
            fresh_copy = creature.model_copy(deep=True)
            # Reset HP to max (in case template was modified)
            fresh_copy.current_hp = fresh_copy.hp_max
            fresh[cid] = fresh_copy
        return fresh
