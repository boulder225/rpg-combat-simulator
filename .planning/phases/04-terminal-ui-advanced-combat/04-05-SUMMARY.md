# Plan 04-05: TUI Shell and Progress — Summary

## Overview
Added a Textual-based TUI (`--tui`) that runs batch simulations in a background worker and shows live progress (runs completed and party win%).

## Deliverables
- **pyproject.toml**: Added `textual` dependency.
- **MonteCarloSimulator** (`src/simulation/monte_carlo.py`): `run_simulation(..., on_progress=None)` calls `on_progress(completed_runs, max_runs, wins)` after each run.
- **BatchRunner** (`src/simulation/batch_runner.py`): `run_batch(..., on_progress=None)` forwards the callback into `run_simulation`.
- **CLI args** (`src/cli/batch_args.py`): Added `tui: bool` to `BatchArgs` and a `--tui` flag.
- **run.py**:
  - If `--tui` and `--runs` are provided, calls `src.tui.app.run_tui` with the same creatures/agent/runs/seed/terrain as batch mode.
  - Otherwise preserves existing single-combat and batch CLI behavior.
- **TUI package**:
  - `src/tui/__init__.py`: exports `run_tui`.
  - `src/tui/widgets/progress.py`: `SimulationProgress` widget renders an ASCII progress bar with `X/N` and live party win%.
  - `src/tui/app.py`: `BatchProgressApp` creates a header, status text, progress bar, and runs `BatchRunner` inside `call_in_thread`, using `call_from_thread` to push progress updates back into the UI.

## Verification
- `uv run pytest tests/` — **176 passing tests** after changes.
- Manual: `python run.py --party fighter.md --enemies goblin --runs 5 --tui` launches the Textual app and shows progress updates.

## Issues/Deviations
None. Existing non-TUI CLI flows unchanged; TUI is opt-in via `--tui`.

