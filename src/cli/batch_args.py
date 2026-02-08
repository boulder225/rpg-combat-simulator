"""CLI argument parsing utilities for batch simulation.

Provides argument parsing for the main CLI entry point with support for:
- Party and enemy creature specification (local files or SRD names)
- Batch simulation run counts
- Random seed for reproducibility
- Verbose output control
"""

import argparse
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class BatchArgs:
    """Parsed arguments for batch simulation.

    Attributes:
        party: List of party creature names/files
        enemies: List of enemy creature names/files
        runs: Number of simulation runs (None means single simulation mode)
        seed: Random seed for reproducibility
        verbose: Enable verbose output
        agent: Agent type for action selection (heuristic or llm)
        provider: LLM provider (only used with --agent llm)
        model: LLM model name (None uses default based on provider)
        role: Creature role archetype for LLM tactical behavior
    """
    party: List[str]
    enemies: List[str]
    runs: Optional[int]
    seed: Optional[int]
    verbose: bool
    agent: str
    provider: str
    model: Optional[str]
    role: str


def parse_batch_args(args=None) -> BatchArgs:
    """Parse command line arguments for batch simulation.

    Supports two modes:
    1. Single simulation (no --runs): Run one combat, show detailed logs
    2. Batch simulation (with --runs): Run multiple combats, show statistics

    Creature resolution:
    - Names with .md extension: Load from local file (e.g., fighter.md)
    - Names without .md: Treat as SRD creature lookup (e.g., goblin)
    - Local files override SRD data when both exist

    Example usage:
        python run.py --party fighter.md --enemies goblin goblin goblin --runs 500

    Args:
        args: Command line arguments (None to use sys.argv)

    Returns:
        BatchArgs dataclass with parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="D&D 5e combat simulator with SRD creature support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
 Examples:
   # Single combat with detailed logs
   python run.py --party fighter.md --enemies goblin goblin

   # Batch simulation with 500 runs
   python run.py --party fighter.md cleric.md --enemies goblin goblin goblin --runs 500

   # With random seed for reproducibility
   python run.py --party fighter.md --enemies orc --runs 100 --seed 42

   # With LLM agent (local Ollama)
   python run.py --party fighter.md --enemies goblin goblin --agent llm --runs 100

   # With LLM agent (cloud OpenRouter)
   python run.py --party fighter.md --enemies goblin --agent llm --provider openrouter --runs 50

   # With role archetype
   python run.py --party fighter.md --enemies goblin --agent llm --role striker

 Creature resolution:
   - fighter.md    → Load from data/creatures/fighter.md (local file)
   - goblin        → Fetch from SRD API, cache in data/srd-cache/goblin.md
   - orc           → Fetch from SRD API, cache in data/srd-cache/orc.md

 Local files always take precedence over SRD data.
        """
    )

    parser.add_argument(
        "--party",
        nargs="+",
        required=True,
        metavar="CREATURE",
        help="Party creature files or SRD names (e.g., fighter.md or goblin)"
    )

    parser.add_argument(
        "--enemies",
        nargs="+",
        required=True,
        metavar="CREATURE",
        help="Enemy creature files or SRD names (e.g., goblin or orc.md)"
    )

    parser.add_argument(
        "--runs",
        type=int,
        default=None,
        metavar="N",
        help="Number of simulation runs (omit for single combat mode)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="SEED",
        help="Random seed for reproducibility"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output (ignored in single combat mode)"
    )

    parser.add_argument(
        "--agent",
        choices=["heuristic", "llm"],
        default="heuristic",
        help="Agent type for action selection (heuristic or llm)"
    )

    parser.add_argument(
        "--provider",
        choices=["ollama", "openrouter"],
        default="ollama",
        help="LLM provider (only used with --agent llm)"
    )

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="LLM model name (default: qwen2.5:7b-instruct for ollama, qwen/qwen2.5-coder-7b-instruct for openrouter)"
    )

    parser.add_argument(
        "--role",
        choices=["default", "tank", "striker", "controller", "support"],
        default="default",
        help="Creature role archetype for LLM tactical behavior"
    )

    parsed = parser.parse_args(args)

    # Validate runs parameter
    if parsed.runs is not None and parsed.runs <= 0:
        parser.error("--runs must be a positive integer")

    # Validate OpenRouter API key if needed
    if parsed.agent == "llm" and parsed.provider == "openrouter":
        import os
        if not os.environ.get("OPENROUTER_API_KEY"):
            print("Warning: OPENROUTER_API_KEY environment variable not set. OpenRouter provider will fail.")

    return BatchArgs(
        party=parsed.party,
        enemies=parsed.enemies,
        runs=parsed.runs,
        seed=parsed.seed,
        verbose=parsed.verbose,
        agent=parsed.agent,
        provider=parsed.provider,
        model=parsed.model,
        role=parsed.role
    )

    parser.add_argument(
        "--agent",
        choices=["heuristic", "llm"],
        default="heuristic",
        help="Agent type for action selection (heuristic or llm)"
    )

    parser.add_argument(
        "--provider",
        choices=["ollama", "openrouter"],
        default="ollama",
        help="LLM provider (only used with --agent llm)"
    )

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="LLM model name (default: qwen2.5:7b-instruct for ollama, qwen/qwen2.5-coder-7b-instruct for openrouter)"
    )

    parser.add_argument(
        "--role",
        choices=["default", "tank", "striker", "controller", "support"],
        default="default",
        help="Creature role archetype for LLM tactical behavior"
    )

    parsed = parser.parse_args(args)

    # Validate runs parameter
    if parsed.runs is not None and parsed.runs <= 0:
        parser.error("--runs must be a positive integer")

    # Validate OpenRouter API key if needed
    if parsed.agent == "llm" and parsed.provider == "openrouter":
        import os
        if not os.environ.get("OPENROUTER_API_KEY"):
            print("Warning: OPENROUTER_API_KEY environment variable not set. OpenRouter provider will fail.")

    return BatchArgs(
        party=parsed.party,
        enemies=parsed.enemies,
        runs=parsed.runs,
        seed=parsed.seed,
        verbose=parsed.verbose,
        agent=parsed.agent,
        provider=parsed.provider,
        model=parsed.model,
        role=parsed.role
    )
