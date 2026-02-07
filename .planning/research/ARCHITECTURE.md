# Architecture Research

**Domain:** D&D 5e Combat Simulator with Monte Carlo Analysis
**Researched:** 2026-02-07
**Confidence:** MEDIUM-HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Presentation Layer                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │
│  │ CLI Entry  │  │ Textual    │  │ Progress   │                 │
│  │ (run.py)   │  │ TUI App    │  │ Display    │                 │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘                 │
│        │               │               │                         │
├────────┴───────────────┴───────────────┴─────────────────────────┤
│                    Simulation Orchestration                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │         Monte Carlo Batch Runner                           │  │
│  │  (parallel execution, seed management, aggregation)        │  │
│  └──────────────────────────────┬─────────────────────────────┘  │
│                                 │                                │
│  ┌──────────────────────────────┴─────────────────────────────┐  │
│  │         Single Combat Simulator                            │  │
│  │  (turn loop, initiative, victory detection)                │  │
│  └──────────────────────────────┬─────────────────────────────┘  │
│                                 │                                │
├─────────────────────────────────┴─────────────────────────────────┤
│                       Agent Decision Layer                        │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │ BaseAgent   │  │ Heuristic    │  │ LLM Agent               │  │
│  │ (abstract)  │  │ Agent        │  │ (ollama/openai)         │  │
│  └─────────────┘  └──────────────┘  └─────────────────────────┘  │
├───────────────────────────────────────────────────────────────────┤
│                       Core Domain Layer                           │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────────┐   │
│  │ CombatState  │  │ Creature      │  │ Distance/Geometry    │   │
│  │ (immutable)  │  │ (Pydantic)    │  │ (tactical logic)     │   │
│  └──────┬───────┘  └───────┬───────┘  └──────────┬───────────┘   │
│         │                  │                      │               │
├─────────┴──────────────────┴──────────────────────┴───────────────┤
│                        Data & Logging Layer                       │
│  ┌───────────┐  ┌──────────────┐  ┌────────────────────────────┐ │
│  │ Markdown  │  │ Creature     │  │ SRD API Cache              │ │
│  │ Logger    │  │ Definitions  │  │ (dnd5eapi.co)              │ │
│  │ (events)  │  │ (.md files)  │  │                            │ │
│  └───────────┘  └──────────────┘  └────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **run.py** | CLI entry, argument parsing, mode routing | argparse/click, dispatches to simulator or TUI |
| **Textual TUI** | Live progress, combat log display, results table | Textual app with reactive widgets, async message handlers |
| **Monte Carlo Runner** | Batch orchestration, parallel execution, seed mgmt | multiprocessing.Pool or joblib.Parallel with Loky backend |
| **Combat Simulator** | Turn loop: roll initiative → turns → victory check | Stateless function accepting CombatState, returns final state |
| **BaseAgent** | Decision API: `choose_action(state, creature_id)` | Abstract base class with Heuristic and LLM implementations |
| **CombatState** | Immutable snapshot: creatures, positions, HP, initiative | Pydantic dataclass with copy-on-write semantics |
| **Creature** | Stats: HP, AC, actions, position, conditions | Pydantic model loaded from markdown or SRD API |
| **Distance/Geometry** | Coord parsing, distance calc, advantage/cover logic | Pure functions operating on (x, y) tuples |
| **Markdown Logger** | Append-only event log for resume/analysis | Open file, write structured events, close on combat end |
| **SRD API Client** | Fetch monster stat blocks, cache locally | HTTP client with JSON cache in data/cache/ |

## Recommended Project Structure

```
dnd-simulator/
├── src/
│   ├── domain/              # Core business logic (no I/O)
│   │   ├── creature.py      # Pydantic model: Creature, Action, StatBlock
│   │   ├── combat_state.py  # CombatState (immutable), initiative ordering
│   │   ├── distance.py      # Coordinate parsing, distance, advantage
│   │   └── rules.py         # D&D 5e rules: attack roll, damage, saves
│   ├── agents/              # Decision-making implementations
│   │   ├── base.py          # BaseAgent abstract interface
│   │   ├── heuristic.py     # HeuristicAgent (greedy, simple tactics)
│   │   ├── llm.py           # LLMAgent (ollama/openai integration)
│   │   └── retry.py         # LLM retry logic with exponential backoff
│   ├── simulation/          # Combat execution and orchestration
│   │   ├── simulator.py     # run_combat(state, agent) -> final_state
│   │   ├── monte_carlo.py   # batch_run(encounter, n_sims, parallel=True)
│   │   └── victory.py       # Victory condition detection
│   ├── io/                  # External integration (files, APIs, logs)
│   │   ├── markdown.py      # Load creatures from .md, write combat logs
│   │   ├── srd_api.py       # Fetch from dnd5eapi.co, cache locally
│   │   └── logger.py        # Structured event logging
│   ├── tui/                 # Textual terminal UI
│   │   ├── app.py           # Main Textual App with screens
│   │   ├── widgets/         # Custom widgets (progress, log viewer)
│   │   └── screens/         # Combat screen, results screen
│   └── utils/               # Shared utilities
│       ├── dice.py          # d20, advantage/disadvantage logic
│       └── config.py        # Config loading (YAML/TOML)
├── run.py                   # CLI entry point
├── data/
│   ├── creatures/           # .md stat blocks (custom format)
│   ├── encounters/          # .md encounter definitions
│   ├── cache/               # SRD API JSON cache
│   └── saved_games/         # Markdown combat logs for resume
├── tests/
│   ├── unit/                # Pure function tests (domain, distance)
│   ├── integration/         # Agent + simulator tests
│   └── fixtures/            # Test creatures and encounters
└── .planning/
    └── research/            # This file
```

### Structure Rationale

- **`domain/`**: Pure Python, no I/O. Enables fast unit tests and easy reasoning. Creature, CombatState, and rules are the "kernel" of the simulator.
- **`agents/`**: Isolated decision-making. BaseAgent interface allows plugging heuristic or LLM without changing simulator.
- **`simulation/`**: Orchestration layer. `simulator.py` is stateless (takes state, returns state), making it easy to parallelize in `monte_carlo.py`.
- **`io/`**: All file/network I/O lives here. Keeps domain pure and testable.
- **`tui/`**: Textual UI is separate concern. Can run headless batch simulations without importing Textual.

## Architectural Patterns

### Pattern 1: Event Sourcing for Combat Logs

**What:** Store combat as append-only event log (initiative rolled, attack made, damage dealt, creature defeated). Current state is derived by replaying events.

**When to use:** Always for this project. Enables resume-from-log, analysis of tactical decisions, and debugging.

**Trade-offs:**
- **Pro**: Complete audit trail, time-travel debugging, easy to serialize to Markdown
- **Pro**: Replay events to reconstruct exact combat state at any turn
- **Con**: Slightly more complex than direct state mutation (but worth it)

**Example:**
```python
# logger.py writes events
logger.log_event({
    "type": "attack",
    "turn": 3,
    "attacker": "goblin-1",
    "target": "fighter",
    "roll": 15,
    "hit": True,
    "damage": 5
})

# resume.py replays events to rebuild state
def load_combat(log_path: Path) -> CombatState:
    state = CombatState.initial()
    for event in parse_log(log_path):
        state = apply_event(state, event)
    return state
```

### Pattern 2: Immutable State with Copy-on-Write

**What:** CombatState is immutable. Every state change returns a new CombatState with updated values. Old state remains valid.

**When to use:** Always. Critical for parallel Monte Carlo simulations where each run must be isolated.

**Trade-offs:**
- **Pro**: Thread-safe by default, easy to parallelize, no shared mutable state bugs
- **Pro**: Easier to debug (states don't change under you)
- **Con**: Slightly more memory (but Python GC handles this well with structural sharing)

**Example:**
```python
@dataclass(frozen=True)
class CombatState:
    creatures: dict[str, Creature]
    initiative_order: list[str]
    round: int

    def take_damage(self, creature_id: str, damage: int) -> "CombatState":
        """Returns new state with updated HP."""
        updated = self.creatures[creature_id].reduce_hp(damage)
        return replace(self, creatures={**self.creatures, creature_id: updated})
```

### Pattern 3: Agent Strategy Pattern

**What:** BaseAgent defines `choose_action(state, creature_id) -> Action`. HeuristicAgent and LLMAgent implement different strategies.

**When to use:** Always. Allows swapping AI without changing simulator.

**Trade-offs:**
- **Pro**: Easy to test (mock agent in tests), compare strategies (heuristic vs LLM)
- **Pro**: Can mix strategies (goblin uses heuristic, boss uses LLM)
- **Con**: Requires interface discipline (but prevents coupling)

**Example:**
```python
class BaseAgent(ABC):
    @abstractmethod
    def choose_action(self, state: CombatState, creature_id: str) -> Action:
        pass

class HeuristicAgent(BaseAgent):
    def choose_action(self, state, creature_id):
        # Attack nearest enemy with highest HP
        return greedy_attack(state, creature_id)

class LLMAgent(BaseAgent):
    def choose_action(self, state, creature_id):
        prompt = format_state_for_llm(state, creature_id)
        response = self.llm.call(prompt)
        return parse_llm_action(response)
```

### Pattern 4: Retry with Exponential Backoff for LLM Calls

**What:** Wrap LLM API calls in retry logic: on error or malformed response, wait (1s, 2s, 4s, ...) and retry up to 3 times.

**When to use:** All LLM agent calls. LLMs occasionally return invalid JSON or timeout.

**Trade-offs:**
- **Pro**: Resilient to transient failures, handles rate limits gracefully
- **Pro**: Parse errors (malformed JSON) can retry with clarified prompt
- **Con**: Adds latency on failures (but prevents simulation crash)

**Example:**
```python
def call_llm_with_retry(prompt: str, max_retries: int = 3) -> dict:
    for attempt in range(max_retries):
        try:
            response = llm_client.call(prompt)
            return parse_json(response)  # Raises on invalid JSON
        except (APIError, JSONDecodeError) as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt  # 1s, 2s, 4s
            logger.warning(f"LLM call failed: {e}, retrying in {wait}s")
            time.sleep(wait)
```

### Pattern 5: Parallel Monte Carlo with Joblib Loky

**What:** Run N simulations in parallel using `joblib.Parallel(backend='loky')`. Each simulation is independent (different random seed).

**When to use:** When N > 100 simulations. Below 100, overhead dominates; above 100, scales linearly.

**Trade-offs:**
- **Pro**: 85-90% efficiency on multi-core CPUs, 15-20% faster than multiprocessing.Pool
- **Pro**: Auto-recovery on worker crashes, better memory isolation
- **Con**: Pickling overhead for large CombatState (mitigate by keeping state small)

**Example:**
```python
from joblib import Parallel, delayed

def run_batch(encounter: Encounter, n_sims: int, parallel: bool = True) -> Results:
    seeds = range(n_sims)

    if parallel:
        outcomes = Parallel(n_jobs=-1, backend='loky')(
            delayed(run_combat)(encounter, seed=s) for s in seeds
        )
    else:
        outcomes = [run_combat(encounter, seed=s) for s in seeds]

    return aggregate_results(outcomes)
```

### Pattern 6: Reactive TUI with Textual Messages

**What:** Textual app uses message-passing for state updates. Widgets post messages (e.g., `SimulationProgress`), handlers react (update UI).

**When to use:** All TUI interactions. Textual is built around reactive message-passing.

**Trade-offs:**
- **Pro**: Decouples widgets from business logic, testable via message injection
- **Pro**: Async handlers enable non-blocking I/O (LLM calls don't freeze UI)
- **Con**: Indirection (harder to trace flow than direct calls)

**Example:**
```python
class CombatApp(App):
    def on_mount(self):
        self.run_worker(self.run_simulation(), exclusive=True)

    async def run_simulation(self):
        for i in range(100):
            result = await run_combat_async(encounter, seed=i)
            self.post_message(SimulationProgress(i + 1, result))

    def on_simulation_progress(self, msg: SimulationProgress):
        self.query_one(ProgressBar).update(msg.count)
```

## Data Flow

### Single Combat Flow

```
1. [CLI] Load encounter from .md
        ↓
2. [Simulator] Roll initiative → create CombatState
        ↓
3. [Turn Loop] For each creature in initiative order:
        ↓
4. [Agent] choose_action(state, creature_id) → Action
        ↓
5. [Rules] Execute action (attack roll, damage) → new CombatState
        ↓
6. [Logger] Write event to .md log
        ↓
7. [Victory Check] All enemies defeated? → Yes: return state | No: next turn
        ↓
8. [CLI] Display result (winner, rounds, final HP)
```

### Monte Carlo Batch Flow

```
1. [CLI] Parse args: encounter.md, n_sims=1000, parallel=True
        ↓
2. [Monte Carlo Runner] Generate seeds [0..999]
        ↓
3. [Joblib Parallel] Spawn workers (n_jobs=-1 = all cores)
        ↓
4. [Workers] Each runs run_combat(encounter, seed=i)
        ↓  (parallel execution, no shared state)
5. [Aggregator] Collect results → win rate, avg rounds, HP distributions
        ↓
6. [TUI or CLI] Display: "Party wins 73% of 1000 sims, avg 4.2 rounds"
```

### LLM Agent Decision Flow

```
1. [Simulator] Calls agent.choose_action(state, "goblin-1")
        ↓
2. [LLM Agent] Format state as prompt:
        "You are goblin-1. HP: 7/7, AC: 15, Position: (10, 5).
         Enemies: fighter (12, 3), wizard (15, 8).
         Choose action: {"action": "attack", "target": "fighter"}"
        ↓
3. [Retry Wrapper] Call LLM with exponential backoff
        ↓
4. [LLM API] Returns JSON: {"action": "attack", "target": "fighter"}
        ↓
5. [Parser] Validate JSON → Action object
        ↓
6. [Simulator] Execute action → apply damage → new state
```

### Resume from Log Flow

```
1. [CLI] run.py --resume saved_games/combat_2026-02-07.md
        ↓
2. [Markdown Parser] Read log, extract events
        ↓
3. [Event Replayer] For each event:
        state = apply_event(state, event)
        ↓
4. [Simulator] Continue from reconstructed state
        ↓
5. [Logger] Append new events to same .md file
```

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| **1-10 simulations** | Sequential execution, no parallelization overhead. Run in 5-30 seconds. |
| **100-1000 simulations** | Parallel with joblib Loky. Target 8 cores → 85% efficiency. 8 minutes for 1000 sims (user's requirement). |
| **10K+ simulations** | Consider distributed execution (Ray, Dask) for multi-machine. Cache LLM responses to avoid rate limits. |
| **Real-time TUI** | Use Textual async workers. Run simulations in background, post progress messages. UI remains responsive. |

### Scaling Priorities

1. **First bottleneck: LLM API rate limits**
   - **Problem**: OpenAI has 60 req/min limit. 1000 sims × 10 turns/sim = 10K calls → 2.5 hours.
   - **Solution**: Batch cache LLM responses by (state_hash, creature_id). Reuse across similar states. Or use heuristic agent for bulk sims, LLM for demo/analysis.

2. **Second bottleneck: Memory for large state objects**
   - **Problem**: 10K parallel workers with 50KB CombatState = 500MB RAM.
   - **Solution**: Use `joblib.Parallel(batch_size=100)` to chunk work. Or serialize state to SQLite, pass IDs instead of objects.

3. **Third bottleneck: Markdown log I/O**
   - **Problem**: Writing 1000 logs to disk is slow.
   - **Solution**: Only log on `--save` flag. For batch analysis, keep logs in memory, write summary stats to CSV.

## Anti-Patterns

### Anti-Pattern 1: Shared Mutable State in Parallel Simulations

**What people do:** Pass a global `CombatState` object to parallel workers, mutate it in place.

**Why it's wrong:** Race conditions. Two workers modify `creatures["goblin-1"].hp` simultaneously → corrupted state, non-deterministic results.

**Do this instead:** Use immutable state (frozen dataclasses). Each worker gets a deep copy or reconstructs state from encounter definition.

### Anti-Pattern 2: Blocking LLM Calls in TUI Main Thread

**What people do:** Call `llm_client.call(prompt)` directly in Textual message handler.

**Why it's wrong:** LLM calls take 1-5 seconds. UI freezes, can't cancel, poor UX.

**Do this instead:** Use `self.run_worker(call_llm_async())` in Textual. Worker runs in background, posts result via message.

### Anti-Pattern 3: Embedding D&D Rules in Agent Logic

**What people do:** LLM agent calculates damage, applies conditions, checks advantage.

**Why it's wrong:** Rules logic scattered across agents. Hard to test, violates Single Responsibility Principle.

**Do this instead:** Agents only choose actions (target, spell, movement). Simulator applies rules via `rules.py`. Pure separation: agents decide, simulator executes.

### Anti-Pattern 4: Parsing Markdown During Simulation

**What people do:** Read `creatures/goblin.md` on every combat start.

**Why it's wrong:** I/O is slow. For 1000 parallel sims, 1000 file reads → 10s overhead.

**Do this instead:** Load creatures once, pass in-memory Creature objects to simulator. Use `@lru_cache` on `load_creature(path)`.

### Anti-Pattern 5: Monolithic CombatState with All Encounter Data

**What people do:** Include terrain, weather, lore, DM notes in CombatState.

**Why it's wrong:** Large objects → pickling overhead in parallel execution, wasted memory.

**Do this instead:** Only store simulation-relevant data in CombatState (creatures, positions, HP, conditions). Metadata stays in Encounter object, not passed to workers.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **dnd5eapi.co** | HTTP GET with local JSON cache | Cache in `data/cache/monsters/{name}.json`. TTL = 30 days. Fallback to cached if API down. |
| **OpenAI API** | REST client with API key from env | Use `OPENAI_API_KEY` env var. Timeout = 30s. Retry on 429 (rate limit), 503 (server error). |
| **Ollama** | Local HTTP (localhost:11434) | No auth needed. Check health endpoint before combat. Fail fast if Ollama not running. |
| **Textual** | Import as library, run app.run() | No external service. Runs in same process as CLI. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| **Simulator ↔ Agent** | Function call: `agent.choose_action(state, creature_id)` → `Action` | Stateless. Simulator doesn't care if agent is heuristic or LLM. |
| **Simulator ↔ Logger** | Function call: `logger.log_event(event_dict)` | Append-only. Logger writes to open file handle, flushes on combat end. |
| **Monte Carlo ↔ Simulator** | Function call in worker: `run_combat(encounter, seed)` → `Outcome` | Parallel via joblib. No shared state. Each worker has own RNG seeded differently. |
| **TUI ↔ Simulator** | Async worker + message passing: `run_worker(simulate) → post_message(Progress)` | Non-blocking. TUI updates on messages, doesn't poll. |
| **Domain ↔ I/O** | Never direct. I/O calls domain functions, domain never imports I/O. | Dependency inversion. `creature.py` doesn't know about markdown, `markdown.py` knows about `Creature`. |

## Build Order Implications

Based on dependency analysis, recommended build order for roadmap:

### Phase 1: Core Domain (No Dependencies)
- `creature.py` (Creature, Action, StatBlock)
- `combat_state.py` (CombatState, initiative)
- `distance.py` (coordinate math, distance calc)
- `rules.py` (attack roll, damage, saves)
- `dice.py` (d20, advantage logic)

**Why first:** Pure Python, no external deps. Everything else depends on these. Fast unit tests.

### Phase 2: Agents (Depends on Domain)
- `base.py` (BaseAgent interface)
- `heuristic.py` (greedy agent)
- (defer `llm.py` to Phase 4)

**Why second:** Enables combat simulation without LLM complexity. Can test full combat loop with deterministic agent.

### Phase 3: Simulation (Depends on Domain + Agents)
- `simulator.py` (single combat runner)
- `victory.py` (win condition detection)
- `logger.py` (event logging)

**Why third:** Now have full combat simulation. Can run single combats, verify rules work.

### Phase 4: I/O (Depends on Domain)
- `markdown.py` (load creatures, write logs)
- `srd_api.py` (fetch monsters, cache)

**Why fourth:** Enables loading real creatures, not just test fixtures. Can run combats from .md files.

### Phase 5: Monte Carlo (Depends on Simulation)
- `monte_carlo.py` (parallel batch runner)

**Why fifth:** Requires working simulator. Adds parallelization complexity, so test thoroughly first.

### Phase 6: LLM Integration (Depends on Agents + Simulation)
- `llm.py` (LLMAgent)
- `retry.py` (retry logic)

**Why sixth:** Most complex integration. Requires API keys, error handling, prompt engineering. Do last to avoid blocking progress.

### Phase 7: TUI (Depends on Everything)
- `tui/app.py`, `tui/widgets/`, `tui/screens/`

**Why last:** UI is presentation layer. Needs working simulation + Monte Carlo to visualize. Can develop CLI first, add TUI later.

## Sources

**Turn-Based Combat Architecture:**
- [Outscal: Turn-Based Game Architecture](https://outscal.com/blog/turn-based-game-architecture) - State machine patterns, turn loop design
- [Tactical Grid Combat Simulator](https://github.com/Alva2084/Tactical-Grid-Combat-Simulator) - OOP design patterns (Command, Strategy, State, Observer)
- [A Turn-Based Game Loop by Bob Nystrom](https://journal.stuffwithstuff.com/2014/07/15/a-turn-based-game-loop/) - Staggered turn timing

**Entity Component System (ECS):**
- [Understanding Modern Game Engine Architecture with ECS](https://columbaengine.org/blog/ecs-architecture-with-ecs/) - Component composition over inheritance
- [Entity Component System - Wikipedia](https://en.wikipedia.org/wiki/Entity_component_system) - ECS fundamentals
- [Entity Component System FAQ](https://github.com/SanderMertens/ecs-faq) - Common ECS questions

**D&D Combat Simulators:**
- [GitHub: DndFight](https://github.com/AndHilton/DndFight) - Python combat simulator
- [GitHub: combatsim](https://github.com/lemonade512/combatsim) - D&D 5e combat simulator
- [TaRCoS: Combat Simulation for Tabletop RPGs](https://www.sbgames.org/proceedings2021/ComputacaoShort/218046.pdf) - Academic paper on TRPG simulation

**Monte Carlo Parallel Execution:**
- [Python Batch Processing with Joblib 2026](https://johal.in/python-batch-processing-with-joblib-parallel-loky-backends-scheduling-2026/) - Loky backend performance
- [Parallel Monte Carlo Simulation](https://ieeexplore.ieee.org/document/9150294/) - VaR calculation with Intel MIC
- [MATLAB: Improving Performance with Parallel Computing](https://www.mathworks.com/help/finance/improving-performance-of-monte-carlo-simulation-with-parallel-computing.html) - Parallel patterns

**State Management Patterns:**
- [State Machine Design Pattern in Python](https://www.linkedin.com/pulse/state-machine-design-pattern-concepts-examples-python-sajad-rahimi) - State pattern concepts
- [pytransitions](https://github.com/pytransitions/transitions) - Python state machine library
- [python-statemachine PyPI](https://pypi.org/project/python-statemachine/) - Expressive state machine API

**Agent-Based Modeling:**
- [Agent-based model - Wikipedia](https://en.wikipedia.org/wiki/Agent-based_model) - ABM fundamentals
- [2026 Guide to AI Agent Architecture](https://procreator.design/blog/guide-to-ai-agent-architecture-components/) - Modern agent patterns
- [7 Agentic AI Trends to Watch in 2026](https://machinelearningmastery.com/7-agentic-ai-trends-to-watch-in-2026/) - Behavioral telemetry, observability

**Pydantic vs Dataclasses:**
- [Type Safety in Python: Pydantic vs. Data Classes](https://www.speakeasy.com/blog/pydantic-vs-dataclasses) - When to use each
- [Pydantic Dataclasses Documentation](https://docs.pydantic.dev/latest/concepts/dataclasses/) - Official docs
- [Pydantic vs. Dataclass Comparison](https://medium.com/@nishthakukreti.01/pydantic-vs-dataclass-640ed78a5f7c) - Validation advantages

**LLM Integration & Retry Logic:**
- [Retries, Fallbacks, and Circuit Breakers in LLM Apps](https://portkey.ai/blog/retries-fallbacks-and-circuit-breakers-in-llm-apps/) - Production patterns
- [Mastering Retry Logic Agents 2025](https://sparkco.ai/blog/mastering-retry-logic-agents-a-deep-dive-into-2025-best-practices) - Adaptive retry strategies
- [Datadog Google LLM Observability 2026](https://www.infoq.com/news/2026/02/datadog-google-llm-observability/) - Tracing retry loops

**Textual TUI Architecture:**
- [Textual Tutorial](https://textual.textualize.io/tutorial/) - Official getting started
- [Real Python: Build Beautiful UIs in the Terminal](https://realpython.com/python-textual/) - Comprehensive guide
- [Textual Events and Messages](https://textual.textualize.io/guide/events/) - Message-passing patterns
- [8 TUI Patterns to Turn Scripts Into Apps](https://medium.com/@Nexumo_/8-tui-patterns-to-turn-python-scripts-into-apps-ce6f964d3b6f) - Common patterns

**Event Sourcing:**
- [Event Sourcing Pattern - Azure Architecture](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing) - Pattern overview
- [Event Sourcing by Martin Fowler](https://martinfowler.com/eaaDev/EventSourcing.html) - Canonical definition
- [Event-Driven Architecture on AWS: Event Sourcing](https://aws-samples.github.io/eda-on-aws/patterns/event-sourcing/) - Replay and recovery patterns
- [Event Sourcing and Event Replay](https://dev.to/boostercloud/event-sourcing-and-the-event-replay-mistery-4cn0) - Log replay mechanisms

---
*Architecture research for: D&D 5e Combat Simulator*
*Researched: 2026-02-07*
