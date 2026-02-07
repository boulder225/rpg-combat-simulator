# D&D 5e Combat Simulator

A terminal-based D&D 5th Edition combat simulator that helps Dungeon Masters evaluate encounter balance through Monte Carlo batch simulations.

## What It Does

- **Define creatures** as markdown files with YAML frontmatter (stats, actions, spells)
- **Run batch simulations** — 20+ runs in minutes to see win rates, damage breakdowns, and tactical patterns
- **AI-driven tactics** — heuristic or LLM-powered agents make decisions for all combatants
- **Fast feedback** — tweak encounters and re-run until the balance feels right

## Quick Start

```bash
python run.py --party fighter.md rogue.md --enemies goblin-boss.md --runs 50 --agent heuristic
```

## Requirements

- Python 3.x
- Creature definitions as `.md` files in `data/creatures/`
- Optional: [Ollama](https://ollama.ai) for local LLM agents, or OpenRouter for cloud

## Project Structure

```
dnd-combat-sim/
├── data/
│   ├── creatures/     # .md files for monsters / PCs
│   ├── terrain/       # optional arena descriptions
│   └── saved_games/   # combat logs (resume support)
├── rules/             # cached JSON from 5e-database
├── src/               # simulator core
└── run.py             # CLI entry point
```

## Rules

- **SRD 2014** only — no 2024 revisions
- **Chess-like coordinates** (A1, C4, F7) on a 5×5 ft grid
- **Manhattan distance** with optional diagonal cost

## License

MIT
