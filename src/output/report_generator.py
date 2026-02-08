"""Report generation system with dual output (terminal + markdown).

Produces both immediate terminal summaries and detailed markdown reports
for DM session prep notes.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from src.simulation.batch_runner import BatchResults
from src.analysis.difficulty import calculate_difficulty_rating


class ReportGenerator:
    """Generates terminal summaries and markdown reports from simulation results.

    Produces dual output:
    - Terminal: Concise summary with win rate, CI, difficulty rating
    - Markdown: Detailed report with full statistics and per-run outcomes
    """

    def __init__(
        self,
        batch_results: BatchResults,
        creatures: Dict[str, any],
        party_size: int = 4,
        encounter_name: Optional[str] = None
    ):
        """Initialize report generator.

        Args:
            batch_results: BatchResults instance from batch simulation
            creatures: Dict of creature_id -> Creature templates
            party_size: Number of party members (for difficulty calculation)
            encounter_name: Optional name for the encounter (for report title)
        """
        self.results = batch_results
        self.creatures = creatures
        self.party_size = party_size
        self.encounter_name = encounter_name or "Combat Simulation"

        # Calculate derived metrics
        ci_lower, ci_upper = self.results.confidence_interval
        self.ci_width = ci_upper - ci_lower
        self.tpk_risk = self.results.tpk_count / self.results.total_runs

        # Calculate difficulty rating
        self.difficulty = calculate_difficulty_rating(
            win_rate=self.results.win_rate,
            ci_width=self.ci_width,
            tpk_risk=self.tpk_risk,
            avg_duration=self.results.avg_combat_duration_wins,
            party_size=self.party_size
        )

    def generate_terminal_summary(self) -> str:
        """Generate concise terminal summary.

        Returns:
            Formatted terminal output string
        """
        ci_lower, ci_upper = self.results.confidence_interval

        # Format primary result line
        summary = f"\n{'='*60}\n"
        summary += f"SIMULATION RESULTS: {self.encounter_name}\n"
        summary += f"{'='*60}\n\n"

        # Win rate with confidence interval
        summary += f"Party wins: {ci_lower:.0%}-{ci_upper:.0%} (95% CI) - {self.difficulty} difficulty\n"
        summary += f"  Point estimate: {self.results.win_rate:.1%}\n"
        summary += f"  Total runs: {self.results.total_runs}\n"
        summary += f"  TPK risk: {self.tpk_risk:.1%}\n\n"

        # Combat duration
        summary += f"Combat Duration:\n"
        summary += f"  Wins: {self.results.avg_combat_duration_wins:.1f} rounds (avg)\n"
        summary += f"  Losses: {self.results.avg_combat_duration_losses:.1f} rounds (avg)\n\n"

        # Damage breakdown by creature
        summary += f"Damage Breakdown:\n"
        summary += f"  Total damage: {self.results.damage_breakdown.total_damage}\n"

        if self.results.damage_breakdown.by_creature:
            summary += f"  By creature:\n"
            # Sort by damage (highest first)
            sorted_creatures = sorted(
                self.results.damage_breakdown.by_creature.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for creature_name, damage in sorted_creatures[:5]:  # Top 5
                pct = (damage / self.results.damage_breakdown.total_damage * 100) if self.results.damage_breakdown.total_damage > 0 else 0
                summary += f"    {creature_name}: {damage} ({pct:.1f}%)\n"

            if len(sorted_creatures) > 5:
                summary += f"    ... and {len(sorted_creatures) - 5} more\n"

        summary += f"\n{'='*60}\n"

        return summary

    def generate_markdown_report(self) -> str:
        """Generate detailed markdown report.

        Returns:
            Full markdown report as string
        """
        ci_lower, ci_upper = self.results.confidence_interval

        # Header
        report = f"# {self.encounter_name} - Simulation Report\n\n"
        report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Executive summary
        report += f"## Executive Summary\n\n"
        report += f"**Result:** Party wins {ci_lower:.0%}-{ci_upper:.0%} (95% CI)\n\n"
        report += f"**Difficulty Rating:** {self.difficulty}\n\n"
        report += f"**Key Statistics:**\n"
        report += f"- Win rate: {self.results.win_rate:.1%} ({self.results.wins}/{self.results.total_runs} runs)\n"
        report += f"- TPK risk: {self.tpk_risk:.1%} ({self.results.tpk_count} occurrences)\n"
        report += f"- Average combat duration: {self.results.avg_combat_duration_wins:.1f} rounds (wins), {self.results.avg_combat_duration_losses:.1f} rounds (losses)\n"
        report += f"- Party size: {self.party_size}\n\n"

        # Combat duration analysis
        report += f"## Combat Duration\n\n"
        report += f"| Outcome | Average Rounds |\n"
        report += f"|---------|----------------|\n"
        report += f"| Party wins | {self.results.avg_combat_duration_wins:.1f} |\n"
        report += f"| Party losses | {self.results.avg_combat_duration_losses:.1f} |\n\n"

        # Damage breakdown
        report += f"## Damage Analysis\n\n"
        report += f"**Total damage dealt:** {self.results.damage_breakdown.total_damage}\n\n"

        # By creature
        if self.results.damage_breakdown.by_creature:
            report += f"### Damage by Creature\n\n"
            report += f"| Creature | Damage | Percentage |\n"
            report += f"|----------|--------|------------|\n"

            sorted_creatures = sorted(
                self.results.damage_breakdown.by_creature.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for creature_name, damage in sorted_creatures:
                pct = (damage / self.results.damage_breakdown.total_damage * 100) if self.results.damage_breakdown.total_damage > 0 else 0
                report += f"| {creature_name} | {damage} | {pct:.1f}% |\n"

            report += f"\n"

        # By ability
        if self.results.damage_breakdown.by_ability:
            report += f"### Damage by Ability\n\n"
            report += f"| Ability | Damage | Percentage |\n"
            report += f"|---------|--------|------------|\n"

            sorted_abilities = sorted(
                self.results.damage_breakdown.by_ability.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for ability_name, damage in sorted_abilities:
                pct = (damage / self.results.damage_breakdown.total_damage * 100) if self.results.damage_breakdown.total_damage > 0 else 0
                report += f"| {ability_name} | {damage} | {pct:.1f}% |\n"

            report += f"\n"

        # Per-run outcomes table
        report += f"## Per-Run Outcomes\n\n"
        report += f"| Run # | Winner | Rounds | Party HP Remaining |\n"
        report += f"|-------|--------|--------|--------------------|\n"

        from src.simulation.victory import get_winner

        for idx, state in enumerate(self.results.final_states, start=1):
            winner = get_winner(state)

            # Calculate party HP remaining
            party_hp = sum(
                max(0, c.current_hp)
                for c in state.creatures.values()
                if c.team == "party"
            )

            # Extract rounds (from state or default)
            rounds = state.round_number if hasattr(state, 'round_number') else 0

            report += f"| {idx} | {winner} | {rounds} | {party_hp} |\n"

            # Limit to first 50 runs for readability
            if idx >= 50:
                report += f"\n*Showing first 50 of {self.results.total_runs} runs*\n\n"
                break

        if len(self.results.final_states) <= 50:
            report += f"\n"

        # Difficulty rating explanation
        report += f"## Difficulty Rating Explanation\n\n"
        report += f"The **{self.difficulty}** rating is calculated based on:\n\n"
        report += f"- Win rate: {self.results.win_rate:.1%}\n"
        report += f"- TPK risk: {self.tpk_risk:.1%}\n"
        report += f"- Combat duration: {self.results.avg_combat_duration_wins:.1f} rounds\n"
        report += f"- Party size adjustment: {self.party_size} players\n\n"
        report += f"**Rating Scale:**\n"
        report += f"- **Easy:** Win rate > 80%, TPK risk < 5%\n"
        report += f"- **Medium:** Win rate 60-80%, TPK risk < 15%\n"
        report += f"- **Hard:** Win rate 40-60%, TPK risk 15-30%\n"
        report += f"- **Deadly:** Win rate < 40%, TPK risk > 30%\n\n"

        # Footer
        report += f"---\n\n"
        report += f"*Generated by D&D Combat Simulator*\n"

        return report

    def save_markdown_report(self, output_dir: str = "data/reports") -> str:
        """Save markdown report to file.

        Args:
            output_dir: Directory to save report (default: data/reports/)

        Returns:
            Path to saved report file

        Raises:
            OSError: If directory creation or file write fails
        """
        # Create output directory if needed
        output_path = Path(output_dir)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create reports directory: {e}") from e

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}_simulation_report.md"
        filepath = output_path / filename

        # Generate and save report
        report_content = self.generate_markdown_report()

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
        except OSError as e:
            raise OSError(f"Failed to write report file: {e}") from e

        return str(filepath)
