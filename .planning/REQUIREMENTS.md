# Requirements: D&D 5e Combat Simulator

**Defined:** 2026-02-07
**Core Value:** A DM can define creatures in markdown, run batch Monte Carlo simulations with AI tactical agents, and know within 8 minutes whether an encounter is balanced.

## v1 Requirements

### Core Combat Engine

- [ ] **COMBAT-01**: DM can resolve attack rolls (d20 + modifier vs AC) with hit/miss determination
- [ ] **COMBAT-02**: DM can see damage rolls with damage types (slashing, piercing, fire, cold, etc.)
- [ ] **COMBAT-03**: Creatures apply damage resistances, immunities, and vulnerabilities automatically
- [ ] **COMBAT-04**: Combat begins with initiative rolls (d20 + modifier) determining turn order
- [ ] **COMBAT-05**: Advantage/disadvantage resolved as ternary state (multiple sources cancel, don't stack)
- [ ] **COMBAT-06**: Creatures execute multiattack (multiple attacks per turn per stat block)
- [ ] **COMBAT-07**: HP tracked per creature (current/max) with damage and healing applied correctly
- [ ] **COMBAT-08**: Combat ends when one side is eliminated (0 HP creatures removed from combat)
- [ ] **COMBAT-09**: Creatures spend movement per turn limited by their speed stat
- [ ] **COMBAT-10**: Saving throws resolved (DEX, CON, WIS, etc.) against spell/ability DCs
- [ ] **COMBAT-11**: PCs at 0 HP make death saving throws (3 successes = stable, 3 failures = dead)
- [ ] **COMBAT-12**: Healing actions (Healing Word, Cure Wounds, potions) restore HP mid-combat

### Grid & Positioning

- [ ] **GRID-01**: Creatures positioned on chess-notation coordinate grid (A1, C4, F7) with 5ft squares
- [ ] **GRID-02**: Distance between creatures calculated using Manhattan distance
- [ ] **GRID-03**: Per-turn movement budget tracked and enforced by creature speed
- [ ] **GRID-04**: Half-cover (+2 AC/DEX saves) and three-quarters cover (+5) from terrain zones
- [ ] **GRID-05**: Opportunity attacks triggered when creature leaves another's melee reach
- [ ] **GRID-06**: Area-of-effect abilities (cone, sphere, line) hit creatures based on grid positions

### Creature Data

- [ ] **CREATURE-01**: Creatures defined as .md files with YAML frontmatter (name, AC, HP, speed, initiative bonus, team, position, ability scores)
- [ ] **CREATURE-02**: Action blocks structured in .md files (attack bonus, damage dice, reach/range, description)
- [ ] **CREATURE-03**: SRD 2014 monsters auto-fetched from dnd5eapi.co API
- [ ] **CREATURE-04**: Custom homebrew creatures supported via user-authored .md files

### Agent System

- [ ] **AGENT-01**: Heuristic agent makes rule-based decisions (target by threat/HP, use best action, position tactically)
- [ ] **AGENT-02**: LLM agent makes decisions via Ollama (local, e.g. qwen2.5:7b-instruct)
- [ ] **AGENT-03**: LLM agent makes decisions via OpenRouter (cloud, OpenAI-compatible API)
- [ ] **AGENT-04**: LLM output uses strict format (`<thinking>` block + ACTION/TARGET/MOVEMENT/BONUS/REACTION keys)
- [ ] **AGENT-05**: Validation layer rejects illegal LLM moves and falls back to heuristic on parse failure
- [ ] **AGENT-06**: Creature role archetypes (tank/striker/controller/support) influence agent behavior

### Simulation Engine

- [ ] **SIM-01**: Monte Carlo batch runner executes N simulations with configurable random seeds
- [ ] **SIM-02**: Aggregate win/loss percentage reported across all runs
- [ ] **SIM-03**: Average combat duration (rounds) reported per outcome
- [ ] **SIM-04**: Damage breakdown by source creature and ability type
- [ ] **SIM-05**: OpenRouter API cost tracked and displayed per batch
- [ ] **SIM-06**: Results mapped to D&D difficulty ratings (Easy/Medium/Hard/Deadly)

### Combat Logging & Resume

- [ ] **LOG-01**: Append-only markdown combat log records every round (positions, HP, actions, dice rolls)
- [ ] **LOG-02**: Simulations can be resumed from saved combat log / checkpoint state
- [ ] **LOG-03**: Verbose single-run mode displays LLM thinking and dice rolls live

### Terminal UI

- [ ] **TUI-01**: Textual TUI shows live progress bars during batch simulation
- [ ] **TUI-02**: Scrollable combat log viewer in TUI
- [ ] **TUI-03**: Colored result tables display Monte Carlo statistics
- [ ] **TUI-04**: Interactive panels with keyboard navigation

### Spells & Conditions

- [ ] **SPELL-01**: Spell slot tracking with depletion across combat rounds
- [ ] **SPELL-02**: Concentration enforced (one spell at a time, CON save on damage)
- [ ] **SPELL-03**: Conditions (frightened, prone, stunned, grappled) tracked with duration and roll effects

### Terrain & CLI

- [ ] **TERRAIN-01**: Terrain defined in .md files (cover zones, arena features)
- [ ] **CLI-01**: CLI entry point: `python run.py --party ... --enemies ... --terrain ... --runs N --agent [heuristic|llm] --model ... --seed ...`

## v2 Requirements

### Advanced Simulation

- **ADV-01**: Sensitivity analysis ("What if boss gets +2 AC?" — shows balance tipping points)
- **ADV-02**: Action economy visualization (shows why 4 weak creatures beat 1 strong creature)
- **ADV-03**: Multi-encounter adventuring day simulation (resource depletion across encounters)

### Advanced Combat

- **ADV-04**: Legendary actions and legendary resistances for high-CR creatures
- **ADV-05**: Lair actions triggered on initiative count 20
- **ADV-06**: Difficult terrain zones (half movement cost)
- **ADV-07**: Flanking rules (optional rule, advantage on flanked targets)

### Export & Polish

- **ADV-08**: Export summary to DM session prep notes (markdown output)
- **ADV-09**: Custom AI prompt templates for LLM agents
- **ADV-10**: Export results to PDF/HTML reports
- **ADV-11**: D&D 2024 rules support (weapon masteries, new conditions)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time 3D visualization | Massive scope creep, breaks terminal focus, slow to render |
| Web UI or GUI | Terminal-native is the differentiator, not a limitation |
| Multiplayer/shared sessions | Single-user DM prep tool, networking adds huge complexity |
| D&D Beyond character sheet import | Proprietary format, legal gray area, markdown is faster |
| Full non-SRD spell book | SRD covers 90%+ of combat spells, full book is months of work |
| "Perfect" AI that never misses optimal play | Agents model creature intelligence, not chess-engine optimization |
| Real-time encounter builder UI | Markdown in preferred editor is faster for target audience |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| COMBAT-01 | Phase 1 | Complete |
| COMBAT-02 | Phase 1 | Complete |
| COMBAT-03 | Phase 1 | Complete |
| COMBAT-04 | Phase 1 | Complete |
| COMBAT-05 | Phase 1 | Complete |
| COMBAT-06 | Phase 1 | Complete |
| COMBAT-07 | Phase 1 | Complete |
| COMBAT-08 | Phase 1 | Complete |
| COMBAT-09 | Phase 1 | Complete |
| COMBAT-10 | Phase 1 | Complete |
| COMBAT-11 | Phase 1 | Complete |
| COMBAT-12 | Phase 1 | Partial |
| GRID-01 | Phase 1 | Complete |
| GRID-02 | Phase 1 | Complete |
| GRID-03 | Phase 1 | Complete |
| GRID-04 | Phase 4 | Pending |
| GRID-05 | Phase 4 | Pending |
| GRID-06 | Phase 4 | Pending |
| CREATURE-01 | Phase 1 | Complete |
| CREATURE-02 | Phase 1 | Complete |
| CREATURE-03 | Phase 2 | Complete |
| CREATURE-04 | Phase 2 | Complete |
| AGENT-01 | Phase 1 | Complete |
| AGENT-02 | Phase 3 | Pending |
| AGENT-03 | Phase 3 | Pending |
| AGENT-04 | Phase 3 | Pending |
| AGENT-05 | Phase 3 | Pending |
| AGENT-06 | Phase 3 | Pending |
| SIM-01 | Phase 2 | Complete |
| SIM-02 | Phase 2 | Complete |
| SIM-03 | Phase 2 | Complete |
| SIM-04 | Phase 2 | Complete |
| SIM-05 | Phase 2 | Pending |
| SIM-06 | Phase 2 | Complete |
| LOG-01 | Phase 2 | Complete |
| LOG-02 | Phase 5 | Pending |
| LOG-03 | Phase 5 | Pending |
| TUI-01 | Phase 4 | Pending |
| TUI-02 | Phase 4 | Pending |
| TUI-03 | Phase 4 | Pending |
| TUI-04 | Phase 4 | Pending |
| SPELL-01 | Phase 5 | Pending |
| SPELL-02 | Phase 5 | Pending |
| SPELL-03 | Phase 5 | Pending |
| TERRAIN-01 | Phase 4 | Pending |
| CLI-01 | Phase 1 | Complete |

**Coverage:**
- v1 requirements: 46 total
- Mapped to phases: 46
- Unmapped: 0

**Phase Distribution:**
- Phase 1: 19 requirements (Foundation & Core Combat)
- Phase 2: 9 requirements (Creature Data & Monte Carlo Engine)
- Phase 3: 5 requirements (LLM Tactical Agents)
- Phase 4: 8 requirements (Terminal UI & Advanced Combat)
- Phase 5: 5 requirements (Spells, Conditions & Resume)

---
*Requirements defined: 2026-02-07*
*Last updated: 2026-02-07 after roadmap creation*
