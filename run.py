"""CLI entry point for combat simulator."""

import argparse
from pathlib import Path
from src.simulation.simulator import run_combat
from src.agents.heuristic import HeuristicAgent
from src.io.markdown import load_creature


def main():
    """Run a combat simulation from command line."""
    parser = argparse.ArgumentParser(description="D&D 5e combat simulator")
    parser.add_argument("--party", nargs="+", required=True, help="Party creature files")
    parser.add_argument(
        "--enemies", nargs="+", required=True, help="Enemy creature files"
    )
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    args = parser.parse_args()

    creatures = {}

    # Load party creatures
    for i, path in enumerate(args.party):
        creature_id, creature = load_creature(Path(path))
        # Override team and ID
        creature = creature.model_copy(
            update={"team": "party", "creature_id": f"party_{i}"}
        )
        creatures[f"party_{i}"] = creature

    # Load enemy creatures
    for i, path in enumerate(args.enemies):
        creature_id, creature = load_creature(Path(path))
        # Override team and ID
        creature = creature.model_copy(
            update={"team": "enemy", "creature_id": f"enemy_{i}"}
        )
        creatures[f"enemy_{i}"] = creature

    agent = HeuristicAgent()
    run_combat(creatures, agent, seed=args.seed)


if __name__ == "__main__":
    main()
