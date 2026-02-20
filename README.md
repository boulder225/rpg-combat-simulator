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
