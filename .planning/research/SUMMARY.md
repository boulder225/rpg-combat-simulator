# Project Research Summary

**Project:** D&D 5e Combat Simulator
**Domain:** Terminal-based tactical combat simulator with AI agents
**Researched:** 2026-02-07
**Confidence:** MEDIUM-HIGH

## Executive Summary

This is a terminal-based Monte Carlo combat simulator for D&D 5e that helps DMs evaluate encounter balance during session prep. Unlike static difficulty calculators (D&D Beyond, Kobold Fight Club), this tool runs actual combat simulations with AI agents making tactical decisions, producing win percentages with statistical confidence intervals. The core differentiator is LLM-powered tactical AI that models realistic creature behavior rather than simplistic "attack nearest" heuristics.

The recommended approach is to build in layers: start with a pure Python core combat engine (domain models, rules, dice), add heuristic agents for baseline validation, then integrate Monte Carlo parallelization, and finally add LLM agents once the simulation framework is proven. Use Python 3.11 for performance, Textual for the terminal UI, Pydantic for data validation, and local Ollama for LLM inference (cloud OpenRouter as fallback). Target 8 minutes for 1000 simulations through parallel execution with joblib.

Key risks include: (1) LLM agents hallucinating illegal moves requiring strict validation layers, (2) advantage/disadvantage implemented incorrectly as counters instead of ternary state, (3) insufficient Monte Carlo sample sizes leading to unreliable statistics, and (4) combat model ignoring spatial positioning which affects most tactical mechanics. All risks are mitigable through careful architecture (immutable state, validation wrappers, statistical rigor, explicit spatial model decisions).

## Key Findings

### Recommended Stack

**Python 3.11+ ecosystem optimized for M1 Mac with 16GB RAM.** The stack emphasizes modern Python tooling (uv, ruff, Pydantic v2), local LLM inference (Ollama), and terminal-first UX (Textual). All libraries are actively maintained with recent 2026 releases.

**Core technologies:**
- **Python 3.11**: M1-optimized runtime with 25% performance boost over 3.10, modern typing features, async support for LLM integration
- **Textual 7.5.0**: Modern reactive TUI framework with live widgets, CSS-like styling, and async message-passing (released Jan 30, 2026)
- **Pydantic 2.12.5**: Industry standard for D&D stat modeling with runtime validation, YAML deserialization, and 17x performance improvement over v1
- **ollama 0.6.1**: Local LLM inference for 7B models (Mistral, Llama 3.3) running on M1 without GPU, simple chat/generate API
- **d20 1.1.2**: Fast dice engine supporting full D&D notation (advantage, keep highest, etc.) with security features and tree-based results for logging
- **dnd5epy 1.0.7**: Auto-generated OpenAPI client for dnd5eapi.co SRD 2014 content (monsters, spells, conditions)
- **uv 0.10.0**: 10-100x faster package manager than pip, manages Python versions and lockfiles in one tool
- **ruff 0.15.0**: 10-100x faster linter/formatter than flake8/black, replaces 8+ tools with single config

**Critical constraints:**
- Python 3.10+ required (pytest-asyncio constraint)
- Memory budget: 6GB OS + 6GB LLM + 4GB app = 16GB total
- M1 runs 7B models at ~20 tokens/sec (acceptable for turn-based, not real-time)

### Expected Features

**Table stakes (must have for v1):**
- Basic 5e mechanics (AC, HP, attack rolls, damage types, resistances) — users expect this
- Initiative system with advantage/disadvantage — core D&D mechanic
- Multiple attacks per creature — critical for action economy balance
- Target selection logic — even basic heuristics require this
- Monte Carlo batch simulation (20+ runs) — the core differentiator vs calculators
- Grid + positioning (basic) — enables tactical AI decisions
- Markdown combat logs — transparency and debugging
- Textual TUI with live progress — professional DM tool feel
- Markdown creature files (YAML frontmatter) — fits DM workflow
- Difficulty rating (Easy/Medium/Hard/Deadly) — standard DM vocabulary

**Differentiators (competitive advantage):**
- **LLM-powered tactical AI** — realistic behavior vs simple heuristics (THE differentiator)
- **Monte Carlo win percentages** — statistical certainty vs one-shot difficulty labels
- **8-minute target for 1000 runs** — actionable feedback during session prep, not overnight jobs
- **Terminal TUI** — professional tool vs web toy, shows real-time simulation progress
- **Custom creatures via markdown** — easy homebrew without code

**Should add after v1 validation:**
- Cover mechanics — tactical depth (when users request "archer tactics")
- Spell slot tracking — resource depletion for long encounters (when "casters feel overpowered")
- Conditions (prone, stunned, grappled) — control tactics (when "monk/grappler inaccuracy" reported)
- Resume from log files — recovery from crashes (when users lose simulation progress)
- Creature role archetypes — different AI for tank/striker/controller (when "all creatures use same tactics")

**Defer to v2+:**
- Sensitivity analysis ("what if +2 AC to boss?") — optimization tool, not core validation
- Legendary actions/resistances — high-CR only, <10% of encounters
- Lair actions — niche single-monster boss fights
- Action economy visualization — educational but not essential
- 2024 rules support — wait for demand, avoid dual ruleset complexity

**Anti-features (actively avoid):**
- Real-time 3D visualization — massive scope creep, breaks terminal focus
- Every spell in the game — SRD-only keeps it legally clean, 90% coverage
- Web-based UI — dilutes terminal tool differentiator
- Perfect AI that never makes mistakes — LLMs should model realistic creature intelligence, not chess-engine perfection

### Architecture Approach

**Layered architecture with immutable state, event sourcing, and agent strategy pattern.** Core design prioritizes testability (pure domain layer), parallelizability (immutable state), and flexibility (pluggable agents). The separation between domain logic (rules), decision logic (agents), and presentation (TUI) enables independent development and testing.

**Major components:**

1. **Domain Layer** (pure Python, no I/O) — `Creature`, `CombatState`, `distance.py`, `rules.py`
   - Pydantic models for creatures and combat state (immutable, frozen dataclasses)
   - Pure functions for D&D 5e rules: attack rolls, damage calculation, saves
   - Coordinate math and tactical logic (distance, advantage from positioning)

2. **Agent Decision Layer** (strategy pattern) — `BaseAgent`, `HeuristicAgent`, `LLMAgent`
   - Abstract interface: `choose_action(state, creature_id) -> Action`
   - Heuristic implementation for baseline (greedy, attack nearest)
   - LLM implementation with retry logic and validation wrapper

3. **Simulation Orchestration** — `simulator.py`, `monte_carlo.py`
   - Stateless combat runner: `run_combat(state, agent) -> final_state`
   - Parallel batch runner using joblib Loky backend (85-90% efficiency)
   - Victory condition detection and results aggregation

4. **I/O Layer** — `markdown.py`, `srd_api.py`, `logger.py`
   - Load creatures from .md files with YAML frontmatter parsing
   - Fetch SRD data from dnd5eapi.co with local JSON caching
   - Event sourcing: append-only combat logs enabling resume and analysis

5. **TUI Presentation** — `tui/app.py`, `tui/widgets/`, `tui/screens/`
   - Textual app with reactive message-passing (non-blocking async workers)
   - Progress bars, live combat logs, results tables
   - Background simulation workers posting progress messages to UI

**Key architectural patterns:**
- **Event Sourcing**: Combat stored as append-only event log, state derived by replay (enables resume, debugging, analysis)
- **Immutable State**: CombatState is frozen, copy-on-write semantics (thread-safe for parallel execution)
- **Agent Strategy Pattern**: BaseAgent interface allows swapping heuristic vs LLM without changing simulator
- **Retry with Exponential Backoff**: LLM calls wrapped in 1s/2s/4s retry logic for resilience
- **Parallel Monte Carlo**: joblib Loky backend for multi-core efficiency (target 8 cores, 85% scaling)
- **Reactive TUI**: Textual message-passing for async workers updating UI without blocking

**Build order implications:**
1. Domain layer first (pure Python, fast unit tests, everything depends on it)
2. Heuristic agents second (enables full combat loop testing without LLM complexity)
3. Simulation third (now have working combat to validate rules)
4. I/O fourth (load real creatures, not just test fixtures)
5. Monte Carlo fifth (requires proven simulator before adding parallelization)
6. LLM agents sixth (most complex, do last to avoid blocking progress)
7. TUI last (presentation layer needs working simulation to visualize)

### Critical Pitfalls

From analysis of D&D combat simulators, LLM agent systems, and Monte Carlo implementations:

1. **Advantage/disadvantage as counters** — Implementing as `+1/-1` numeric accumulation instead of ternary state (ADVANTAGE | NORMAL | DISADVANTAGE). D&D 5e rules: any source of advantage + any source of disadvantage = complete cancellation to NORMAL, regardless of count. Fix: Use state machine with explicit cancellation logic. Validate in Phase 1 (Core Combat Engine) with unit test: 2x advantage + 1x disadvantage = NORMAL state, rolls 1d20.

2. **LLM agents hallucinating illegal moves** — LLMs generate plausible-sounding but invalid actions (goblin casting Fireball, moving twice, casting while silenced). In Chess.com experiments, ChatGPT repeatedly made illegal moves. Fix: Validation layer treats LLM output as suggestions, not commands. Parse response, validate against creature statblock, action economy, conditions, and resources. Reject and re-prompt with error feedback. Verify in Phase 4 (AI Agents) with test: LLM suggests "cast Fireball" for goblin, validation rejects (not in spell list).

3. **Insufficient Monte Carlo sample size** — Running <500 simulations produces unreliable balance assessments. Small samples amplify dice variance, can't distinguish 60% from 70% win rate (moderate vs severe imbalance). Fix: Calculate required sample size for ±5% confidence interval at 95% confidence = ~1,500-2,000 simulations. Implement progressive sampling: run 500, check CI width, continue if needed. Display CI in results. Verify in Phase 5 with statistical test: 2000 runs produce ±5% CI.

4. **Concentration stacking** — Failing to automatically end first concentration spell when casting second. Allows illegal multiple buff states (Bless + Haste simultaneously), dramatically skews balance. Fix: Track concentration as single slot: `creature.concentration = Optional[Spell]`. When casting concentration spell, execute `if creature.concentration: creature.concentration.end()` first. Verify in Phase 2 (Spell System) with integration test: Bless → Haste on same caster ends Bless, only Haste active.

5. **Resume without state checkpointing** — Attempting to reconstruct state from human-readable markdown logs fails when logs are lossy (missing RNG seeds, queued reactions, AI rationale). Resumed combat diverges from original. Fix: Separate concerns: binary checkpoints for resume (include complete state, RNG seed, queued effects) vs markdown logs for humans. Checkpoints are source of truth. Verify in Phase 6 with resume test: checkpoint at round 5, resume, exact same outcome as non-resumed.

6. **Dimensionless combat model** — Simulating without grid/distance makes opportunity attacks, reach weapons, ranged disadvantage, AoE targeting, and cover impossible to implement correctly. Most tactical mechanics depend on positioning. Fix: Either (a) accept limitations and document what's NOT modeled, or (b) implement minimal spatial model (discrete zones: melee/short/long range). Architectural decision required in Phase 1 before building action resolution.

7. **SRD API mapping mismatches** — Naive mapping from API structure (hit_dice: "2d6" string) to internal model (hit_die_count: int, hit_die_type: int) breaks on edge cases (spellcasters, legendary creatures, swarms). Fix: Schema validation with Pydantic. Define APICreature and SimulationCreature schemas, write tested adapter handling dice parsing, action types, special traits, optional fields. Test with diverse creatures (spellcasters, dragons, aberrations). Verify in Phase 3 with diversity test: load 50 random creatures, all parse correctly.

**Additional technical debt risks:**
- Skipping concentration validation (never acceptable — core rule for spell balance)
- Synchronous LLM calls in TUI event loop (causes 3-5s freezes, poor UX)
- Deep-copying entire state each round (slows down with >8 creatures or >12 rounds)
- No timeout handling on LLM API calls (blocking on slow responses)

## Implications for Roadmap

Based on research dependencies and build order analysis, suggested phase structure:

### Phase 1: Core Combat Engine
**Rationale:** Pure Python domain layer with no external dependencies. Foundation for everything else. Fast unit tests enable rapid iteration. Critical architectural decisions (spatial model, advantage/disadvantage, immutable state) must be made here.

**Delivers:**
- Pydantic creature models with stat blocks, actions, HP tracking
- Combat state with initiative ordering and round tracking
- D&D 5e rules engine: attack rolls, damage calculation, saves
- Dice rolling with advantage/disadvantage (ternary state, NOT counters)
- Coordinate system and distance calculations (discrete zones or full grid — decide early)

**Addresses features:**
- Basic 5e mechanics (AC, HP, attacks)
- Initiative system
- Advantage/disadvantage
- Damage types and resistances
- Hit point tracking

**Avoids pitfalls:**
- Advantage/disadvantage counters (use ternary state machine)
- Dimensionless model (make explicit spatial architecture decision)
- Shared mutable state (use frozen dataclasses)

**Research flag:** Low need — D&D 5e rules are well-documented, d20 library handles dice complexity.

---

### Phase 2: Heuristic Agents & Single Combat
**Rationale:** Implement deterministic agents before LLM complexity. Enables end-to-end combat simulation testing without API dependencies, timeouts, or validation layers. Greedy heuristics (attack nearest, attack weakest) are sufficient to validate core mechanics.

**Delivers:**
- BaseAgent abstract interface with `choose_action(state, creature_id) -> Action`
- HeuristicAgent implementing greedy tactics (attack nearest enemy with highest HP)
- Single combat simulator: turn loop, agent decisions, victory detection
- Event logging to markdown (append-only, structured events)

**Uses stack:**
- d20 for dice rolls
- Pydantic models from Phase 1
- pathlib for log file handling

**Implements architecture:**
- Agent strategy pattern
- Event sourcing (combat log replay)
- Stateless simulator function

**Avoids pitfalls:**
- Embedding rules in agents (agents choose, simulator executes via rules.py)
- Parsing markdown during simulation (load creatures once, cache in memory)

**Research flag:** Low need — Strategy pattern and event sourcing are well-established patterns.

---

### Phase 3: Creature Data Integration
**Rationale:** Real creature variety required to validate combat balance. SRD API provides 300+ monsters. Markdown file format fits DM workflow (many already use markdown notes). Adapter layer isolates API changes from domain.

**Delivers:**
- Markdown parser using python-frontmatter (YAML headers + content)
- SRD API client with local JSON caching (30-day TTL)
- Schema validation: APICreature → SimulationCreature adapter
- Creature loading with fallback (markdown → SRD API → cache)

**Uses stack:**
- python-frontmatter for .md parsing
- dnd5epy for SRD API client
- Pydantic for schema validation
- httpx for API calls with retry

**Implements architecture:**
- I/O layer separation (domain never imports I/O)
- @lru_cache for creature loading performance

**Avoids pitfalls:**
- SRD API mapping mismatches (tested adapter with diverse creatures)
- Loading files during simulation (cache creatures in memory)

**Research flag:** Low need — dnd5eapi.co is well-documented, Pydantic validation is straightforward.

---

### Phase 4: Monte Carlo Batch Engine
**Rationale:** Parallel execution required to hit 8-minute target for 1000 simulations. Joblib Loky backend provides 85-90% efficiency on multi-core. Immutable state from Phase 1 makes parallelization safe. Must implement before LLM agents to establish baseline performance.

**Delivers:**
- Parallel batch runner using joblib with Loky backend
- Seed management for reproducible random sequences
- Results aggregation: win rate, confidence intervals, avg rounds, HP distributions
- Statistical validation: require minimum sample size for target CI width

**Uses stack:**
- joblib for parallel execution
- stdlib statistics for confidence intervals

**Implements architecture:**
- Parallel Monte Carlo pattern
- Copy-on-write state isolation per worker

**Avoids pitfalls:**
- Insufficient sample size (validate 1500-2000 runs for ±5% CI at 95% confidence)
- Shared mutable state (immutable CombatState prevents race conditions)
- Memory bloat (batch_size=100 to chunk work)

**Research flag:** Medium need — Performance tuning may require experimentation with worker counts, batch sizes, and state serialization overhead.

---

### Phase 5: LLM Tactical Agents
**Rationale:** Core differentiator requiring stable simulation framework first. Most complex integration (API keys, retries, validation, prompt engineering). Local Ollama for privacy/latency, OpenRouter for experimentation. Validation layer critical to prevent hallucinations.

**Delivers:**
- LLMAgent implementing BaseAgent interface
- Ollama integration for local 7B models (Mistral, Llama 3.3)
- OpenRouter integration for cloud fallback
- Retry logic with exponential backoff (1s, 2s, 4s)
- Validation wrapper: verify actions against statblock, action economy, conditions, resources
- Prompt engineering: format state for LLM, parse JSON responses

**Uses stack:**
- ollama SDK for local inference
- openrouter SDK for cloud fallback
- httpx for robust HTTP with timeouts

**Implements architecture:**
- Retry with exponential backoff pattern
- Validation layer treating LLM output as suggestions

**Avoids pitfalls:**
- LLM hallucinations (strict validation rejecting illegal moves with error feedback)
- Blocking TUI (use async workers, not synchronous calls in event loop)
- Unlimited context (sliding window of last 5 turns, 2k-4k token limit for 7B models)
- No timeout handling (aggressive 5-10s timeouts, fallback to heuristic on failure)

**Research flag:** High need — Prompt engineering for tactical decisions, validation schema design, and performance optimization (LLM latency dominates runtime) require experimentation.

---

### Phase 6: Textual Terminal UI
**Rationale:** Presentation layer requires working simulation + Monte Carlo to visualize. Can develop CLI first, add TUI later. Textual's reactive message-passing enables non-blocking async workers showing live progress.

**Delivers:**
- Textual App with screens (combat, results)
- Widgets: progress bars, live combat log viewer, results table with confidence intervals
- Async workers running simulations in background
- Message-passing for state updates (SimulationProgress events)
- CLI mode for headless batch runs

**Uses stack:**
- Textual for TUI framework
- rich for markdown rendering in logs

**Implements architecture:**
- Reactive TUI with message-passing
- Background workers with `call_from_thread()` for UI updates

**Avoids pitfalls:**
- Blocking LLM calls in main thread (use run_worker for async execution)
- Regenerating widgets on every update (reactive attributes, partial diffing)
- Missing thread safety (marshal updates via call_from_thread)

**Research flag:** Low need — Textual has excellent documentation and tutorials.

---

### Phase 7: Spell System & Conditions
**Rationale:** Add after core mechanics proven. Spells and conditions create complex interactions requiring stable foundation. Concentration tracking critical for spell balance.

**Delivers:**
- SRD spell integration (damage spells, buff spells)
- Concentration tracking as single slot per creature
- Spell slot management and depletion
- Conditions (prone, stunned, grappled, restrained)
- Condition effects on attacks, saves, and movement

**Uses stack:**
- dnd5epy for spell data from SRD

**Implements architecture:**
- Concentration as mutually exclusive resource

**Avoids pitfalls:**
- Concentration stacking (enforce single slot, auto-end previous spell)
- Missing condition interactions (prone = melee advantage, ranged disadvantage)

**Research flag:** Medium need — Spell interactions and condition precedence may require rules clarification.

---

### Phase 8: Resume & State Persistence
**Rationale:** Recovery from crashes valuable for long simulation runs. Must design checkpointing separate from human logs. Defer until simulation framework stable.

**Delivers:**
- Binary checkpoint format (pickle or JSON) with complete state
- RNG seed preservation for exact replay
- Resume logic: load checkpoint, continue simulation, append to same log
- Checkpoint rotation (keep last N checkpoints)

**Implements architecture:**
- Separation: binary checkpoints (machine) vs markdown logs (human)

**Avoids pitfalls:**
- Resume from markdown (use binary checkpoints as source of truth)
- No RNG seed (preserve seed for deterministic replay)

**Research flag:** Low need — Standard checkpointing patterns.

---

### Phase Ordering Rationale

**Dependencies drive order:**
- Phases 1-3 are sequential dependencies: Core → Agents → Data (can't test agents without core, can't load real creatures without data layer)
- Phase 4 (Monte Carlo) requires Phases 1-3 complete (needs working single combat)
- Phase 5 (LLM) requires Phases 1-4 complete (needs stable simulation framework before adding complexity)
- Phases 6-8 can be parallelized or reordered (TUI, Spells, Resume are independent enhancements)

**Risk mitigation through layering:**
- Pure domain first (fastest feedback loop, no I/O delays)
- Heuristic agents before LLM (validate mechanics without API dependencies)
- Monte Carlo before LLM (establish performance baseline, detect bottlenecks)
- TUI last (presentation doesn't block core functionality)

**Performance optimization sequencing:**
- Phase 4 identifies performance bottlenecks (combat simulation speed)
- Phase 5 adds major latency source (LLM calls)
- Can't optimize LLM integration until baseline performance known

### Research Flags

**Phases needing deeper research during planning:**
- **Phase 4 (Monte Carlo):** Performance tuning (worker counts, batch sizes, state serialization overhead) requires benchmarking on target hardware
- **Phase 5 (LLM Agents):** Prompt engineering for tactical decisions, validation schema design, context window management need experimentation
- **Phase 7 (Spells/Conditions):** Complex spell interactions (concentration + conditions, AoE targeting with positioning) may need rules clarification

**Phases with standard patterns (skip research-phase):**
- **Phase 1 (Core):** D&D 5e rules well-documented, established patterns
- **Phase 2 (Heuristic Agents):** Strategy pattern is standard OOP
- **Phase 3 (Data):** API integration is straightforward with Pydantic
- **Phase 6 (TUI):** Textual has excellent tutorials and examples
- **Phase 8 (Resume):** Standard checkpointing patterns

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All libraries verified on PyPI with recent 2026 releases. Python 3.11 on M1 well-tested. Ollama 7B performance benchmarked. |
| Features | MEDIUM | Feature priorities based on competitor analysis and domain research. MVP scope validated against existing simulators, but user validation needed. |
| Architecture | HIGH | Patterns (immutable state, event sourcing, agent strategy) proven in similar domains. Build order validated against dependency analysis. |
| Pitfalls | MEDIUM-HIGH | Critical pitfalls (advantage/disadvantage, LLM hallucinations, Monte Carlo sample size) verified with multiple sources. Some edge cases may emerge during implementation. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

**Performance uncertainty:**
- **Gap:** Actual runtime for 1000 simulations unknown until implementation. 8-minute target may require optimization.
- **Handle:** Benchmark Phase 2 (single combat) to establish baseline. If >0.5s per combat, optimize before Phase 4. Profile bottlenecks (dice rolling, state copying, rule evaluation).

**LLM prompt engineering:**
- **Gap:** Optimal prompts for tactical decisions unknown. Balance between context (state detail) and token budget (2k-4k limit for 7B models).
- **Handle:** Iterative experimentation in Phase 5. Start with minimal state (HP, positions, actions), expand based on decision quality. A/B test prompts.

**Spatial model complexity:**
- **Gap:** Full grid pathfinding may be too expensive for 1000-run batches. Discrete zones may oversimplify tactics.
- **Handle:** Prototype both approaches in Phase 1. Benchmark grid (A* pathfinding) vs zones (simple distance). Choose based on runtime vs accuracy tradeoff. Document limitations.

**Statistical rigor:**
- **Gap:** Required sample size depends on encounter variance (high-variance encounters need more runs). 1500-2000 is estimate, not precise.
- **Handle:** Implement progressive sampling in Phase 4. Run 500, calculate CI width, continue if >5%. Adaptive sample size per encounter.

**Rule ambiguities:**
- **Gap:** Some D&D 5e rules (e.g., simultaneous damage resolution, exact concentration check timing) have community debate.
- **Handle:** Document interpretation decisions in Phase 1. Link to Sage Advice, Crawford rulings. Flag "house rule" choices in logs.

## Sources

### Primary (HIGH confidence)
- **Technology Stack:** PyPI verified versions (Textual 7.5.0, Pydantic 2.12.5, ollama 0.6.1) with official documentation
- **D&D 5e Rules:** D&D Beyond official resources, SRD 2014 via dnd5eapi.co
- **Architecture Patterns:** Azure Architecture Center (event sourcing), Martin Fowler (event sourcing canonical definition), Textual official docs

### Secondary (MEDIUM confidence)
- **Feature Analysis:** Competitor tools (D&D Beyond, Kobold Plus Fight Club), GitHub simulators (DnD-battler, dnd-combat-sim, DnD5e-CombatSimulator)
- **LLM Tactical AI:** Recent research (Dec 2025 UCSD D&D AI study, Claude 3.5 Haiku tactical performance), Medium articles on LLM game integration
- **Monte Carlo Simulation:** Academic papers (IEEE parallel simulation, Stanford RAWR D&D optimization), practical guides (Medium sample size estimation)

### Tertiary (LOW confidence)
- **Performance Estimates:** 8-minute target extrapolated from M1 benchmarks (20 tok/s for 7B models) and joblib efficiency (85-90%). Needs validation.
- **UX Patterns:** Terminal TUI best practices from Medium articles, Textual blog posts. Community-driven, not research-backed.

---
*Research completed: 2026-02-07*
*Ready for roadmap: yes*
