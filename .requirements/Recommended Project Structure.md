dnd-combat-sim/
├── data/
│   ├── creatures/          # .md files for custom monsters / PCs
│   ├── terrain/            # optional .md arena descriptions
│   └── saved_games/        # Markdown logs for resuming
├── rules/                  # optional cached JSON from 5e-database
├── src/
│   ├── creature.py         # Pydantic/dataclass: hp, ac, position:str, actions…
│   ├── combat_state.py     # creatures dict, initiative order, round, log list
│   ├── distance.py         # coord parsing → feet, advantage logic
│   ├── agent.py            # BaseAgent + HeuristicAgent + LLM via ollama / openai
│   ├── simulator.py        # main loop: roll init → turns → end check
│   └── logger.py           # append-only Markdown writer
└── run.py                  # CLI entry: python run.py --party fighter.md rogue.md --enemies dragon.md --runs 50