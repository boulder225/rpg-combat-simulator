"""Textual TUI application for batch simulations with live progress."""

from dataclasses import dataclass
from typing import Any, Optional

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, TabbedContent, TabPane
from textual.containers import Vertical

from src.simulation.monte_carlo import MonteCarloSimulator
from src.simulation.batch_runner import BatchRunner
from src.tui.widgets.progress import SimulationProgress
from src.tui.widgets.log_viewer import CombatLogViewer
from src.tui.widgets.results_panel import ResultsPanel


@dataclass
class TuiConfig:
    creatures: dict[str, Any]
    agent: Any
    runs: int
    seed: Optional[int]
    terrain: Optional[Any]
    lang: str = "en"


class BatchProgressApp(App):
    """Textual App showing live progress for batch simulations."""

    CSS_PATH = None

    def __init__(self, config: TuiConfig) -> None:
        super().__init__()
        self._config = config
        self._progress_widget: SimulationProgress | None = None
        self._status: Static | None = None
        self._log_viewer: CombatLogViewer | None = None
        self._results_panel: ResultsPanel | None = None

    def compose(self) -> ComposeResult:
        """Compose the TUI layout: header, status/progress, and tabbed log/results."""
        yield Header(show_clock=True)

        with Vertical():
            yield Static("D&D Combat Simulator — Batch Mode (TUI)", id="title")

            self._status = Static("Preparing batch simulation...", id="status")
            yield self._status

            self._progress_widget = SimulationProgress(id="progress")
            yield self._progress_widget

            # Tabbed content: Log and Results
            with TabbedContent():
                with TabPane("Log", id="log"):
                    self._log_viewer = CombatLogViewer(id="log-viewer")
                    yield self._log_viewer
                with TabPane("Results", id="results"):
                    self._results_panel = ResultsPanel(id="results-panel")
                    yield self._results_panel

        yield Footer()

    def on_mount(self) -> None:
        """Start batch simulation when app mounts.

        Note: For now this runs in the main thread; batch runs are relatively
        fast and this keeps the implementation simple and robust.
        """
        if self._status is not None:
            self._status.update("Starting batch simulation...")
        # Run blocking work (progress updates go straight to widgets)
        self._run_batch_worker()

    # Worker -----------------------------------------------------------------

    def _run_batch_worker(self) -> None:
        cfg = self._config
        simulator = MonteCarloSimulator(
            min_runs=cfg.runs,
            max_runs=cfg.runs,
            target_precision=0.01,
            check_interval=max(1, min(100, cfg.runs)),
        )
        runner = BatchRunner(simulator, verbose=False)

        def on_progress(completed: int, total: int, wins: int) -> None:
            # We are already on the main thread; update widgets directly.
            self._handle_progress(completed, total, wins)

        results = runner.run_batch(
            cfg.creatures,
            cfg.agent,
            seed=cfg.seed,
            terrain=cfg.terrain,
            on_progress=on_progress,
            lang=cfg.lang,
        )

        self._handle_complete(results)

    # UI update helpers ------------------------------------------------------

    def _handle_progress(self, completed: int, total: int, wins: int) -> None:
        if self._progress_widget is not None:
            self._progress_widget.update_progress(completed, total, wins)
        if self._status is not None:
            self._status.update(f"Running simulations... ({completed}/{total})")

    def _handle_complete(self, results) -> None:
        if self._status is not None:
            self._status.update(
                f"Complete: {results.total_runs} runs, party win rate {results.win_rate:.1%}"
            )

        # Populate log viewer: show logs for all runs if available
        if self._log_viewer is not None:
            log_text = getattr(results, "combined_log", None)
            if not log_text and getattr(results, "last_logger", None):
                # Fallback: last run only
                log_text = results.last_logger.get_full_log()
            if log_text:
                self._log_viewer.set_content(log_text)

        # Populate results panel
        if self._results_panel is not None:
            # Party size = number of party creatures in config
            party_size = sum(
                1 for c in self._config.creatures.values() if getattr(c, "team", "") == "party"
            )
            self._results_panel.set_results(results, party_size=party_size or 4)


def run_tui(
    creatures: dict[str, Any],
    agent: Any,
    runs: int,
    seed: Optional[int] = None,
    terrain: Optional[Any] = None,
    lang: str = "en",
) -> None:
    """Entry point used by run.py when --tui is enabled."""
    config = TuiConfig(
        creatures=creatures,
        agent=agent,
        runs=runs,
        seed=seed,
        terrain=terrain,
        lang=lang,
    )
    app = BatchProgressApp(config)
    app.run()

