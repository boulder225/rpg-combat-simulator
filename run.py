"""CLI entry point for combat simulator with batch simulation support."""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.cli.batch_args import parse_batch_args
from src.io.creature_loader import CreatureLoader
from src.simulation.simulator import run_combat
from src.simulation.monte_carlo import MonteCarloSimulator
from src.simulation.batch_runner import BatchRunner
from src.agents.heuristic import HeuristicAgent
from src.analysis.difficulty import calculate_difficulty_rating
from src.simulation.victory import get_winner


def _single_combat_difficulty_and_notes(final_state, creatures):
    """Compute difficulty rating and short notes for a single combat.

    Args:
        final_state: CombatState at end of combat
        creatures: Original creature dict (for names/teams)

    Returns:
        Tuple of (difficulty_str, notes_str)
    """
    winner = get_winner(final_state)
    rounds = final_state.round
    party = [c for c in final_state.creatures.values() if c.team == "party"]
    enemies = [c for c in final_state.creatures.values() if c.team == "enemy"]
    party_size = len(party)
    party_alive = sum(1 for c in party if c.current_hp > 0)
    party_down = party_size - party_alive
    enemies_alive = sum(1 for c in enemies if c.current_hp > 0)
    tpk = party_alive == 0
    win_rate = 1.0 if winner == "party" else 0.0
    tpk_risk = 1.0 if tpk else 0.0

    difficulty = calculate_difficulty_rating(
        win_rate=win_rate,
        ci_width=0.0,
        tpk_risk=tpk_risk,
        avg_duration=rounds,
        party_size=max(1, party_size),
    )

    # Notes: outcome, duration, casualties
    if winner == "party":
        outcome = "Party victory"
    elif winner == "enemy":
        outcome = "Enemy victory"
    else:
        outcome = "No clear winner"
    notes = [f"{outcome} in {rounds} round(s)."]
    if party_down > 0:
        notes.append(f"Party: {party_down} down, {party_alive} standing.")
    if enemies_alive == 0 and enemies:
        notes.append("All enemies defeated.")
    elif enemies_alive > 0:
        notes.append(f"Enemies: {enemies_alive} still standing.")
    notes_str = " ".join(notes)
    return difficulty, notes_str


def _format_final_shape(final_state) -> str:
    """Return final shape of party and enemies (name, HP, AC, position) for end-of-combat stats."""
    party = sorted(
        [c for c in final_state.creatures.values() if c.team == "party"],
        key=lambda c: c.name,
    )
    enemies = sorted(
        [c for c in final_state.creatures.values() if c.team == "enemy"],
        key=lambda c: c.name,
    )
    lines = []
    if party:
        parts = [f"{c.name} {c.current_hp}/{c.hp_max} HP AC {c.ac} {c.position}" for c in party]
        lines.append("  Party: " + " | ".join(parts))
    if enemies:
        parts = [f"{c.name} {c.current_hp}/{c.hp_max} HP AC {c.ac} {c.position}" for c in enemies]
        lines.append("  Enemies: " + " | ".join(parts))
    return "\n".join(lines) if lines else ""


def _format_fallen(final_state) -> str:
    """Return a Fallen report: who died (0 HP) by party and enemies."""
    party_fallen = [c.name for c in final_state.creatures.values() if c.team == "party" and c.current_hp <= 0]
    enemy_fallen = [c.name for c in final_state.creatures.values() if c.team == "enemy" and c.current_hp <= 0]
    lines = []
    if party_fallen:
        lines.append(f"  Party: {', '.join(party_fallen)}")
    else:
        lines.append("  Party: none")
    if enemy_fallen:
        lines.append(f"  Enemies: {', '.join(enemy_fallen)}")
    else:
        lines.append("  Enemies: none")
    return "\n".join(lines)


def _format_combat_stats(logger, final_state) -> str:
    """Build Damage Dealt summary: by side, then by weapon/spell/special attack (hits and damage)."""
    stats = logger.get_combat_stats()
    if not stats:
        return ""

    # Map creature name -> team from final state (names are stable)
    name_to_team = {}
    for c in final_state.creatures.values():
        name_to_team[c.name] = c.team

    # Aggregate by team then by (attack_name, is_aoe): count and total damage
    by_team = {}  # team -> (attack_name, is_aoe) -> (count, damage)
    for s in stats:
        team = name_to_team.get(s["attacker_name"], "?")
        if team not in by_team:
            by_team[team] = {}
        key = (s["attack_name"], s["is_aoe"])
        if key not in by_team[team]:
            by_team[team][key] = {"count": 0, "damage": 0}
        by_team[team][key]["count"] += 1
        by_team[team][key]["damage"] += s["damage"]

    lines = []
    for team_label, team_key in [("Party", "party"), ("Enemies", "enemy")]:
        if team_key not in by_team:
            continue
        entries = []
        total_damage = 0
        for (attack_name, is_aoe), agg in sorted(by_team[team_key].items(), key=lambda x: -x[1]["damage"]):
            count, damage = agg["count"], agg["damage"]
            total_damage += damage
            if is_aoe:
                entries.append(f"{attack_name}: {count} cast(s), {damage} total damage")
            else:
                entries.append(f"{attack_name}: {count} hit(s), {damage} damage")
        lines.append(f"  {team_label} (total {total_damage}): " + "; ".join(entries))
    return "\n".join(lines) if lines else ""


def _format_deaths_by_element(logger) -> str:
    """Build 'Deaths by character' (kills per character, by damage type) in same style as Damage Dealt."""
    deaths = logger.get_deaths_by_type()
    if not deaths:
        return ""

    # Each record: (victim_name, victim_team, damage_type, killer_name, killer_team)
    # Group by killer side, then by killer name, then count kills and by damage type
    by_side: dict[str, dict[str, dict[str, int]]] = {}  # killer_team -> killer_name -> damage_type -> count
    for _victim, _v_team, dtype, killer_name, killer_team in deaths:
        dtype = (dtype or "unknown").strip().lower() or "unknown"
        k_team = killer_team or "?"
        k_name = killer_name or "?"
        if k_team not in by_side:
            by_side[k_team] = {}
        if k_name not in by_side[k_team]:
            by_side[k_team][k_name] = {}
        by_side[k_team][k_name][dtype] = by_side[k_team][k_name].get(dtype, 0) + 1

    lines = []
    for team_label, team_key in [("Party", "party"), ("Enemies", "enemy")]:
        if team_key not in by_side or not by_side[team_key]:
            continue
        total_kills = sum(
            sum(by_side[team_key][k].values())
            for k in by_side[team_key]
        )
        entries = []
        for killer_name in sorted(by_side[team_key].keys(), key=lambda k: -sum(by_side[team_key][k].values())):
            by_type = by_side[team_key][killer_name]
            kills = sum(by_type.values())
            type_parts = [f"{dt.capitalize()} {n}" for dt, n in sorted(by_type.items(), key=lambda x: -x[1])]
            kill_str = "kill" if kills == 1 else "kills"
            entries.append(f"{killer_name}: {kills} {kill_str} ({'; '.join(type_parts)})")
        lines.append(f"  {team_label} (total {total_kills} kill{'s' if total_kills != 1 else ''}): " + "; ".join(entries))
    return "\n".join(lines)


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


def run_single_combat(creatures, agent, seed=None, terrain=None, lang="en", pause_between_rounds=False):
    """Run a single combat simulation with detailed logs.

    Args:
        creatures: Dict of creature_id -> Creature
        agent: Agent for action selection
        seed: Random seed for reproducibility
        terrain: Optional Terrain for cover
        lang: Language for strategy evolution and round labels ("en", "it")
        pause_between_rounds: If True, show round shape summary and wait for Enter each round (e.g. LLM mode)
    """
    print("Running single combat simulation...")
    print(f"Party: {[c.name for c in creatures.values() if c.team == 'party']}")
    print(f"Enemies: {[c.name for c in creatures.values() if c.team == 'enemy']}")
    if terrain:
        print(f"Terrain: {terrain.name}")
    print()

    final_state, logger = run_combat(
        creatures,
        agent,
        seed=seed,
        verbose=True,
        terrain=terrain,
        lang=lang,
        pause_between_rounds=pause_between_rounds,
    )

    # Difficulty, notes, and how each side fought
    difficulty, notes = _single_combat_difficulty_and_notes(final_state, creatures)
    combat_stats_str = _format_combat_stats(logger, final_state)
    print("\n" + "="*60)
    print("Combat Complete!")
    print("="*60)
    print(f"\nMatch level: {difficulty}")
    print(f"Notes: {notes}")
    print("\nFinal shape:")
    print(_format_final_shape(final_state))
    print("\nFallen:")
    print(_format_fallen(final_state))
    if combat_stats_str:
        print("\nDamage Dealt:")
        print(combat_stats_str)
    deaths_by_character = _format_deaths_by_element(logger)
    if deaths_by_character:
        print("\nDeaths by character:")
        print(deaths_by_character)


def run_batch_simulation(creatures, agent, runs, seed=None, verbose=True, terrain=None, lang="en"):
    """Run batch simulation with Monte Carlo engine.

    Args:
        creatures: Dict of creature_id -> Creature
        agent: Agent for action selection
        runs: Number of simulation runs
        seed: Random seed for reproducibility
        verbose: Whether to print progress updates
        terrain: Optional Terrain for cover
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
    results = runner.run_batch(creatures, agent, seed=seed, terrain=terrain, lang=lang)

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

    # Load terrain if specified
    terrain = None
    if args.terrain:
        try:
            from src.io.terrain_loader import TerrainLoader
            terrain_loader = TerrainLoader(terrain_dir="data/terrain")
            terrain = terrain_loader.load(args.terrain)
        except FileNotFoundError as e:
            print(f"Error loading terrain: {e}")
            return 1

    # Initialize agent
    if args.agent == "llm":
        from src.agents.llm_agent import LLMAgent
        from src.agents.llm_providers import OllamaProvider, OpenAIProvider, OpenRouterProvider
        import os

        # Select provider
        if args.provider == "ollama":
            ollama_host = args.ollama_host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
            provider = OllamaProvider(host=ollama_host)
        elif args.provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                print("Error: OPENAI_API_KEY environment variable required for openai provider")
                return 1
            openai_base = args.openai_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            provider = OpenAIProvider(api_key=api_key, base_url=openai_base)
        elif args.provider == "openrouter":
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                print("Error: OPENROUTER_API_KEY environment variable required for openrouter provider")
                return 1
            openrouter_base = args.openrouter_url or os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            provider = OpenRouterProvider(api_key=api_key, base_url=openrouter_base)

        # Select model (defaults based on provider)
        model = args.model
        if model is None:
            model = {
                "ollama": "qwen2.5:7b-instruct",
                "openai": "gpt-4o-mini",
                "openrouter": "qwen/qwen-2.5-7b-instruct",
            }[args.provider]

        agent = LLMAgent(provider=provider, model=model, role=args.role)
        print(f"Using LLM agent: {args.provider}/{model} (role: {args.role})")
    else:
        agent = HeuristicAgent()

    # Run appropriate mode
    if args.tui:
        if args.runs is None:
            print("--tui requires --runs for batch simulations.")
            return 1
        # TUI batch mode
        from src.tui.app import run_tui

        run_tui(
            creatures=creatures,
            agent=agent,
            runs=args.runs,
            seed=args.seed,
            terrain=terrain,
            lang=args.lang,
        )
    elif args.runs is None:
        # Single combat mode (pause each round in LLM mode)
        run_single_combat(
            creatures,
            agent,
            seed=args.seed,
            terrain=terrain,
            lang=args.lang,
            pause_between_rounds=(args.agent == "llm"),
        )
    else:
        # Batch simulation mode (standard CLI)
        run_batch_simulation(
            creatures,
            agent,
            runs=args.runs,
            seed=args.seed,
            verbose=args.verbose,
            terrain=terrain,
            lang=args.lang,
        )

    return 0


if __name__ == "__main__":
    exit(main())
