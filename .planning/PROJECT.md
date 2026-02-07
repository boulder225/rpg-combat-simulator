# D&D 5e Combat Simulator

## What This Is

A terminal-based D&D 5th Edition combat simulator that helps Dungeon Masters evaluate encounter balance through Monte Carlo batch simulations. Creatures are defined as markdown files with YAML frontmatter. Autonomous AI agents (heuristic or LLM-powered) make tactical decisions for all combatants. Run 20+ simulations in minutes to see win rates, damage breakdowns, and tactical patterns — then tweak and re-run until the encounter feels right.

## Core Value

A DM can sit down, define creatures in markdown files, run batch simulations, and know within 8 minutes whether an encounter is balanced, deadly, or a TPK — with enough tactical intelligence that the results feel realistic.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Creatures defined as .md files with YAML frontmatter (name, AC, HP, speed, initiative, team, position, stats) and structured action/spell blocks
- [ ] SRD 2014 monster lookup from dnd5eapi.co — auto-fetch standard creature stats, user overrides in .md files
- [ ] Coordinate-based positioning on implicit 5x5 ft grid (chess notation: A1, C4, F7)
- [ ] Manhattan distance calculation with optional diagonal cost (+5 ft)
- [ ] Cover system: half-cover and three-quarters cover from terrain/positioning, affecting AC and Dex saves
- [ ] Advantage/disadvantage from range, cover, conditions, pack tactics, flanking
- [ ] Full combat loop: initiative rolls, turn order, action/bonus action/reaction/movement per turn
- [ ] Conditions tracking: frightened, prone, grappled, concentration, etc. with auto-triggers
- [ ] Heuristic agent tier: fixed rule-based decision-making (fast, deterministic, good for large batch runs)
- [ ] LLM agent tier: full LLM decision per turn via Ollama (local) or OpenRouter (cloud), strict output format with `<thinking>` + uppercase action keys
- [ ] Monte Carlo batch runner: N simulations with random seeds, aggregate win/loss stats, damage breakdowns, average duration, cost tracking
- [ ] Append-only markdown combat log per simulation (rounds, positions, HP, actions, dice rolls, results)
- [ ] Resume interrupted simulations from saved combat log state
- [ ] Terrain defined in .md files (cover zones, difficult terrain, lair features)
- [ ] Full Textual TUI: live progress bars, scrollable combat log, colored result tables, interactive panels
- [ ] Verbose single-run mode: watch LLM thinking + rolls live, step through combat
- [ ] CLI interface: `python run.py --party ... --enemies ... --terrain ... --runs N --agent [heuristic|llm] --model ... --seed ...`

### Out of Scope

- Export summary / DM notes generation — nice-to-have for v2, copy-paste from terminal for now
- D&D 2024 rules (weapon masteries, new conditions) — SRD 2014 only
- ASCII/graphical map rendering — text coordinates are sufficient
- Web UI or GUI — terminal-only
- Character builder / level-up automation — creatures are manually authored .md files
- Real-time multiplayer — single-user DM tool
- Encounter XP/CR calculator — focus is on simulation, not math formulas

## Context

- **Rules source:** D&D 5e SRD 2014. Primary API: dnd5eapi.co (REST + GraphQL). Offline fallback: 5e-bits/5e-database JSON clone. LLMs are NOT used as rules sources (too error-prone on exact mechanics).
- **LLM agent format:** Rigid output format enforced — `<thinking>` block (120-150 words max) followed by ACTION/TARGET/MOVEMENT/BONUS/REACTION uppercase keys. Parsing must be strict.
- **LLM provider options:** Local via Ollama (qwen2.5:7b-instruct recommended, ~4.5-6GB quantized, 20-35 tok/s on M1). Cloud via OpenRouter (qwen/qwen2.5-coder-7b-instruct, OpenAI-compatible API, ~$0.01-0.03 per full simulation).
- **Creature file format:** Markdown with YAML frontmatter for stats, followed by structured action/spell blocks. See `.requirements/Combat Simulator.md` for example format.
- **Target workflow:** Create/edit .md creature files → run batch CLI command → read aggregated stats → tweak encounter → re-run. Full prep cycle: ~8 minutes.
- **Existing notes:** Detailed requirements and system prompt design in `.requirements/` directory.

## Constraints

- **Hardware**: Apple M1, 16GB unified RAM, ~23GB free disk — local LLM limited to 7B parameter models (no 14B+)
- **Rules**: SRD 2014 only — no homebrew rule systems, no 2024 revisions
- **Language**: Python — ecosystem has best D&D tooling, LLM client libraries, and Textual TUI framework
- **LLM latency**: 1-2 seconds per decision acceptable; full 20-run batch should complete in <40 minutes (LLM mode) or <2 minutes (heuristic mode)
- **Cost**: Cloud LLM runs via OpenRouter should stay under $0.50 for a 20-run batch
- **Data format**: All configuration and output as markdown files — no databases, no binary formats

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python as language | Best ecosystem for D&D APIs, LLM clients (openai lib), Textual TUI, rapid prototyping | -- Pending |
| Markdown files for all data | Fits DM workflow (Obsidian/text editors), human-readable, git-friendly, resume from logs | -- Pending |
| Chess-notation coordinates (A1) | Simple, familiar, avoids graphical complexity while maintaining spatial reasoning | -- Pending |
| Manhattan distance | Good enough approximation without full Euclidean grid; matches D&D's 5ft-square movement | -- Pending |
| Strict LLM output format | Prevents hallucinated abilities, enables reliable parsing, keeps agents honest to stat blocks | -- Pending |
| OpenRouter for cloud LLM | OpenAI-compatible API, cheap small models, avoids vendor lock-in | -- Pending |
| Textual for TUI | Rich terminal UI framework in Python, supports live updates, panels, tables | -- Pending |
| dnd5eapi.co as rules source | Free, well-maintained SRD API; avoids LLM rules hallucination | -- Pending |

---
*Last updated: 2026-02-07 after initialization*
