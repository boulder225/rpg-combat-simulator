# Phase 2: Creature Data & Monte Carlo Engine - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Batch simulation with real SRD creature data and statistical analysis. DM can run 1000+ simulations using SRD monsters, see win percentages with confidence intervals, damage breakdowns, and D&D difficulty ratings. Two capabilities: (1) auto-fetch creatures from dnd5eapi.co with caching, and (2) Monte Carlo batch runner with progressive sampling and statistical output.

</domain>

<decisions>
## Implementation Decisions

### SRD Data Fetching
- Cache-first resolution: check local file cache before hitting dnd5eapi.co API
- Local .md files always win: if DM has a local creature file, it takes priority over SRD entirely (no merging)
- Auto-map SRD action patterns: parse SRD action descriptions to extract attack bonus, damage dice, reach/range automatically
- Skip complex actions in Phase 2: only map melee/ranged attacks. Spellcasting and legendary actions deferred to later phases.
- File cache as .md files: fetched SRD creatures saved as markdown in `data/srd-cache/` (human-readable, editable)
- CLI uses creature name directly: `--enemies goblin goblin goblin` (no prefix needed). If no .md extension, assume SRD lookup.
- Auto-number duplicates: `--enemies goblin goblin` becomes goblin_0, goblin_1 with same stats, different IDs

### Batch Output Format
- Dual output: summary table to terminal + detailed markdown report to `data/reports/`
- Full stats: win rate, duration, damage breakdown, per-creature stats, difficulty rating
- Per-creature damage breakdown (not just per-team totals)
- Progress bar during runs: `[=====>    ] 523/1000 (52%)` — count only, no ETA
- Confidence intervals shown as range: `Party wins: 69%-77% (95% CI)`
- Per-run outcomes table included in markdown report (not terminal)

### Sampling Strategy
- Progressive sampling by default: start at 100 runs, check CI width every 100 runs, stop when ±5% or max 5000 reached
- Default 100 runs if user doesn't specify --runs or --precision
- Sequential execution (no multiprocessing) — parallelism deferred to future optimization
- Warn at 5 min mark but continue until done (no hard timeout)
- Live progress shows current win %: `[=====>    ] 300 runs | Party: 72% (67%-77%)`

### Difficulty Rating
- Combined metric: both party win rate AND TPK risk, label by the worse indicator
- Adjust thresholds for party size (4-player baseline)
- Duration factors into label: a "Hard" 12-round fight reads differently than a "Hard" 3-round fight
- Just label the difficulty — no encounter adjustment suggestions in Phase 2

### Claude's Discretion
- Exact CI width thresholds for progressive stopping
- SRD API response parsing strategy and error handling
- Markdown report layout and formatting
- Difficulty threshold exact values
- How to handle SRD creatures with no parseable attacks

</decisions>

<specifics>
## Specific Ideas

- DM workflow: `python run.py --party fighter.md --enemies goblin goblin goblin --runs 500` should just work
- Cache lives in `data/srd-cache/` alongside `data/creatures/` for discoverability
- Reports go to `data/reports/` with timestamped filenames
- Progressive sampling gives "good enough" fast, then refines — respects DM's time

</specifics>

<deferred>
## Deferred Ideas

- Spellcasting SRD creatures — Phase 5
- Legendary actions/resistances — v2 (ADV-04)
- Parallel simulation execution — future optimization
- Encounter adjustment suggestions — future phase
- Sensitivity analysis ("what if boss gets +2 AC") — v2 (ADV-01)

</deferred>

---

*Phase: 02-creature-data-monte-carlo*
*Context gathered: 2026-02-07*
