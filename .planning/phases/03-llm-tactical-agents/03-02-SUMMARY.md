# Plan 03-02: LLM Providers and Prompt Builder

## Overview
Successfully created the input/output interfaces for LLM integration. OllamaProvider and OpenRouterProvider handle synchronous LLM calls, while the prompt builder constructs combat state prompts with role-based system instructions that guide tactical behavior.

## Deliverables
- `src/agents/llm_providers.py` - Synchronous Ollama and OpenRouter provider implementations
- `src/agents/llm_prompt.py` - Combat state → LLM prompt messages with role archetypes
- `pyproject.toml` - Added ollama, openai, and tenacity dependencies

## Key Features
- **Synchronous providers**: Both OllamaProvider and OpenRouterProvider use sync APIs to match the combat simulator's synchronous architecture
- **Role archetype system**: Tank/striker/controller/support/default roles modify system prompts with distinct behavioral instructions
- **Concise prompt engineering**: Combat state prompts stay within 2K-4K token budget for 7B models
- **Tactical notes**: Distance-based tactical information for each enemy
- **Proper error handling**: Provider exceptions propagate to agent level for retry logic
- **Dependency management**: Added required dependencies (ollama, openai, tenacity) to pyproject.toml

## Verification
- Dependencies installed successfully with `pip install -e ".[dev]"`
- Provider classes import and instantiate without error
- Prompt builder produces correctly formatted messages matching user's specified format
- Role archetypes modify system prompt (STRIKER vs TANK vs default produce different instructions)
- Tactical notes show correct distances between creatures
- All existing tests pass: `python -m pytest tests/ -v`

## Issues/Deviations
None. Implementation matches plan requirements exactly.