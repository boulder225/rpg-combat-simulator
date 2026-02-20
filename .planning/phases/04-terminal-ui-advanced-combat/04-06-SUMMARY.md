# Plan 04-06: TUI Log and Results Panel — Summary

## Overview
Extended the TUI to let the DM scroll through the combat log for the last run and view a styled results panel with win %, confidence interval, difficulty, and damage breakdown.

## Deliverables
- **BatchResults** (`src/simulation/batch_runner.py`): Added `last_logger` field; `run_batch` populates it from `SimulationResults.loggers[-1]` for use in the TUI.
- **Log viewer** (`src/tui/widgets/log_viewer.py`):
  - `CombatLogViewer` (subclass of `TextLog`) with `set_content(log_text: str)` that clears and re-adds lines, providing a scrollable combat log for the last run.
- **Results panel** (`src/tui/widgets/results_panel.py`):
  - `ResultsPanel` widget with `set_results(results: BatchResults, party_size: int = 4)`.
  - Renders win rate, 95% CI, TPK risk, difficulty label (via `calculate_difficulty_rating`), average durations, and top damage dealers using Rich markup for basic color highlighting (e.g., green/yellow/orange/red).
- **TUI app layout** (`src/tui/app.py`):
  - Imported `CombatLogViewer`, `ResultsPanel`, and `TabbedContent` / `TabPane`.
  - Layout now: title, status, progress bar, and a `TabbedContent` with two tabs:
    - **Log**: `CombatLogViewer` (scrollable).
    - **Results**: `ResultsPanel`.
  - `_handle_complete`:
    - Updates status with final run count and win rate.
    - If `results.last_logger` exists, calls `log_viewer.set_content(last_logger.get_full_log())`.
    - Computes party size from creatures and passes `BatchResults` into `results_panel.set_results(...)`.

## Verification
- `uv run pytest tests/` — **176 passing tests** after the TUI log/results changes.
- Manual smoke test: `python run.py --party fighter.md --enemies goblin --runs 5 --tui` launches the Textual app; after completion, the Log tab shows the last run’s combat log and the Results tab shows batch statistics with colored difficulty label and top damage dealers.

## Issues/Deviations
- Phase 4 scope: only the **last run** log is shown (not all runs), as planned.

