"""Results panel widget showing batch statistics with basic coloring."""

from typing import Optional

from textual.widgets import Static
from textual.reactive import reactive

from src.simulation.batch_runner import BatchResults
from src.analysis.difficulty import calculate_difficulty_rating


class ResultsPanel(Static):
    """Displays win rate, CI, difficulty, duration, and top damage dealers."""

    results: Optional[BatchResults] = reactive(None)
    party_size: int = reactive(4)

    def set_results(self, results: BatchResults, party_size: int = 4) -> None:
        self.results = results
        self.party_size = party_size

    def render(self) -> str:
        if not self.results:
            return "Results will appear here after the batch completes."

        r = self.results
        ci_lower, ci_upper = r.confidence_interval
        ci_width = ci_upper - ci_lower
        tpk_risk = (r.tpk_count / r.total_runs) if r.total_runs else 0.0
        difficulty = calculate_difficulty_rating(
            win_rate=r.win_rate,
            ci_width=ci_width,
            tpk_risk=tpk_risk,
            avg_duration=r.avg_combat_duration_wins,
            party_size=self.party_size,
        )

        # Simple color coding via Rich markup
        diff_color = {
            "Easy": "green",
            "Medium": "yellow",
            "Hard": "orange3",
            "Deadly": "red",
        }.get(difficulty, "white")

        lines: list[str] = []
        lines.append(f"[b]Batch Results[/b]")
        lines.append(
            f"Party wins: [b]{r.win_rate:.1%}[/b] "
            f"(95% CI: {ci_lower:.1%}–{ci_upper:.1%}, {r.wins}/{r.total_runs} runs)"
        )
        lines.append(f"TPK risk: {tpk_risk:.1%} ({r.tpk_count} TPKs)")
        lines.append(
            f"Difficulty: [b][{diff_color}]{difficulty}[/{diff_color}][/b]"
        )
        lines.append(
            f"Avg duration — wins: {r.avg_combat_duration_wins:.1f} rounds; "
            f"losses: {r.avg_combat_duration_losses:.1f} rounds"
        )
        lines.append("")

        # Damage breakdown
        lines.append(f"[b]Top damage dealers[/b]")
        if r.damage_breakdown.total_damage == 0 or not r.damage_breakdown.by_creature:
            lines.append("  No damage recorded.")
        else:
            sorted_creatures = sorted(
                r.damage_breakdown.by_creature.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:5]
            for name, dmg in sorted_creatures:
                pct = dmg / r.damage_breakdown.total_damage * 100.0
                lines.append(f"  {name}: {dmg} ({pct:.1f}% of total)")

        return "\n".join(lines)

