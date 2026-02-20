# D&D 5e Combat Simulator

A terminal-based D&D 5th Edition combat simulator that helps Dungeon Masters evaluate encounter balance through Monte Carlo batch simulations.

## What It Does

- **Define creatures** as markdown files with YAML frontmatter (stats, actions, spells)
- **Run batch simulations** — 20+ runs in minutes to see win rates, damage breakdowns, and tactical patterns
- **AI-driven tactics** — heuristic or LLM-powered agents make decisions for all combatants
- **Fast feedback** — tweak encounters and re-run until the balance feels right

## Command

```bash
python run.py --party CREATURE [CREATURE ...] --enemies CREATURE [CREATURE ...] [options]
```

Use `uv run python run.py` if you manage the project with [uv](https://docs.astral.sh/uv/).

## Help

```bash
python run.py --help
```

## Options

| Option | Description |
|--------|-------------|
| `--party CREATURE [CREATURE ...]` | Party creature files or SRD names (e.g. `fighter`, `rogue.md`) |
| `--enemies CREATURE [CREATURE ...]` | Enemy creature files or SRD names (e.g. `goblin`, `orc.md`) |
| `--runs N` | Number of simulation runs (omit for single combat mode) |
| `--seed SEED` | Random seed for reproducibility |
| `--verbose` | Enable verbose output (ignored in single combat mode) |
| `--agent {heuristic,llm}` | Agent type for action selection |
| `--provider {ollama,openai,openrouter}` | LLM provider (only with `--agent llm`) |
| `--model MODEL` | LLM model name (default by provider) |
| `--role {default,tank,striker,controller,support}` | LLM tactical role archetype |
| `--ollama-host URL` | Ollama server URL (default: `http://localhost:11434`) |
| `--openrouter-url URL` | OpenRouter API base URL |
| `--openai-url URL` | OpenAI API base URL |
| `--terrain NAME` | Terrain for cover (load from `data/terrain/NAME.md`) |
| `--tui` | Launch Textual TUI for batch runs (requires `--runs`) |
| `--lang {en,it}` | Language for strategy evolution and round labels |

## Creature Resolution

- `fighter.md` → Load from `data/creatures/fighter.md` (local file)
- `goblin` → Fetch from SRD API, cache in `data/srd-cache/goblin.md`
- `orc` → Fetch from SRD API, cache in `data/srd-cache/orc.md`

Local files always take precedence over SRD data.

## Examples

### Single combat (detailed logs, one run)

```bash
python run.py --party fighter --enemies goblin goblin
```

### Batch simulation

```bash
python run.py --party fighter cleric --enemies goblin goblin goblin --runs 500
```

### Reproducible runs

```bash
python run.py --party fighter --enemies orc --runs 100 --seed 42
```

### LLM agent (local Ollama)

```bash
python run.py --party fighter --enemies goblin goblin --agent llm --runs 100
```

### LLM agent (OpenRouter)

```bash
python run.py --party fighter --enemies goblin --agent llm --provider openrouter --runs 50
```

### LLM with role archetype

```bash
python run.py --party fighter --enemies goblin --agent llm --role striker
```

### Remote Ollama

```bash
OLLAMA_HOST=http://remote:11434 python run.py --party fighter --enemies goblin --agent llm
# or
python run.py --party fighter --enemies goblin --agent llm --ollama-host http://remote:11434
```

### With terrain (cover)

```bash
python run.py --party fighter --enemies goblin --terrain forest --runs 50
```

### TUI mode

```bash
python run.py --party fighter --enemies goblin goblin --runs 100 --tui
```

### Italian output

```bash
python run.py --party fighter --enemies goblin --lang it --runs 20
```

## Outcome

The simulator runs in two main modes. What you see depends on whether you use `--runs` (batch) or omit it (single combat).

### Single Combat Mode (no `--runs`)

Runs one fight with full round-by-round output. Ideal for LLM agents or when you want to inspect tactics in detail.

**When to use:** Omit `--runs`, e.g. `python run.py --party fighter --enemies goblin goblin`.

**Output:**

1. **Setup** — Party and enemy lists, optional terrain
2. **Combat log** — Initial initiative rolls, then for each round:
   - **Strategy evolution** — Previous round’s tactics per creature (at start of round)
   - **Actions** — Movements, attacks, damage, opportunity attacks, deaths
3. **Combat Complete** — Summary with:

| Section | Description |
|--------|-------------|
| **Match level** | Difficulty rating: Easy, Medium, Hard, or Deadly |
| **Notes** | Short outcome: winner, rounds, casualties |
| **Final shape** | Each creature’s HP, AC, position at combat end |
| **Fallen** | Who reached 0 HP (party and enemies) |
| **Damage Dealt** | Per side: total damage and breakdown by attack (e.g. Longsword: 3 hit(s), 24 damage) |
| **Deaths by character** | Kills per character by damage type (e.g. Fighter: 2 kills (Slashing 2)) |

### LLM Mode (`--agent llm`)

Same as single combat, but:

- Each creature’s actions are chosen by the LLM
- **Pause between rounds** — You can press Enter to step through
- Strategy evolution shows the model’s reasoning

Use: `python run.py --party fighter --enemies goblin --agent llm` (no `--runs`).

### Batch Mode (`--runs N`)

Runs N simulations and aggregates results. Use for balance testing and win-rate estimates.

**When to use:** Add `--runs N`, e.g. `python run.py --party fighter cleric --enemies goblin goblin goblin --runs 500`.

**Output:**

| Metric | Description |
|--------|-------------|
| **Party Win Rate** | Proportion of runs where the party wins (0–100%) |
| **95% Confidence** | Confidence interval for the win rate |
| **TPK Rate** | Total Party Kill rate — proportion of runs where all party members die |
| **Difficulty** | Easy / Medium / Hard / Deadly based on win rate, TPK risk, and duration |
| **Combat Duration** | Average rounds when party wins vs when party loses |
| **Damage Dealt** | Total damage across runs; top damage dealers per creature |

### TUI Mode (`--tui --runs N`)

Interactive terminal UI for batch runs: progress bar, live stats, and log viewer.

---

## Metrics Reference

| Metric | Mode | Description |
|--------|------|-------------|
| **Match level / Difficulty** | Both | Easy, Medium, Hard, or Deadly. Based on win rate, TPK risk, and combat length |
| **Final shape** | Single | Each creature’s current HP, max HP, AC, and grid position at combat end |
| **Fallen** | Single | Names of creatures that reached 0 HP, grouped by party/enemies |
| **Damage Dealt** | Both | Per side: total damage and breakdown by attack (hits/casts and damage) |
| **Deaths by character** | Single | Who scored each killing blow, with damage type (e.g. Slashing, Fire) |
| **Party Win Rate** | Batch | % of runs won by the party |
| **95% Confidence** | Batch | Statistical interval for the win rate |
| **TPK Rate** | Batch | % of runs where the whole party died |
| **Combat Duration** | Batch | Average rounds to reach a result (separately for wins and losses) |

---

## Requirements

- Python 3.x
- Creature definitions as `.md` files in `data/creatures/`
- Optional: [Ollama](https://ollama.ai) for local LLM agents, or OpenRouter for cloud

## Project Structure

```
dnd-simulator/
├── data/
│   ├── creatures/     # .md files for monsters / PCs
│   ├── srd-cache/     # SRD creatures fetched on demand
│   ├── terrain/       # optional arena descriptions
│   └── saved_games/   # combat logs (resume support)
├── src/               # simulator core
└── run.py             # CLI entry point
```

## Rules

- **SRD 2014** only — no 2024 revisions
- **Chess-like coordinates** (A1, C4, F7) on a 5×5 ft grid
- **Manhattan distance** with optional diagonal cost

## License

MIT
