"""Simple Textual widget for displaying batch simulation progress."""

from textual.reactive import reactive
from textual.widgets import Static


class SimulationProgress(Static):
    """ASCII progress bar for Monte Carlo runs."""

    completed: int = reactive(0)
    total: int = reactive(0)
    win_rate: float = reactive(0.0)

    def update_progress(self, completed: int, total: int, wins: int) -> None:
        """Update internal progress state."""
        self.completed = completed
        self.total = total
        self.win_rate = (wins / completed) if completed else 0.0

    def render(self) -> str:
        if not self.total:
            return "No runs started yet."

        ratio = self.completed / self.total if self.total else 0.0
        bar_width = 30
        filled = int(bar_width * ratio)
        bar = "[" + "#" * filled + "-" * (bar_width - filled) + "]"
        percent_done = ratio * 100.0
        win_pct = self.win_rate * 100.0
        return (
            f"{bar} {self.completed}/{self.total} runs "
            f"({percent_done:.1f}% complete) | Party wins: {win_pct:.1f}%"
        )

