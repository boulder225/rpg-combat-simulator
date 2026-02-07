import argparse
from src.simulation.simulator import run_combat
from src.agents.heuristic import HeuristicAgent
from src.io.parser import parse_creature_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--party', nargs='+', required=True)
    parser.add_argument('--enemies', nargs='+', required=True)
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()

    creatures = {}
    for i, path in enumerate(args.party):
        cid = f"party_{i}"
        c = parse_creature_file(path, cid)
        c.team = "party"
        creatures[cid] = c
    for i, path in enumerate(args.enemies):
        cid = f"enemy_{i}"
        c = parse_creature_file(path, cid)
        c.team = "enemy"
        creatures[cid] = c

    agent = HeuristicAgent()
    run_combat(creatures, agent, seed=args.seed)


if __name__ == '__main__':
    main()
