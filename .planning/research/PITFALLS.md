# Pitfalls Research: D&D 5e Combat Simulator

**Domain:** D&D 5e Combat Simulation with AI Tactical Agents
**Researched:** 2026-02-07
**Confidence:** MEDIUM (verified with multiple sources, domain-specific research)

## Critical Pitfalls

### Pitfall 1: Advantage/Disadvantage Implemented as Counters Instead of Ternary State

**What goes wrong:**
Implementing advantage/disadvantage as a counter (+1 for advantage, -1 for disadvantage) leads to incorrect game behavior. Projects may track "net advantage" (e.g., 2 sources of advantage + 1 disadvantage = net +1), but D&D 5e rules explicitly state advantage and disadvantage cancel completely regardless of count.

**Why it happens:**
The intuitive interpretation is that multiple sources should stack or cancel proportionally. The name "advantage" suggests a numeric bonus rather than a game state.

**How to avoid:**
Implement as a ternary state machine: `ADVANTAGE | NORMAL | DISADVANTAGE`. When adding a source, check: if any advantage source exists AND any disadvantage source exists, the state is NORMAL (complete cancellation). Otherwise, if any advantage source exists, state is ADVANTAGE. If any disadvantage source exists, state is DISADVANTAGE.

**Warning signs:**
- Code like `advantage_count - disadvantage_count`
- Tests that verify "double advantage" rolls 3d20
- Attack roll functions that accept numeric advantage parameters

**Phase to address:**
Phase 1 (Core Combat Engine) - This is fundamental to all combat rolls and must be correct from the start.

**Sources:**
- [D&D Beyond: Advantage & Disadvantage Forum](https://www.dndbeyond.com/forums/dungeons-dragons-discussion/rules-game-mechanics/56601-advantage-disadvantage)
- [GitHub Gist: Advantage/Disadvantage Summary](https://gist.github.com/OpenNingia/025ffcf269126a97503b34e243feee73)

---

### Pitfall 2: Concentration Tracking Without Automatic Cascading Termination

**What goes wrong:**
When a spellcaster casts a second concentration spell, the simulator fails to automatically end the first concentration spell. This leads to illegal game states where creatures have multiple concentration effects active simultaneously, dramatically skewing combat balance.

**Why it happens:**
Concentration seems like a "tag" on a spell rather than a mutually exclusive resource. Developers implement concentration checks (damage breaks concentration) but forget that casting a new concentration spell immediately ends the previous one.

**How to avoid:**
Track concentration as a single slot per creature: `creature.concentration = Optional[Spell]`. When casting a concentration spell, execute: `if creature.concentration: creature.concentration.end()` before `creature.concentration = new_spell`. Include this in the spell-casting validation logic, not just as a side effect.

**Warning signs:**
- Concentration tracked as a list/set of active spells
- Multiple buff spells (Bless, Haste, Hex) active on one caster
- No "previous concentration ended" log messages when casting

**Phase to address:**
Phase 2 (Spell System) - Concentration is central to spell balance and must be enforced before complex spell interactions.

**Sources:**
- [Onixshu: Mastering Concentration in D&D 5e](https://onixshu.com/blogs/articles/concentration-in-dnd-5e)
- [D&D Beyond: How Concentration Works](https://www.dndbeyond.com/posts/1224-how-concentration-works-in-dungeons-dragons)

---

### Pitfall 3: LLM Agents Hallucinating Abilities or Making Illegal Moves

**What goes wrong:**
LLM tactical agents invent abilities creatures don't have ("the goblin casts Fireball"), make illegal moves (moving twice, casting while silenced), or hallucinate tactical advantages that don't exist in the current game state. In Chess.com experiments, ChatGPT repeatedly made illegal moves including moving pawns horizontally to capture and forgetting piece positions.

**Why it happens:**
LLMs generate plausible-sounding text based on training data patterns, not rule-based reasoning. An LLM "knows" goblins are associated with D&D combat and Fireball is a D&D spell, so it may confidently assert a goblin can cast Fireball without checking the creature's actual spell list.

**How to avoid:**
Implement a validation layer that treats LLM output as suggestions, not commands. Parse LLM responses for intended actions, then validate against: (1) creature's actual abilities from statblock, (2) action economy (only one action per turn), (3) current conditions (silenced = no verbal spells), (4) resource availability (spell slots, limited-use abilities). Reject and re-prompt on validation failure with specific error feedback.

**Warning signs:**
- Direct execution of LLM text output as actions
- No schema validation on LLM responses
- Missing "available actions" context in prompts
- Simulation logs with impossible ability combinations

**Phase to address:**
Phase 4 (AI Tactical Agents) - The validation layer must be built before any LLM integration.

**Sources:**
- [Timeplus: AI Chess Hallucination Detection](https://www.timeplus.com/post/ai-chess-hallucination-detection)
- [Medium: How I Built an LLM-Based Game](https://medium.com/data-science/how-i-built-an-llm-based-game-from-scratch-86ac55ec7a10)
- [CloudBabble: Preventing Hallucinations in Agentic AI](https://www.cloudbabble.co.uk/2025-12-06-preventing-agent-hallucinations-defence-in-depth/)

---

### Pitfall 4: Insufficient Monte Carlo Sample Size Leading to Statistical Noise

**What goes wrong:**
Running too few combat simulations (e.g., 100 runs) produces unreliable balance assessments. Small sample sizes amplify variance from lucky/unlucky dice rolls, making it impossible to distinguish a 60% win rate (moderately balanced) from a 70% win rate (severely unbalanced). The 8-minute runtime constraint forces a tradeoff between sample size and combat complexity.

**Why it happens:**
Developers test with small sample sizes (10-50 runs) during development, see results that "look reasonable," and ship without validating statistical significance. Monte Carlo literature suggests "a few hundred" iterations, but this is context-dependent.

**How to avoid:**
Calculate required sample size based on desired confidence interval. For encounter balance (detecting win rate differences of ±5%), you need approximately 1,500-2,000 simulations per encounter at 95% confidence. Implement progressive sampling: run 500 simulations, check if confidence interval is tight enough, continue if needed. Display confidence intervals in results to surface uncertainty.

**Warning signs:**
- Hard-coded `num_simulations = 100`
- Results change significantly when re-run with same parameters
- No confidence intervals reported
- Claims of "perfectly balanced" (exactly 50% win rate)

**Phase to address:**
Phase 5 (Monte Carlo Engine) - Statistical validity is the entire value proposition of the batch simulator.

**Sources:**
- [Medium: Sample Size Estimation and Monte Carlo](https://medium.com/@sorellanamontini/sample-size-estimation-and-monte-carlo-simulations-e2ff4783664a)
- [Yeng Miller-Chang: D&D and Monte Carlo Simulation](https://www.yengmillerchang.com/post/standard-setting-or-dice-rolls-in-d-d/)
- [GitHub: Monte Carlo D&D Combat](https://github.com/andrei-gorbatch/monte_carlo)

---

### Pitfall 5: Resume from Markdown Logs Without State Checkpointing

**What goes wrong:**
Attempting to reconstruct combat state purely from markdown logs fails when logs are lossy (don't capture internal state like random seeds, queued reactions, or AI decision rationale). A "resumed" combat diverges from the original because hidden state wasn't preserved.

**Why it happens:**
Markdown logs are designed for human readability (DM review), not machine reconstruction. Developers assume "if we log all actions, we can replay them," forgetting that stochastic processes (dice rolls, AI decisions) won't reproduce identically without seed preservation.

**How to avoid:**
Separate concerns: human-readable markdown logs (for DM) and binary checkpoints (for resume). Checkpoints must include: (1) complete creature state (HP, conditions, spell slots, concentration), (2) combat state (round, turn, initiative order), (3) random seed, (4) queued effects (end-of-turn triggers), (5) AI decision history. Markdown logs are derived from checkpoints, not the source of truth.

**Warning signs:**
- Markdown parsing code in simulation resume logic
- No serialization of RNG state
- "Resume from turn X" without checkpoint file
- Inability to reproduce exact combat results

**Phase to address:**
Phase 6 (State Persistence) - Must be designed before markdown logging, as logs should be checkpoint exports.

**Sources:**
- [GROMACS: Managing Simulations](https://manual.gromacs.org/current/user-guide/managing-simulations.html)
- [DEV: LangGraph Checkpoint-Based State Replay](https://dev.to/sreeni5018/debugging-non-deterministic-llm-agents-implementing-checkpoint-based-state-replay-with-langgraph-5171)

---

### Pitfall 6: Dimensionless Combat Model Ignoring Movement and Positioning

**What goes wrong:**
Simulating combat without a grid or distance model makes it impossible to correctly implement opportunity attacks, reach weapons, ranged attack disadvantage, area-of-effect spell targeting, cover, and movement-based tactics (kiting, flanking). Existing D&D simulators often assume "everyone borders everyone" because tactical positioning is too complex to model, but this dramatically changes combat balance.

**Why it happens:**
Adding a spatial dimension increases complexity: pathfinding, line of sight, optimal positioning AI. For batch Monte Carlo (thousands of combats), spatial simulation seems prohibitively expensive. Developers rationalize "we'll approximate positioning effects" but underestimate how much tactics matter.

**How to avoid:**
Accept that a dimensionless model is a simplified abstraction with known limitations. Document what's NOT modeled (opportunity attacks, reach, cover, AoE positioning) and advise users that results are approximate. Alternatively, implement a minimal spatial model: discrete zones (melee range, short range, long range) rather than full grid. AI agents choose zones, enabling some tactical decisions without full pathfinding.

**Warning signs:**
- Opportunity attacks implemented as "always triggers on move"
- Ranged weapons have no disadvantage in melee
- Area spells affect predetermined targets without positioning
- AI never uses movement strategically (Dash, Disengage)

**Phase to address:**
Phase 1 (Core Combat Engine) - Spatial model architecture decision must be made before building action resolution, as it affects every combat mechanic.

**Sources:**
- [GitHub: matteoferla/DnD-battler](https://github.com/matteoferla/DnD-battler) (documents dimensionless model limitations)
- [Sly Flourish: D&D 5e Gotchas](https://slyflourish.com/5e_gotchas.html)

---

### Pitfall 7: SRD API Data Mapping Mismatches with Internal Creature Model

**What goes wrong:**
SRD API creature data uses different naming conventions, structures, and units than your internal model. For example, API returns `hit_dice: "2d6"` (string), but your model expects `hit_die_count: 2, hit_die_type: 6` (integers). Naive mapping causes runtime errors, data loss (special abilities missing), or incorrect stats (proficiency bonuses calculated wrong).

**Why it happens:**
Developers write a quick mapping function during prototyping, test with one creature (goblin), and assume it works for all creatures. Edge cases (creatures with multiple attack types, legendary actions, lair actions, spellcasting) break the mapping in production.

**How to avoid:**
Use schema validation (Pydantic models) with explicit mappings. Define an `APICreature` schema matching SRD API structure and a `SimulationCreature` schema for internal use. Write a tested adapter layer that handles: (1) parsing dice notation strings, (2) mapping action types (melee/ranged/spell), (3) extracting special traits (Magic Resistance, Pack Tactics), (4) handling optional fields (legendary actions may be absent). Test with diverse creature types: spellcasters, legendary creatures, swarms.

**Warning signs:**
- Mapping code is < 50 lines (too simple for real complexity)
- No schema validation on API responses
- Tests only use basic humanoid creatures
- Crashes when loading dragons, spellcasters, or aberrations

**Phase to address:**
Phase 3 (Creature Data Integration) - The adapter layer is the foundation for creature variety.

**Sources:**
- [GitHub: 5e-bits/5e-srd-api](https://github.com/5e-bits/5e-srd-api)
- [Open5e API: Creature Instance](https://api.open5e.com/v2/creatures/srd_goblin/?depth=1)
- [D&D 5e API Documentation](https://www.dnd5eapi.co/)

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hard-code creature stats instead of loading from SRD | Fast prototyping, no API dependencies | Unmaintainable, no creature variety, can't update stats | Only for proof-of-concept demo (< 1 week) |
| Skip concentration validation | Fewer edge cases to handle | Incorrect simulation results, unreliable balance assessments | Never - core rule for spell balance |
| Use synchronous LLM calls in TUI event loop | Simple code, no async complexity | TUI freezes during AI decisions, poor UX | Never - 3-5s LLM latency will block UI |
| Ignore opportunity attacks entirely | Simpler combat model, faster simulation | Overvalues ranged attackers, undervalues defender tactics | If documented and users accept limitation |
| Single-threaded Monte Carlo simulation | Simple implementation, no race conditions | Can't meet 8-minute target on large encounters | Only if encounter size is small (< 4v4) |
| Store simulation results in memory only | No database complexity | Can't analyze historical trends, data lost on crash | Early phases; must add persistence by MVP |

---

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Ollama local LLM | Assuming unlimited context window, sending entire combat log | Use sliding window (last 5 turns) or summarization. 7B models typically have 2k-4k token limits. |
| OpenRouter cloud LLM | No timeout handling, blocking on slow API responses | Set aggressive timeouts (5-10s), implement retry with exponential backoff, fallback to heuristic agent on failure. |
| SRD 5e API | Fetching creature data synchronously on every simulation run | Cache creature data locally (SQLite), refresh periodically (daily), only fetch on cache miss. |
| Textual TUI updates | Calling UI update methods from worker threads | Use `App.call_from_thread()` to marshal updates to main thread. Direct calls cause race conditions. |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Deep-copying entire combat state each round | Simulations slow down with long combats (10+ rounds) | Use copy-on-write for creature stats, only clone changed attributes | > 8 creatures or > 12 rounds |
| LLM API call per creature per turn | 3-5 second per turn with 6 creatures = 30s/round = 5+ minutes for 10-round combat | Batch creature decisions into single prompt "what does party do?" or use async concurrent calls | > 4 creatures with LLM agents |
| Regenerating Textual UI widgets on every state change | Stuttering animations, missed input events | Use reactive attributes, only update changed widgets, leverage Textual's partial diffing | > 10 Hz update rate or complex widgets |
| Logging every dice roll to markdown | Multi-MB log files, slow I/O, disk space issues | Log at action level (attack results), not individual dice rolls, rotate logs per simulation batch | > 1000 simulation runs |
| Loading entire creature database into memory | High memory usage, slow startup | Lazy-load creatures on demand, use SQLite for querying, index by name/CR | > 500 creatures in database |

---

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Executing LLM-generated code (eval/exec on agent output) | Remote code execution, data exfiltration | Never eval LLM output. Parse structured responses (JSON schema), validate actions against whitelist. |
| Loading untrusted creature YAML without sanitization | YAML deserialization attacks (arbitrary object instantiation) | Use safe YAML loaders (yaml.safe_load), validate against schema, reject unknown fields. |
| Storing OpenRouter API keys in code/logs | API key theft, unauthorized usage, cost overruns | Use environment variables, never log API keys, implement rate limiting per user. |
| Allowing user-provided markdown logs to overwrite system files | Path traversal, file overwrite | Validate file paths, use safe filename sanitization, write to restricted directory only. |

---

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No progress indicator during Monte Carlo batch | User thinks app crashed, kills process prematurely | Show live progress: "Run 342/2000 (17%), Round 3, Goblins winning 58%". Update every 100ms. |
| Displaying raw JSON/YAML errors from creature parsing | User confused, can't diagnose issue | Parse error, show: "Goblin.md line 12: hit_dice must be XdY format (got: 'lots')". |
| No explanation of statistical confidence | User trusts 52% win rate from 20 runs as meaningful | Always show: "Win rate: 52% ± 8% (95% CI, n=500)". Flag if CI too wide. |
| Showing every simulation log to user | Information overload, can't identify patterns | Show summary stats, allow drill-down to individual runs by outcome (narrow win, TPK, etc.). |
| AI agent makes tactically terrible moves without explanation | User loses trust in simulator validity | Log AI reasoning: "Goblin archer stays in melee (45% hit chance) instead of Disengaging (would be 60% next turn)". Shows limitations. |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Spell system:** Often missing concentration enforcement — verify second concentration spell ends first spell.
- [ ] **Attack resolution:** Often missing advantage/disadvantage cancellation — verify multiple sources cancel completely.
- [ ] **Opportunity attacks:** Often missing forced movement exemption — verify shove/pull effects don't trigger OAs.
- [ ] **Conditions:** Often missing condition interactions (restrained = disadvantage on Dex saves) — verify all condition effects.
- [ ] **AI validation:** Often missing illegal action detection — verify LLM can't move twice or cast without spell slots.
- [ ] **Monte Carlo results:** Often missing confidence intervals — verify statistical significance is reported.
- [ ] **Resume from checkpoint:** Often missing RNG seed preservation — verify resumed combat matches original exactly.
- [ ] **LLM integration:** Often missing timeout/fallback — verify graceful degradation when API is slow/down.
- [ ] **Creature loading:** Often missing validation — verify corrupted YAML produces helpful error, not crash.
- [ ] **TUI live updates:** Often missing thread-safety — verify UI updates from background workers don't corrupt state.

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Advantage/disadvantage as counters | MEDIUM | Refactor to enum/ternary state. Requires updating all attack roll call sites, moderate test updates. |
| Missing concentration enforcement | HIGH | Requires spell system rewrite. Must add concentration slot, audit all spells, update AI agents to track. |
| LLM hallucination in production | LOW | Add validation layer around existing LLM calls. Can be done incrementally per action type. |
| Insufficient Monte Carlo samples | LOW | Increase `num_simulations` parameter, possibly reduce per-combat complexity to meet time budget. |
| No state checkpointing | HIGH | Requires new serialization system. Can't retrofit onto markdown logs; must design checkpoint format. |
| Dimensionless combat model | VERY HIGH | Fundamental architecture change. Requires spatial model, pathfinding, AI rewrite. Consider out-of-scope. |
| SRD mapping bugs | MEDIUM | Fix adapter layer, add schema validation. Requires regression testing with diverse creatures. |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Advantage/disadvantage counters | Phase 1: Core Combat Engine | Unit test: apply 2x advantage + 1x disadvantage = NORMAL state, rolls 1d20. |
| Concentration stacking | Phase 2: Spell System | Integration test: Bless → Haste on same caster ends Bless, only Haste active. |
| LLM hallucinations | Phase 4: AI Tactical Agents | Validation test: LLM suggests "cast Fireball" for goblin, rejected (not in spell list). |
| Insufficient samples | Phase 5: Monte Carlo Engine | Statistical test: 2000 runs produce ±5% confidence interval at 95% confidence. |
| No checkpointing | Phase 6: State Persistence | Resume test: Checkpoint at round 5, resume, verify exact same outcome as non-resumed combat. |
| Dimensionless model | Phase 1: Core Combat Engine (architecture decision) | Design review: Document spatial model (dimensionless/zones/grid), implications for rules. |
| SRD mapping bugs | Phase 3: Creature Data Integration | Creature diversity test: Load 50 random creatures, verify all parse correctly and stats are valid. |
| Textual TUI threading | Phase 7: TUI Development | Concurrency test: Run 10 concurrent simulations with live updates, verify no race conditions or freezes. |
| Ollama memory constraints | Phase 4: AI Tactical Agents | Performance test: 7B Q4_K_M model on M1 Mac generates responses < 3s (30+ tok/s). |
| Opportunity attack errors | Phase 1: Core Combat Engine | Rules test: Forced movement (shove) doesn't trigger OA, voluntary movement does. |

---

## Sources

**D&D 5e Rules Implementation:**
- [GitHub: matteoferla/DnD-battler](https://github.com/matteoferla/DnD-battler) - Dimensionless model limitations
- [D&D Beyond: Advantage & Disadvantage Forum](https://www.dndbeyond.com/forums/dungeons-dragons-discussion/rules-game-mechanics/56601-advantage-disadvantage)
- [GitHub Gist: Advantage/Disadvantage Summary](https://gist.github.com/OpenNingia/025ffcf269126a97503b34e243feee73)
- [Onixshu: Mastering Concentration in D&D 5e](https://onixshu.com/blogs/articles/concentration-in-dnd-5e)
- [D&D Beyond: How Concentration Works](https://www.dndbeyond.com/posts/1224-how-concentration-works-in-dungeons-dragons)
- [Nerdarchy: TOP 10 Common D&D 5e Mistakes](https://nerdarchy.com/the-top-10-most-common-mistakes-made-in-dd-5e/)
- [Wargamer: Opportunity Attack 5e Rules](https://www.wargamer.com/dnd/opportunity-attack-5e)
- [Sly Flourish: D&D 5e Gotchas](https://slyflourish.com/5e_gotchas.html)

**LLM Agent Hallucinations:**
- [Timeplus: AI Chess Hallucination Detection](https://www.timeplus.com/post/ai-chess-hallucination-detection)
- [Medium: How I Built an LLM-Based Game](https://medium.com/data-science/how-i-built-an-llm-based-game-from-scratch-86ac55ec7a10)
- [CloudBabble: Preventing Hallucinations in Agentic AI](https://www.cloudbabble.co.uk/2025-12-06-preventing-agent-hallucinations-defence-in-depth/)
- [Appsmith: De-hallucinate AI Agents](https://www.appsmith.com/blog/de-hallucinate-ai-agents)

**Monte Carlo Simulation:**
- [Medium: Sample Size Estimation and Monte Carlo](https://medium.com/@sorellanamontini/sample-size-estimation-and-monte-carlo-simulations-e2ff4783664a)
- [Yeng Miller-Chang: D&D and Monte Carlo Simulation](https://www.yengmillerchang.com/post/standard-setting-or-dice-rolls-in-d-d/)
- [GitHub: andrei-gorbatch/monte_carlo](https://github.com/andrei-gorbatch/monte_carlo)

**State Persistence:**
- [GROMACS: Managing Simulations](https://manual.gromacs.org/current/user-guide/managing-simulations.html)
- [DEV: LangGraph Checkpoint-Based State Replay](https://dev.to/sreeni5018/debugging-non-deterministic-llm-agents-implementing-checkpoint-based-state-replay-with-langgraph-5171)

**SRD API Integration:**
- [GitHub: 5e-bits/5e-srd-api](https://github.com/5e-bits/5e-srd-api)
- [D&D 5e API Documentation](https://www.dnd5eapi.co/)
- [Open5e API: Creature Instance](https://api.open5e.com/v2/creatures/srd_goblin/?depth=1)

**Python Local LLM Performance:**
- [Greg's Tech Notes: Apple Silicon LLM Limitations](https://stencel.io/posts/apple-silicon-limitations-with-usage-on-local-llm%20.html)
- [ML Journey: Run LLMs Locally on Mac M1/M2/M3](https://mljourney.com/how-to-run-llms-locally-on-mac-m1-m2-m3-complete-guide/)
- [Medium: Run LLM on M1 MacBook Air with 16GB](https://medium.com/@dlaytonj2/can-you-run-a-large-language-model-llm-locally-on-an-m1-macbook-air-with-only-16-gb-of-memory-cd9741af27bb)

**Textual TUI Performance:**
- [Textual: Workers Guide](https://textual.textualize.io/guide/workers/)
- [Textual: No-async Async with Python](https://textual.textualize.io/blog/2023/03/15/no-async-async-with-python/)
- [Textual: The Heisenbug Lurking in Async Code](https://textual.textualize.io/blog/2023/02/11/the-heisenbug-lurking-in-your-async-code/)
- [Textual: Algorithms for High Performance Terminal Apps](https://textual.textualize.io/blog/2024/12/12/algorithms-for-high-performance-terminal-apps/)

**Tactical AI Design:**
- [GeeksforGeeks: Integrating Game Theory and AI](https://www.geeksforgeeks.org/artificial-intelligence/integrating-game-theory-and-artificial-intelligence-strategies-for-complex-decision-making/)
- [arXiv: Combining Strategic Learning and Tactical Search in RTS Games](https://arxiv.org/pdf/1709.03480)

---

*Pitfalls research for: D&D 5e Combat Simulator with AI Tactical Agents*
*Researched: 2026-02-07*
