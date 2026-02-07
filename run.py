import argparse
from src.simulation.simulator import run_combat
from src.agents.heuristic import HeuristicAgent
from src.domain.combat_state import Creature


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--party', nargs='+', required=True)
    parser.add_argument('--enemies', nargs='+', required=True)
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()
    creatures = {}
    # minimal dummy creatures
    creatures['party'] = Creature('party', 'Party', 'party', 'A1', 10, 10, 10, 30, actions=[])
    creatures['enemy'] = Creature('enemy', 'Enemy', 'enemy', 'B1', 5, 5, 10, 30, actions=[])
    agent = HeuristicAgent()
    run_combat(creatures, agent, seed=args.seed)


if __name__ == '__main__':
    main()
