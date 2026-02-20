"""Batch simulation runner with progress tracking and comprehensive result collection.

Manages execution of Monte Carlo simulations with:
- Progress tracking during execution
- Damage breakdown attribution by creature and ability type
- Combat duration analysis (wins vs losses)
- Sequential execution for simplicity
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from src.domain.terrain import Terrain


@dataclass
class DamageBreakdown:
    """Damage attribution by source creature and ability type.

    Tracks all damage dealt during simulations, broken down by:
    - Which creature dealt it
    - Which ability/attack was used
    - Total and average damage per source
    """
    by_creature: Dict[str, int] = field(default_factory=dict)
    by_ability: Dict[str, int] = field(default_factory=dict)
    total_damage: int = 0


@dataclass
class BatchResults:
    """Comprehensive results from batch simulation execution.

    Attributes:
        wins: Number of party victories
        total_runs: Total simulations executed
        win_rate: Point estimate of win rate
        confidence_interval: Tuple of (lower, upper) CI bounds
        damage_breakdown: DamageBreakdown instance with attribution
        avg_combat_duration_wins: Average rounds for party victories
        avg_combat_duration_losses: Average rounds for party defeats
        tpk_count: Number of total party kills
        final_states: List of all final CombatState objects
    """
    wins: int
    total_runs: int
    win_rate: float
    confidence_interval: tuple
    damage_breakdown: DamageBreakdown
    avg_combat_duration_wins: float
    avg_combat_duration_losses: float
    tpk_count: int
    final_states: list
    last_logger: object | None = None
    combined_log: str | None = None


class BatchRunner:
    """Manages batch simulation execution with progress tracking.

    Coordinates:
    - Monte Carlo simulation execution
    - Progress updates with current statistics
    - Damage breakdown collection from combat logs
    - Duration analysis for tactical insights
    """

    def __init__(self, monte_carlo_simulator, verbose: bool = True):
        """Initialize batch runner.

        Args:
            monte_carlo_simulator: MonteCarloSimulator instance
            verbose: Whether to print progress updates
        """
        self.simulator = monte_carlo_simulator
        self.verbose = verbose

    def run_batch(
        self,
        creatures: dict,
        agent,
        seed: Optional[int] = None,
        max_rounds: int = 100,
        terrain: Optional["Terrain"] = None,
        on_progress=None,
        lang: str = "en",
    ) -> BatchResults:
        """Execute batch simulation with comprehensive result collection.

        Runs Monte Carlo simulation and analyzes results for:
        - Win rate and confidence intervals
        - Damage breakdown by creature and ability
        - Combat duration patterns
        - TPK identification

        Args:
            creatures: Dict of creature_id -> Creature templates
            agent: Agent for action selection
            seed: Random seed for reproducibility
            max_rounds: Maximum rounds per combat

        Returns:
            BatchResults with comprehensive statistics

        Raises:
            ValueError: If simulation fails or returns invalid results
        """
        if self.verbose:
            print("Starting batch simulation...")
            print(f"  Min runs: {self.simulator.min_runs}")
            print(f"  Max runs: {self.simulator.max_runs}")
            print(f"  Target precision: ±{self.simulator.target_precision * 100:.1f}%")

        # Run Monte Carlo simulation
        try:
            sim_results = self.simulator.run_simulation(
                creatures=creatures,
                agent=agent,
                seed=seed,
                max_rounds=max_rounds,
                verbose=False,  # Disable per-combat logs for batch
                terrain=terrain,
                on_progress=on_progress,
                lang=lang,
            )
        except Exception as e:
            raise ValueError(f"Simulation failed: {e}") from e

        if self.verbose:
            print(f"\nSimulation complete: {sim_results.total_runs} runs")
            print(f"  Win rate: {sim_results.win_rate:.1%}")
            ci_lower, ci_upper = sim_results.confidence_interval
            print(f"  95% CI: [{ci_lower:.1%}, {ci_upper:.1%}]")

        # Analyze results
        damage_breakdown = self._extract_damage_breakdown(
            sim_results.loggers, creatures
        )

        duration_wins, duration_losses = self._analyze_combat_duration(
            sim_results.final_states, sim_results.loggers
        )

        tpk_count = self._count_tpks(sim_results.final_states, creatures)

        if self.verbose:
            print(f"\nDamage breakdown:")
            print(f"  Total damage: {damage_breakdown.total_damage}")
            print(f"  By creature: {len(damage_breakdown.by_creature)} sources")
            print(f"  By ability: {len(damage_breakdown.by_ability)} types")
            print(f"\nCombat duration:")
            print(f"  Wins: {duration_wins:.1f} rounds avg")
            print(f"  Losses: {duration_losses:.1f} rounds avg")
            print(f"  TPKs: {tpk_count} ({tpk_count/sim_results.total_runs:.1%})")

        last_logger = sim_results.loggers[-1] if sim_results.loggers else None

        # Build a combined log of all runs for TUI viewing
        combined_log_parts: list[str] = []
        for idx, logger in enumerate(sim_results.loggers, start=1):
            combined_log_parts.append(f"=== Run {idx} ===")
            combined_log_parts.append(logger.get_full_log())
            combined_log_parts.append("")  # blank line between runs
        combined_log = "\n".join(combined_log_parts).rstrip() if combined_log_parts else None

        return BatchResults(
            wins=sim_results.wins,
            total_runs=sim_results.total_runs,
            win_rate=sim_results.win_rate,
            confidence_interval=sim_results.confidence_interval,
            damage_breakdown=damage_breakdown,
            avg_combat_duration_wins=duration_wins,
            avg_combat_duration_losses=duration_losses,
            tpk_count=tpk_count,
            final_states=sim_results.final_states,
            last_logger=last_logger,
            combined_log=combined_log,
        )

    def _extract_damage_breakdown(
        self, loggers: list, creatures: dict
    ) -> DamageBreakdown:
        """Extract damage breakdown from combat logs.

        Parses combat logs to attribute damage to specific creatures and abilities.
        Handles both single attacks and multiattack actions.

        Args:
            loggers: List of CombatLogger instances
            creatures: Dict of creature_id -> Creature (for name mapping)

        Returns:
            DamageBreakdown with damage attributed by source
        """
        by_creature = defaultdict(int)
        by_ability = defaultdict(int)
        total_damage = 0

        # Build name -> creature_id mapping
        name_to_id = {c.name: cid for cid, c in creatures.items()}

        for logger in loggers:
            # Parse log entries for damage events
            # Log format: "    <damage> <type> damage -> <target> HP: <hp>"
            # Preceded by: "  <attacker> attacks <target> with <ability>: ..."

            current_attacker = None
            current_ability = None

            for entry in logger.entries:
                # Check for attack line (sets context for damage)
                if " attacks " in entry and " with " in entry:
                    # Parse: "  Goblin attacks Fighter with Scimitar: Hit!"
                    parts = entry.strip().split(" attacks ")
                    if len(parts) == 2:
                        attacker_name = parts[0].strip()
                        rest = parts[1]
                        if " with " in rest:
                            target_ability = rest.split(" with ")[1]
                            ability_name = target_ability.split(":")[0].strip()
                            current_attacker = attacker_name
                            current_ability = ability_name

                # Check for damage line
                elif "damage ->" in entry and current_attacker:
                    # Parse damage amount
                    # Handle various formats:
                    # "    5 slashing damage -> Fighter HP: 20"
                    # "    10 slashing damage (resisted, halved) -> Fighter HP: 25"
                    # "    Fighter is immune to fire damage! -> HP: 30"

                    # Skip immunity (0 damage)
                    if "is immune to" in entry:
                        continue

                    # Extract damage amount
                    damage_str = entry.strip().split()[0]
                    try:
                        damage = int(damage_str)
                    except ValueError:
                        continue  # Skip malformed lines

                    # Attribute damage
                    by_creature[current_attacker] += damage
                    if current_ability:
                        by_ability[current_ability] += damage
                    total_damage += damage

        return DamageBreakdown(
            by_creature=dict(by_creature),
            by_ability=dict(by_ability),
            total_damage=total_damage
        )

    def _analyze_combat_duration(
        self, final_states: list, loggers: list
    ) -> tuple:
        """Analyze combat duration for wins vs losses.

        Provides tactical insight: Do wins come quickly? Do losses drag on?

        Args:
            final_states: List of final CombatState objects
            loggers: List of CombatLogger instances

        Returns:
            Tuple of (avg_rounds_wins, avg_rounds_losses)
        """
        from src.simulation.victory import get_winner

        win_rounds = []
        loss_rounds = []

        for state, logger in zip(final_states, loggers):
            winner = get_winner(state)

            # Extract rounds from logger
            # Log format: "Combat Over. Winner: party in 5 rounds"
            rounds = self._extract_rounds_from_logger(logger)

            if winner == "party":
                win_rounds.append(rounds)
            else:
                loss_rounds.append(rounds)

        avg_wins = sum(win_rounds) / len(win_rounds) if win_rounds else 0.0
        avg_losses = sum(loss_rounds) / len(loss_rounds) if loss_rounds else 0.0

        return avg_wins, avg_losses

    def _extract_rounds_from_logger(self, logger) -> int:
        """Extract number of rounds from combat logger.

        Args:
            logger: CombatLogger instance

        Returns:
            Number of combat rounds
        """
        # Find last entry with "Combat Over"
        for entry in reversed(logger.entries):
            if "Combat Over" in entry and " in " in entry and " rounds" in entry:
                # Parse: "Combat Over. Winner: party in 5 rounds"
                try:
                    rounds_str = entry.split(" in ")[1].split(" rounds")[0]
                    return int(rounds_str)
                except (IndexError, ValueError):
                    pass

        # Default to 0 if not found
        return 0

    def _count_tpks(self, final_states: list, creatures: dict) -> int:
        """Count Total Party Kills.

        A TPK occurs when all party members reach 0 HP.

        Args:
            final_states: List of final CombatState objects
            creatures: Dict of creature_id -> Creature (for team identification)

        Returns:
            Number of TPKs
        """
        from src.simulation.victory import get_winner

        tpk_count = 0

        for state in final_states:
            winner = get_winner(state)

            # TPK means party lost (enemy won)
            if winner == "enemy":
                # Verify all party members are at 0 HP
                party_dead = all(
                    c.current_hp <= 0
                    for c in state.creatures.values()
                    if c.team == "party"
                )
                if party_dead:
                    tpk_count += 1

        return tpk_count
