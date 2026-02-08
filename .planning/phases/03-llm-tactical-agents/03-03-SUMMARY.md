# Plan 03-03: LLMAgent Orchestrator with Circuit Breaker and CLI Integration

## Overview
Successfully created the LLMAgent orchestrator with circuit breaker + heuristic fallback, and wired it into the CLI. The agent integrates providers, prompt builder, parser, and validator into a working agent. The circuit breaker ensures batch simulations don't hang when the LLM is unavailable, and CLI integration lets the user actually run simulations with LLM agents.

## Deliverables
- `src/agents/llm_agent.py` - LLMAgent with choose_action, circuit breaker, fallback
- `src/cli/batch_args.py` - Updated CLI args with --agent, --provider, --model, --role flags  
- `run.py` - Updated CLI entry point that wires LLM agent with circuit breaker reset

## Key Features
- **LLM orchestration**: build_prompt → provider.chat_completion → parse_llm_output → validate_move → to_agent_action
- **Circuit breaker**: Disables LLM after 3 consecutive failures, resets between combat runs
- **Heuristic fallback**: Seamlessly falls back to HeuristicAgent on any failure in the chain
- **Retry logic**: Uses tenacity for transient errors (ConnectionError, TimeoutError, OSError)
- **CLI integration**: --agent llm --provider ollama/openrouter --model MODEL --role ROLE flags
- **Provider support**: Both Ollama (local) and OpenRouter (cloud) providers with proper API key validation
- **Role archetypes**: Tank/striker/controller/support/default roles influence tactical behavior
- **Backward compatibility**: Heuristic agent still works as default, no regressions

## Verification
- `python run.py --help` shows --agent, --provider, --model, --role flags with correct help text
- `python run.py --party fighter.md --enemies goblin` still works (heuristic default)
- LLMAgent instantiates with OllamaProvider or OpenRouterProvider
- LLMAgent.choose_action returns AgentAction (falls back to heuristic if no Ollama running)
- Circuit breaker opens after 3 consecutive failures
- Circuit breaker resets between combat runs in batch mode
- `python -m pytest tests/ -v` -- all tests pass

## Issues/Deviations
- Added circuit breaker reset logic to run_combat function to ensure proper reset between batch combat runs
- Added OpenRouter API key validation with warning message when provider is openrouter but key not set
- Used tenacity retry decorator for robust LLM provider calls