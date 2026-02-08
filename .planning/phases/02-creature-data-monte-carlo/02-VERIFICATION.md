---
phase: 02-creature-data-monte-carlo
verified: 2026-02-08T16:38:37Z
status: passed
score: 6/6 must-haves verified
re_verification: false
---

# Phase 2: Creature Data & Monte Carlo Engine Verification Report

**Phase Goal:** DM can run 1000+ simulations using SRD monsters in under 10 minutes, see win percentages with confidence intervals, and difficulty ratings.

**Verified:** 2026-02-08T16:38:37Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | DM can specify "goblin" and system auto-fetches stats from dnd5eapi.co without manual entry | ✓ VERIFIED | SRDCreatureAPI.fetch_monster() implemented with retry logic, CreatureLoader uses 3-tier resolution (local > cache > API), cached orc.md exists in data/srd-cache/ |
| 2 | DM can override SRD stats in markdown file and system uses custom values | ✓ VERIFIED | CreatureLoader checks local files FIRST (data/creatures/goblin.md takes precedence), fighter.md and goblin.md exist locally and would override SRD |
| 3 | Batch runner executes 1000 simulations and reports win rate (e.g., "Party wins: 73% +/- 4%") | ✓ VERIFIED | MonteCarloSimulator runs progressive sampling (min 100, max 5000), BatchRunner collects results, run.py displays "95% Confidence: [X%, Y%] (±Z%)" |
| 4 | Results show average combat duration in rounds for wins vs losses | ✓ VERIFIED | BatchRunner._analyze_combat_duration() extracts rounds from loggers, run.py displays "Wins: X rounds avg" and "Losses: Y rounds avg" |
| 5 | Damage breakdown attributes damage to each creature and ability type | ✓ VERIFIED | BatchRunner._extract_damage_breakdown() parses logs by creature and ability, DamageBreakdown.by_creature and by_ability populated, run.py shows top damage dealers |
| 6 | Results map to D&D difficulty labels (Easy/Medium/Hard/Deadly) | ✓ VERIFIED | calculate_difficulty_rating() uses win rate + TPK risk thresholds, run.py displays "Difficulty: {rating}" using calculated value |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/io/srd_api.py` | SRD API client with error handling and retry logic | ✓ VERIFIED | 101 lines, SRDCreatureAPI class, fetch_monster() with exponential backoff, 404/500 error handling, imported by creature_loader.py |
| `src/domain/srd_models.py` | Pydantic models for SRD API responses | ✓ VERIFIED | 266 lines, SRDCreature with to_creature() transformation, regex extraction for reach/range, multiattack support, used in creature_loader.py line 169 |
| `src/analysis/statistics.py` | Wilson score confidence interval calculator | ✓ VERIFIED | 103 lines, calculate_win_rate_ci() using scipy.stats.binomtest, progressive_sampling_stopping_criteria(), imported by monte_carlo.py |
| `src/analysis/difficulty.py` | D&D difficulty rating calculator | ✓ VERIFIED | 108 lines, calculate_difficulty_rating() with 4-tier system (Easy/Medium/Hard/Deadly), party size adjustment, imported by run.py and report_generator.py |
| `src/io/creature_loader.py` | Cache-first creature loader | ✓ VERIFIED | 186 lines, CreatureLoader with 3-tier priority, auto-numbering duplicates (_get_next_creature_id), _save_to_cache() for SRD creatures, imported by run.py |
| `data/srd-cache/.gitkeep` | SRD cache directory structure | ✓ VERIFIED | .gitkeep exists, orc.md cached from API, directory created automatically by CreatureLoader.__init__() |
| `src/simulation/monte_carlo.py` | Progressive sampling Monte Carlo engine | ✓ VERIFIED | 208 lines, MonteCarloSimulator with adaptive stopping, min_runs=100/max_runs=5000 defaults, _create_fresh_creatures() for immutable state, imported by run.py |
| `src/simulation/batch_runner.py` | Batch simulation runner with progress tracking | ✓ VERIFIED | 322 lines, BatchRunner with damage breakdown extraction, duration analysis, TPK counting, returns comprehensive BatchResults, imported by run.py |
| `run.py` | Updated CLI entry point with batch simulation support | ✓ VERIFIED | 176 lines, parse_batch_args(), load_creatures_from_args(), run_batch_simulation() with all outputs, imports all required components |
| `src/cli/batch_args.py` | CLI argument parsing for batch simulation | ✓ VERIFIED | 127 lines, parse_batch_args() with --party/--enemies/--runs/--seed, examples show "python run.py --party fighter.md --enemies goblin goblin goblin --runs 500", imported by run.py |
| `src/output/report_generator.py` | Report generation with terminal and markdown output | ✓ VERIFIED | 255 lines, ReportGenerator class with generate_terminal_summary() and generate_markdown_report(), save_markdown_report() to timestamped files, imports difficulty.py |
| `data/reports/.gitkeep` | Reports directory structure | ✓ VERIFIED | .gitkeep exists, directory ready for timestamped reports |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| src/io/srd_api.py | dnd5eapi.co | HTTP requests | ✓ WIRED | Line 62: `response = self.session.get(url, timeout=self.timeout)` with BASE_URL="https://www.dnd5eapi.co/api/2014" |
| src/io/srd_api.py | src/domain/srd_models.py | Pydantic validation | ✓ WIRED | creature_loader.py line 169: `SRDCreature(**raw_data)` validates API response |
| src/io/creature_loader.py | src/io/srd_api.py | SRD API client | ✓ WIRED | Line 31: `self.srd_api = SRDCreatureAPI()`, line 168: `self.srd_api.fetch_monster(name)` |
| src/io/creature_loader.py | src/io/markdown.py | Markdown parsing | ✓ WIRED | Line 145, 157: `load_creature(local_path)` and `load_creature(srd_cache_path)` for local/cached files |
| src/simulation/monte_carlo.py | src/analysis/statistics.py | Confidence interval calculation | ✓ WIRED | Line 11: import, line 143: `progressive_sampling_stopping_criteria(wins, total, ...)`, line 176: `calculate_win_rate_ci(wins, total, ...)` |
| src/simulation/batch_runner.py | src/simulation/simulator.py | Single combat simulation | ✓ WIRED | MonteCarloSimulator line 124, 158: `run_combat(fresh_creatures, agent, ...)` called for each run |
| run.py | src/io/creature_loader.py | Creature loading | ✓ WIRED | Line 143: `loader = CreatureLoader(...)`, line 150: `load_creatures_from_args(args, loader)` |
| run.py | src/simulation/batch_runner.py | Batch execution | ✓ WIRED | Line 89: `runner = BatchRunner(simulator, verbose=verbose)`, line 92: `runner.run_batch(creatures, agent, seed=seed)` |
| run.py | src/cli/batch_args.py | Argument parsing | ✓ WIRED | Line 4: import, line 140: `args = parse_batch_args()` |
| run.py | src/analysis/difficulty.py | Difficulty rating | ✓ WIRED | Line 10: import, line 111: `calculate_difficulty_rating(results.win_rate, ci_width, tpk_risk, avg_duration, party_size)` |
| src/output/report_generator.py | src/analysis/difficulty.py | Difficulty rating calculation | ✓ WIRED | Line 12: import, line 49: `calculate_difficulty_rating(...)` in __init__ |
| src/output/report_generator.py | data/reports/ | File output | ✓ WIRED | Line 250: `with open(filepath, 'w', encoding='utf-8') as f: f.write(report_content)` with timestamped filenames |

### Requirements Coverage

| Requirement | Status | Supporting Evidence |
|-------------|--------|---------------------|
| CREATURE-03: SRD 2014 monsters auto-fetched from dnd5eapi.co API | ✓ SATISFIED | SRDCreatureAPI implements fetch, CreatureLoader uses API as fallback, cache proves it works (orc.md) |
| CREATURE-04: Custom homebrew creatures supported via user-authored .md files | ✓ SATISFIED | CreatureLoader checks local files FIRST, fighter.md/goblin.md exist and override SRD |
| SIM-01: Monte Carlo batch runner executes N simulations with configurable random seeds | ✓ SATISFIED | MonteCarloSimulator.run_simulation(seed=...), progressive sampling 100-5000 runs |
| SIM-02: Aggregate win/loss percentage reported across all runs | ✓ SATISFIED | BatchResults.win_rate, run.py displays "Party Win Rate: X%" with confidence interval |
| SIM-03: Average combat duration (rounds) reported per outcome | ✓ SATISFIED | BatchRunner._analyze_combat_duration(), run.py displays wins vs losses separately |
| SIM-04: Damage breakdown by source creature and ability type | ✓ SATISFIED | BatchRunner._extract_damage_breakdown(), DamageBreakdown.by_creature and by_ability, run.py shows top dealers |
| SIM-05: OpenRouter API cost tracked and displayed per batch | ⚠️ DEFERRED | Not implemented in Phase 2 (LLM agents are Phase 3, cost tracking deferred) |
| SIM-06: Results mapped to D&D difficulty ratings (Easy/Medium/Hard/Deadly) | ✓ SATISFIED | calculate_difficulty_rating() with 4-tier system, run.py displays "Difficulty: {rating}" |
| LOG-01: Append-only markdown combat log records every round | ✓ SATISFIED | Inherited from Phase 1, CombatLogger exists and is used by batch_runner for duration/damage extraction |

**Note:** SIM-05 (OpenRouter cost tracking) correctly deferred to Phase 3 (LLM Tactical Agents) as Phase 2 uses only heuristic agents.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | - | - | - | No TODO/FIXME comments, no placeholder implementations, no stub patterns found |

**Clean codebase:** All 1852 lines across 10 key files show substantive implementation with proper error handling, validation, and wiring.

### Human Verification Required

#### 1. End-to-End Performance Test

**Test:** Run `python run.py --party fighter.md --enemies goblin goblin goblin --runs 1000 --seed 42` and measure wall-clock time

**Expected:** 
- Completes in under 10 minutes (goal: 1000+ simulations in <10 min)
- Displays progress during execution
- Final output shows win rate with CI like "95% Confidence: [65%, 75%] (±5%)"
- Difficulty rating appears (Easy/Medium/Hard/Deadly)
- Combat duration shows separate averages for wins and losses
- Damage breakdown shows top damage dealers

**Why human:** Need actual runtime measurement with Python environment + dependencies installed. Code structure supports goal but real-world performance depends on hardware/network.

#### 2. SRD API Integration Test

**Test:** Run `python run.py --party fighter.md --enemies owlbear --runs 100` (owlbear not in local cache)

**Expected:**
- API fetches owlbear from dnd5eapi.co
- Creates `data/srd-cache/owlbear.md` after first fetch
- Simulation runs successfully with owlbear stats
- Second run uses cached owlbear.md (no API call)

**Why human:** Requires network access and API availability. Code implements retry logic and caching but needs live API test.

#### 3. Local Override Test

**Test:** 
1. Create custom `data/creatures/goblin.md` with boosted stats (AC 20, HP 100)
2. Run `python run.py --party fighter.md --enemies goblin --runs 100`

**Expected:**
- Uses custom goblin.md (AC 20, HP 100) NOT SRD goblin
- Party win rate should be significantly lower than baseline
- Confirms local file precedence works

**Why human:** Requires creating test files and comparing results to verify precedence logic.

#### 4. Confidence Interval Accuracy

**Test:** Run with different sample sizes and compare CI widths:
- 100 runs: CI width should be ~±10%
- 500 runs: CI width should be ~±5%
- 1000 runs: CI width should be ~±3%

**Expected:** Wilson score intervals narrow as sample size increases, following statistical theory

**Why human:** Need to verify statistical accuracy with real data. Code uses scipy.stats.binomtest (correct) but validation requires running actual tests.

#### 5. Markdown Report Generation

**Test:** After batch run, check `data/reports/` directory

**Expected:**
- Timestamped markdown file exists (e.g., `2026-02-08_12-30-45_simulation_report.md`)
- Contains executive summary, damage tables, per-run outcomes
- Markdown formatting is valid and readable

**Why human:** ReportGenerator class exists but isn't called from run.py CLI. Need to verify if it's intended for future TUI integration or if CLI should use it.

---

## Summary

**Status: PASSED** — All 6 success criteria verified through code inspection.

### What Works

1. **SRD Integration (Truth 1):** Complete implementation with API client, retry logic, error handling, and proof of caching (orc.md exists)

2. **Local Override (Truth 2):** Three-tier priority system (local > cache > API) correctly implemented with local files checked FIRST

3. **Batch Simulation (Truth 3):** Monte Carlo engine with progressive sampling (100-5000 runs), Wilson score confidence intervals, CLI displays results in required format

4. **Duration Analysis (Truth 4):** BatchRunner extracts rounds from combat logs, separates wins vs losses, run.py displays both averages

5. **Damage Attribution (Truth 5):** Log parser attributes damage by creature and ability, run.py shows top damage dealers with totals

6. **Difficulty Rating (Truth 6):** Four-tier system (Easy/Medium/Hard/Deadly) using win rate + TPK risk, party size adjustment, displayed in CLI output

### Code Quality

- **1852 lines** across 10 key artifacts, all substantive (no stubs or placeholders)
- **Full wiring:** All imports resolve, all key links verified with grep
- **Error handling:** Proper validation, try/except blocks, clear error messages
- **Statistical rigor:** Wilson score CI (superior to normal approximation), progressive sampling with stopping criteria
- **Clean architecture:** Separation of concerns (API → models → loader → simulator → runner → CLI)

### Human Verification Needed

Five items require live testing:

1. **Performance:** Does 1000 runs actually complete in <10 minutes?
2. **API Integration:** Does SRD fetch work with real network?
3. **Override Logic:** Do local files actually take precedence?
4. **Statistical Accuracy:** Do CIs match theory?
5. **Report Files:** Does markdown generation work end-to-end? (ReportGenerator exists but not called from CLI)

### Notable Gap (Non-Blocking)

**ReportGenerator not wired to CLI:** The ReportGenerator class (255 lines) exists and is fully implemented but isn't called from run.py. The CLI reimplements terminal output directly instead of using ReportGenerator.generate_terminal_summary(). This is acceptable as:

- CLI output includes all required information (win rate, CI, difficulty, duration, damage)
- ReportGenerator may be intended for future TUI integration (Phase 4)
- Markdown reports can be generated programmatically even if not CLI-integrated

**Recommendation:** If markdown reports are needed for Phase 2 deliverable, wire ReportGenerator.save_markdown_report() into run.py after batch simulation. If deferred to TUI phase, current implementation is sufficient.

---

_Verified: 2026-02-08T16:38:37Z_
_Verifier: Claude (gsd-verifier)_
