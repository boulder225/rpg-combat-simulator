"""CLI entry point for combat simulator with batch simulation support."""

from pathlib import Path
from src.cli.batch_args import parse_batch_args
from src.io.creature_loader import CreatureLoader
from src.simulation.simulator import run_combat
from src.simulation.monte_carlo import MonteCarloSimulator
from src.simulation.batch_runner import BatchRunner
from src.agents.heuristic import HeuristicAgent
from src.analysis.difficulty import calculate_difficulty_rating


def load_creatures_from_args(args, loader):
    """Load creatures from parsed arguments using CreatureLoader.

    Args:
        args: BatchArgs with party and enemies lists
        loader: CreatureLoader instance

    Returns:
        Dict of creature_id -> Creature
    """
    creatures = {}

    # Load party creatures
    for i, name in enumerate(args.party):
        creature = loader.load_creature(name, team="party", position=f"A{i+1}")
        creatures[creature.creature_id] = creature

    # Load enemy creatures
    for i, name in enumerate(args.enemies):
        creature = loader.load_creature(name, team="enemy", position=f"E{i+1}")
        creatures[creature.creature_id] = creature

    return creatures


def run_single_combat(creatures, agent, seed=None):
    """Run a single combat simulation with detailed logs.

    Args:
        creatures: Dict of creature_id -> Creature
        agent: Agent for action selection
        seed: Random seed for reproducibility
    """
    print("Running single combat simulation...")
    print(f"Party: {[c.name for c in creatures.values() if c.team == 'party']}")
    print(f"Enemies: {[c.name for c in creatures.values() if c.team == 'enemy']}")
    print()

    final_state, logger = run_combat(creatures, agent, seed=seed, verbose=True)

    # Print summary
    print("\n" + "="*60)
    print("Combat Complete!")
    print("="*60)


def run_batch_simulation(creatures, agent, runs, seed=None, verbose=True):
    """Run batch simulation with Monte Carlo engine.

    Args:
        creatures: Dict of creature_id -> Creature
        agent: Agent for action selection
        runs: Number of simulation runs
        seed: Random seed for reproducibility
        verbose: Whether to print progress updates
    """
    print("="*60)
    print("Batch Simulation")
    print("="*60)
    print(f"Party: {[c.name for c in creatures.values() if c.team == 'party']}")
    print(f"Enemies: {[c.name for c in creatures.values() if c.team == 'enemy']}")
    print(f"Runs: {runs}")
    if seed is not None:
        print(f"Seed: {seed}")
    print()

    # Initialize Monte Carlo simulator with specified runs
    # Override adaptive sampling to run exactly the specified number
    simulator = MonteCarloSimulator(
        min_runs=runs,
        max_runs=runs,
        target_precision=0.01,  # Will hit max_runs before this
        check_interval=100
    )

    # Initialize batch runner
    runner = BatchRunner(simulator, verbose=verbose)

    # Run batch simulation
    results = runner.run_batch(creatures, agent, seed=seed)

    # Display final results
    print("\n" + "="*60)
    print("Simulation Complete")
    print("="*60)

    ci_lower, ci_upper = results.confidence_interval
    ci_width = ci_upper - ci_lower

    print(f"\nResults ({results.total_runs} runs):")
    print(f"  Party Win Rate: {results.win_rate:.1%}")
    print(f"  95% Confidence: [{ci_lower:.1%}, {ci_upper:.1%}] (±{ci_width/2:.1%})")
    print(f"  TPK Rate: {results.tpk_count/results.total_runs:.1%} ({results.tpk_count} total)")

    # Calculate difficulty rating
    party_size = sum(1 for c in creatures.values() if c.team == "party")
    # Use average of wins and losses for avg_duration
    avg_duration = (results.avg_combat_duration_wins + results.avg_combat_duration_losses) / 2
    rating = calculate_difficulty_rating(
        results.win_rate,
        ci_width,
        results.tpk_count / results.total_runs,
        avg_duration,
        party_size
    )
    print(f"\nDifficulty: {rating}")

    print(f"\nCombat Duration:")
    print(f"  Wins: {results.avg_combat_duration_wins:.1f} rounds avg")
    print(f"  Losses: {results.avg_combat_duration_losses:.1f} rounds avg")

    print(f"\nDamage Dealt:")
    print(f"  Total: {results.damage_breakdown.total_damage}")
    if results.damage_breakdown.by_creature:
        print(f"  Top damage dealers:")
        sorted_creatures = sorted(
            results.damage_breakdown.by_creature.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        for name, damage in sorted_creatures:
            print(f"    {name}: {damage}")


def main():
    """Main CLI entry point with support for single and batch simulation."""
    # Parse arguments
    args = parse_batch_args()

    # Initialize creature loader
    loader = CreatureLoader(
        cache_dir="data/creatures",
        srd_cache_dir="data/srd-cache"
    )

    # Load creatures
    try:
        creatures = load_creatures_from_args(args, loader)
    except ValueError as e:
        print(f"Error loading creatures: {e}")
        return 1

    # Initialize agent
    if args.agent == "llm":
        from src.agents.llm_agent import LLMAgent
        from src.agents.llm_providers import OllamaProvider, OpenRouterProvider
        import os

        # Select provider
        if args.provider == "ollama":
            provider = OllamaProvider()
        elif args.provider == "openrouter":
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                print("Error: OPENROUTER_API_KEY environment variable required for openrouter provider")
                return 1
            provider = OpenRouterProvider(api_key=api_key)

        # Select model (defaults based on provider)
        model = args.model
        if model is None:
            model = "qwen2.5:7b-instruct" if args.provider == "ollama" else "qwen/qwen2.5-coder-7b-instruct"

        agent = LLMAgent(provider=provider, model=model, role=args.role)
        print(f"Using LLM agent: {args.provider}/{model} (role: {args.role})")
    else:
        agent = HeuristicAgent()

    # Run appropriate mode
    if args.runs is None:
        # Single combat mode
        run_single_combat(creatures, agent, seed=args.seed)
    else:
        # Batch simulation mode
        run_batch_simulation(
            creatures,
            agent,
            runs=args.runs,
            seed=args.seed,
            verbose=args.verbose
        )

    return 0


if __name__ == "__main__":
    exit(main())
