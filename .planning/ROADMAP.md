# Roadmap: D&D 5e Combat Simulator

## Overview

This roadmap builds a terminal-based D&D 5e combat simulator with AI tactical agents through five phases. Phase 1 establishes core combat mechanics with deterministic agents. Phase 2 adds real creature data and Monte Carlo batch simulation. Phase 3 integrates LLM tactical decision-making. Phase 4 delivers a professional Textual TUI with advanced positioning mechanics. Phase 5 completes the system with spell slots, conditions, and state persistence. The result: a DM can define creatures, run 1000+ simulations, and know within 8 minutes whether an encounter is balanced.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation & Core Combat** - Combat mechanics work end-to-end with deterministic agents
- [x] **Phase 2: Creature Data & Monte Carlo Engine** - Batch simulations run on real SRD creatures with statistical confidence
- [ ] **Phase 3: LLM Tactical Agents** - LLM agents make tactical decisions with validation
- [ ] **Phase 4: Terminal UI & Advanced Combat** - Professional TUI shows live progress with advanced tactical mechanics
- [ ] **Phase 5: Spells, Conditions & Resume** - Full spell system with concentration and combat state persistence

## Phase Details

### Phase 1: Foundation & Core Combat
**Goal**: DM can run a single combat simulation with heuristic agents, see combat log with dice rolls, and verify basic D&D 5e mechanics work correctly.

**Depends on**: Nothing (first phase)

**Requirements**: COMBAT-01, COMBAT-02, COMBAT-03, COMBAT-04, COMBAT-05, COMBAT-06, COMBAT-07, COMBAT-08, COMBAT-09, COMBAT-10, COMBAT-11, COMBAT-12, GRID-01, GRID-02, GRID-03, AGENT-01, CREATURE-01, CREATURE-02, CLI-01

**Success Criteria** (what must be TRUE):
  1. DM can define two creatures in markdown files with stats and run combat between them
  2. Combat log shows initiative order, attack rolls with hit/miss, damage with types, and HP changes
  3. Creatures with resistance take half damage, creatures with immunity take zero damage
  4. Advantage/disadvantage resolves correctly as ternary state (multiple sources cancel completely)
  5. Combat ends when one side reaches 0 HP and winner is declared

**Plans**: 5 plans

Plans:
- [x] 01-01-PLAN.md -- Project setup, creature models, grid system, combat state, markdown parser
- [x] 01-02-PLAN.md -- Dice engine with advantage/disadvantage, rules engine (attacks, damage, saves, death saves)
- [x] 01-03-PLAN.md -- Heuristic agent, combat simulator loop, logger, CLI entry point
- [x] 01-04-PLAN.md -- Real D&D 5e combat mechanics and structured logging (gap closure)
- [x] 01-05-PLAN.md -- Initiative, turn loop, Multiattack, CLI wiring (gap closure)

### Phase 2: Creature Data & Monte Carlo Engine
**Goal**: DM can run 1000+ simulations using SRD monsters in under 10 minutes, see win percentages with confidence intervals, and difficulty ratings.

**Depends on**: Phase 1

**Requirements**: CREATURE-03, CREATURE-04, SIM-01, SIM-02, SIM-03, SIM-04, SIM-05, SIM-06, LOG-01

**Success Criteria** (what must be TRUE):
  1. DM can specify "goblin" and system auto-fetches stats from dnd5eapi.co without manual entry
  2. DM can override SRD stats in markdown file and system uses custom values
  3. Batch runner executes 1000 simulations and reports win rate (e.g., "Party wins: 73% +/- 4%")
  4. Results show average combat duration in rounds for wins vs losses
  5. Damage breakdown attributes damage to each creature and ability type
  6. Results map to D&D difficulty labels (Easy/Medium/Hard/Deadly)

**Plans**: 6 plans

Plans:
- [x] 02-01-PLAN.md -- SRD API integration and creature data transformation
- [x] 02-02-PLAN.md -- Statistical analysis utilities for confidence intervals and difficulty ratings
- [x] 02-03-PLAN.md -- Cache-first creature loader with local file precedence
- [x] 02-04-PLAN.md -- Monte Carlo simulation engine with progressive sampling
- [x] 02-05-PLAN.md -- CLI integration and batch runner with SRD creature support
- [x] 02-06-PLAN.md -- Report generation and difficulty rating output

### Phase 3: LLM Tactical Agents
**Goal**: LLM agents (local via Ollama or cloud via OpenRouter) make tactical combat decisions using strict output format, with validation that rejects illegal moves and falls back to heuristic agent on failure.

**Depends on**: Phase 2

**Requirements**: AGENT-02, AGENT-03, AGENT-04, AGENT-05, AGENT-06

**Success Criteria** (what must be TRUE):
  1. LLM agent via Ollama makes tactical decisions (move, attack, target selection) for creatures in combat
  2. LLM agent via OpenRouter (OpenAI-compatible API) works as alternative to local Ollama
  3. LLM output uses strict format (`<thinking>` block + ACTION/TARGET/MOVEMENT/BONUS/REACTION keys)
  4. Validation layer rejects illegal moves (out-of-range attacks, invalid targets) with error feedback
  5. On LLM parse failure or illegal move, system falls back to heuristic agent seamlessly
  6. Creature role archetypes (tank/striker/controller/support) influence LLM agent behavior via prompt

**Plans**: 3 plans

Plans:
- [ ] 03-01-PLAN.md -- TDD: LLM output parser and move legality validator
- [ ] 03-02-PLAN.md -- LLM providers (Ollama + OpenRouter) and prompt builder with role archetypes
- [ ] 03-03-PLAN.md -- LLM agent orchestration with circuit breaker, fallback, and CLI integration

### Phase 4: Terminal UI & Advanced Combat
**Goal**: DM sees professional terminal UI with live progress bars, scrollable combat logs, and colored result tables while advanced tactical mechanics (cover, AoE, opportunity attacks) work correctly.

**Depends on**: Phase 3

**Requirements**: TUI-01, TUI-02, TUI-03, TUI-04, GRID-04, GRID-05, GRID-06, TERRAIN-01

**Success Criteria** (what must be TRUE):
  1. TUI displays live progress bars during batch simulation showing X of N runs complete
  2. DM can scroll through combat log in TUI and see round-by-round positions and actions
  3. Result tables show win percentages, duration, damage breakdown with colored formatting
  4. Creature behind half-cover gets +2 AC and DEX saves, three-quarters cover gets +5
  5. Creature leaving melee reach triggers opportunity attack
  6. Fireball (sphere AoE) hits all creatures within grid radius

**Plans**: TBD

Plans:
- [ ] TBD during phase planning

### Phase 5: Spells, Conditions & Resume
**Goal**: Spellcasters manage spell slots across combat, concentration enforces one-spell-at-a-time rules, conditions affect combat correctly, and interrupted simulations can resume from checkpoint.

**Depends on**: Phase 4

**Requirements**: SPELL-01, SPELL-02, SPELL-03, LOG-02, LOG-03

**Success Criteria** (what must be TRUE):
  1. Spellcaster uses spell slot when casting, cannot cast when all slots depleted
  2. Casting second concentration spell automatically ends first (Bless -> Haste ends Bless)
  3. Taking damage while concentrating triggers CON save, failure ends spell
  4. Prone condition gives advantage to melee attacks, disadvantage to ranged attacks
  5. DM can resume interrupted 1000-run batch from checkpoint without losing progress

**Plans**: TBD

Plans:
- [ ] TBD during phase planning

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Core Combat | 5/5 | ✓ Complete | 2026-02-07 |
| 2. Creature Data & Monte Carlo Engine | 6/6 | ✓ Complete | 2026-02-08 |
| 3. LLM Tactical Agents | 0/3 | In progress | - |
| 4. Terminal UI & Advanced Combat | 0/TBD | Not started | - |
| 5. Spells, Conditions & Resume | 0/TBD | Not started | - |
