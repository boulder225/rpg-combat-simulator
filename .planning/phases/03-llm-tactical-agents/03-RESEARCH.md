# Phase 3: LLM Tactical Agents - Research

**Researched:** 2026-02-08
**Domain:** LLM integration for tactical decision-making in combat simulation
**Confidence:** HIGH

## Summary

Phase 3 integrates LLM-based tactical decision-making into the combat simulation using two provider options: local Ollama (qwen2.5:7b-instruct) and cloud OpenRouter (qwen/qwen2.5-coder-7b-instruct). The standard approach uses Pydantic models for strict output validation with automatic retry logic, falling back to the existing HeuristicAgent when LLM parsing fails or produces illegal moves.

The research confirms that Pydantic v2 + Instructor library provides the most robust pattern for LLM structured output validation in 2026. This combination offers automatic retries, type-safe validation, and multi-provider support. The user's chosen output format (XML `<thinking>` tag + uppercase key-value pairs) can be parsed reliably using regex extraction followed by Pydantic validation. Ollama Python client v0.6.1 and OpenAI SDK with OpenRouter provide production-ready LLM integration with async/streaming support.

For graceful degradation, the circuit breaker + fallback pattern is standard: parse failures immediately fall back to HeuristicAgent, while repeated validation failures trigger circuit breaker to skip LLM entirely for that combat.

**Primary recommendation:** Use Pydantic v2 models with custom validators for move legality, parse LLM output with regex extraction, implement retry logic with tenacity for transient failures, and maintain HeuristicAgent as immediate fallback for parse/validation failures.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| ollama | 0.6.1 | Local LLM inference via Ollama | Official Python client, supports async/streaming, 3M+ monthly downloads |
| openai | 1.x | Cloud LLM via OpenRouter | Industry standard SDK, OpenRouter is fully OpenAI-compatible |
| pydantic | 2.12+ | LLM output validation | De facto standard for structured data validation in Python, strict mode + custom validators |
| tenacity | 8.3+ | Retry logic with exponential backoff | Apache 2.0, most popular Python retry library, AI-optimized jitter |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| instructor | 3.x+ | Structured LLM output extraction | Optional - simplifies Pydantic integration with LLMs, auto-retry on validation failure |
| typing-extensions | 4.x | Enhanced type hints | For Python 3.11 compatibility with advanced Pydantic features |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pydantic + regex parsing | LangChain OutputParser | LangChain adds heavy dependencies (100+ packages), project already uses Pydantic |
| tenacity | backoff library | tenacity has better async support and more flexible wait strategies |
| Custom retry logic | No retries | Transient failures (network, rate limits) would cause unnecessary fallbacks |

**Installation:**
```bash
# Core LLM integration
pip install ollama>=0.6.1 openai>=1.0 pydantic>=2.12 tenacity>=8.3

# Optional structured output helper
pip install instructor>=3.0
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── agents/
│   ├── base.py              # AgentAction Protocol (existing)
│   ├── heuristic.py         # HeuristicAgent (existing fallback)
│   ├── llm_agent.py         # LLMAgent: choose_action() orchestration
│   ├── llm_providers.py     # OllamaProvider, OpenRouterProvider
│   ├── llm_prompt.py        # Prompt builder (combat state -> LLM prompt)
│   ├── llm_parser.py        # Output parser (LLM text -> AgentAction)
│   └── llm_validator.py     # Move legality validator (uses CombatState)
```

### Pattern 1: Provider Abstraction
**What:** Abstract LLM provider interface for local (Ollama) and cloud (OpenRouter) backends
**When to use:** When supporting multiple LLM providers with identical calling code
**Example:**
```python
# Source: ollama-python v0.6.1 + OpenAI SDK pattern
from abc import ABC, abstractmethod
from typing import AsyncIterator

class LLMProvider(ABC):
    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7
    ) -> str:
        """Get completion from LLM."""
        pass

class OllamaProvider(LLMProvider):
    def __init__(self, host: str = "http://localhost:11434"):
        from ollama import AsyncClient
        self.client = AsyncClient(host=host)

    async def chat_completion(
        self,
        messages: list[dict],
        model: str = "qwen2.5:7b-instruct",
        temperature: float = 0.7
    ) -> str:
        response = await self.client.chat(
            model=model,
            messages=messages,
            options={"temperature": temperature}
        )
        return response['message']['content']

class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

    async def chat_completion(
        self,
        messages: list[dict],
        model: str = "qwen/qwen2.5-coder-7b-instruct",
        temperature: float = 0.7
    ) -> str:
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
```

### Pattern 2: Strict Output Parsing with Pydantic
**What:** Parse LLM output into validated Pydantic model, then convert to AgentAction
**When to use:** When LLM output has fixed format with validation requirements
**Example:**
```python
# Source: Pydantic v2 strict mode + custom validators
from pydantic import BaseModel, Field, field_validator
import re

class LLMResponse(BaseModel):
    """Validated LLM output."""
    thinking: str = Field(min_length=50, max_length=500)
    action: str
    target: str | None = None
    movement: str | None = None
    bonus: str | None = None
    reaction: str | None = None

    @field_validator('action')
    def action_must_be_valid(cls, v: str) -> str:
        valid = ['attack', 'move', 'move_and_attack', 'dodge', 'death_save']
        v_lower = v.lower().strip()
        if v_lower not in valid:
            raise ValueError(f"Invalid action: {v}. Must be one of {valid}")
        return v_lower

    @field_validator('movement')
    def movement_must_be_grid_position(cls, v: str | None) -> str | None:
        if v is None or v.lower() in ['none', 'stay', '']:
            return None
        # Validate grid position like "D5"
        if not re.match(r'^[A-Z]\d+$', v.upper().strip()):
            raise ValueError(f"Invalid movement position: {v}")
        return v.upper().strip()

def parse_llm_output(text: str) -> LLMResponse:
    """Parse LLM output text into validated model."""
    # Extract thinking tag
    thinking_match = re.search(r'<thinking>(.*?)</thinking>', text, re.DOTALL)
    thinking = thinking_match.group(1).strip() if thinking_match else ""

    # Extract key-value pairs (uppercase keys)
    def extract_value(key: str) -> str | None:
        match = re.search(rf'^{key}:\s*(.+)$', text, re.MULTILINE | re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            return None if val.lower() in ['none', ''] else val
        return None

    return LLMResponse(
        thinking=thinking,
        action=extract_value('ACTION') or 'dodge',
        target=extract_value('TARGET'),
        movement=extract_value('MOVEMENT'),
        bonus=extract_value('BONUS'),
        reaction=extract_value('REACTION')
    )
```

### Pattern 3: Retry with Exponential Backoff
**What:** Automatically retry LLM calls on transient failures (network, rate limit)
**When to use:** When calling external LLM APIs that may have transient failures
**Example:**
```python
# Source: tenacity 8.3+ with exponential backoff
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

class LLMAgent:
    def __init__(self, provider: LLMProvider, fallback_agent):
        self.provider = provider
        self.fallback = fallback_agent

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    async def _call_llm(self, messages: list[dict], model: str) -> str:
        """Call LLM with automatic retry on transient failures."""
        return await self.provider.chat_completion(messages, model)

    async def choose_action(self, state, creature_id: str) -> AgentAction:
        """Choose action using LLM, fallback to heuristic on failure."""
        try:
            # Build prompt from combat state
            messages = build_prompt(state, creature_id)

            # Call LLM with retry logic
            response_text = await self._call_llm(messages, model="qwen2.5:7b-instruct")

            # Parse and validate output
            llm_response = parse_llm_output(response_text)

            # Validate move legality
            action = validate_and_convert(llm_response, state, creature_id)

            return action

        except Exception as e:
            # Log error and fall back to heuristic
            print(f"LLM agent failed: {e}, falling back to heuristic")
            return self.fallback.choose_action(state, creature_id)
```

### Pattern 4: Move Legality Validation
**What:** Validate that LLM-suggested move is legal in current combat state
**When to use:** After parsing LLM output, before executing action
**Example:**
```python
# Source: Game AI action validation pattern
from src.domain.distance import distance_in_feet

def validate_move_legality(
    action: LLMResponse,
    state: CombatState,
    creature_id: str
) -> tuple[bool, str]:
    """
    Validate if action is legal in current combat state.

    Returns: (is_valid, error_message)
    """
    creature = state.creatures[creature_id]

    # Check movement doesn't exceed speed
    if action.movement:
        try:
            current_pos = creature.position
            new_pos = action.movement
            dist = distance_in_feet(current_pos, new_pos)
            if dist > creature.speed:
                return False, f"Movement {dist}ft exceeds speed {creature.speed}ft"
        except Exception:
            return False, f"Invalid position: {action.movement}"

    # Check target exists and is valid
    if action.target:
        if action.target not in state.creatures:
            return False, f"Target {action.target} does not exist"
        target = state.creatures[action.target]
        if target.current_hp <= 0:
            return False, f"Target {action.target} is already dead"

    # Check action requires valid attack
    if action.action in ['attack', 'move_and_attack']:
        if not creature.actions:
            return False, "Creature has no actions available"

        # Check attack is in creature's stat block
        # (simplified - full check would verify attack name)
        if action.target is None:
            return False, "Attack action requires target"

    return True, ""
```

### Anti-Patterns to Avoid
- **Parsing JSON from LLM text without Pydantic validation:** LLMs frequently output malformed JSON or add extra text. Always validate with Pydantic after extraction.
- **No fallback mechanism:** LLM calls can fail in many ways (network, parse, validation). Always have a deterministic fallback.
- **Blocking synchronous LLM calls:** LLM inference takes 1-2 seconds. Use async/await to avoid blocking the event loop.
- **Using LLM for every decision without circuit breaker:** If validation fails repeatedly, circuit breaker should skip LLM to prevent wasted latency.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Retry logic with backoff | Custom sleep loops | tenacity | Handles edge cases: jitter, async, exception filtering, stop conditions |
| LLM output validation | String parsing + if statements | Pydantic v2 models | Type safety, automatic coercion, field validators, clear error messages |
| OpenAI API client | requests + JSON | openai SDK | Handles auth, retries, streaming, rate limits, error codes |
| Ollama API client | requests + JSON | ollama Python client | Official client, async support, streaming, error handling |
| XML tag extraction | String splitting | regex with named groups | Handles malformed output, whitespace, case sensitivity |

**Key insight:** LLM output parsing is inherently unreliable. The value of Pydantic + tenacity is not the parsing itself, but the automatic validation, error messages, and retry infrastructure that catches edge cases you won't think of until production.

## Common Pitfalls

### Pitfall 1: Trusting LLM Output Format
**What goes wrong:** LLM outputs extra text, markdown formatting, or JSON wrapped in code blocks despite prompt instructions.
**Why it happens:** Even with strict format instructions, 7B models occasionally add preambles like "Here's my decision:" or wrap output in ```xml tags.
**How to avoid:** Use permissive regex parsing that extracts content between tags, not just splitting on delimiters. Handle missing tags gracefully.
**Warning signs:** Parsing works in testing with manually crafted examples but fails on real LLM output.

### Pitfall 2: No Validation After Parsing
**What goes wrong:** LLM suggests illegal moves (out-of-range attacks, targeting dead creatures, exceeding movement speed) that crash the rules engine.
**Why it happens:** LLMs hallucinate or misunderstand game state. They might target "Fighter" when only "Fighter_1" exists, or suggest moving 60ft when speed is 30ft.
**How to avoid:** Always validate parsed action against combat state before returning. Check: target exists, target alive, movement within speed, attack in stat block, range sufficient.
**Warning signs:** Rules engine raises exceptions during execute_action(), combat logs show impossible moves.

### Pitfall 3: Synchronous LLM Calls Block Execution
**What goes wrong:** Combat simulation freezes for 1-2 seconds per creature decision while waiting for LLM response.
**Why it happens:** LLM inference is I/O-bound (network for cloud, compute for local). Synchronous calls block the event loop.
**How to avoid:** Use async LLM providers (AsyncClient for Ollama, AsyncOpenAI for OpenRouter) and await calls. For batch simulations, consider running combats in parallel.
**Warning signs:** 20-run batch takes 40 minutes instead of expected time, single combat simulation is slower than LLM latency would suggest.

### Pitfall 4: Overfitting Prompts to Qwen2.5
**What goes wrong:** Prompt uses Qwen-specific quirks that don't transfer to other 7B models.
**Why it happens:** Each model family has prompt format preferences. Qwen uses ChatML format, others may prefer different structures.
**How to avoid:** Use model-agnostic prompt structure (system message + user message). Let Ollama/OpenRouter apply model-specific chat templates. Test with multiple 7B models.
**Warning signs:** Swapping to different 7B model dramatically reduces output quality or parsing success rate.

### Pitfall 5: No Circuit Breaker for Repeated Failures
**What goes wrong:** Combat spends 30+ seconds retrying LLM calls that consistently fail (model not loaded, API down, rate limited).
**Why it happens:** Retry logic attempts each creature decision independently without tracking failure patterns.
**How to avoid:** Implement combat-level circuit breaker: after N consecutive LLM failures, disable LLM for remainder of combat. Reset on success.
**Warning signs:** Batch simulations hang or take 10x expected time when Ollama is misconfigured.

### Pitfall 6: Token Budget Exceeded by Combat State
**What goes wrong:** Large combats (8+ creatures) with full stat blocks exceed 7B model's effective context (2K-4K tokens for reliable output).
**Why it happens:** Full creature stat blocks are verbose (200-500 tokens each). 8 creatures = 1600-4000 tokens + system prompt.
**How to avoid:** Summarize stat blocks in prompt (show only HP, AC, position, available actions). Full stat block not needed for tactical decision. Include only enemies within 60ft.
**Warning signs:** LLM output quality degrades in large combats, ignores distant creatures, outputs become generic.

## Code Examples

Verified patterns from official sources:

### Ollama Async Chat
```python
# Source: https://github.com/ollama/ollama-python v0.6.1
import asyncio
from ollama import AsyncClient

async def chat_with_ollama():
    client = AsyncClient(host="http://localhost:11434")

    messages = [
        {
            "role": "system",
            "content": "You are a tactical combat agent."
        },
        {
            "role": "user",
            "content": "Choose your action."
        }
    ]

    response = await client.chat(
        model="qwen2.5:7b-instruct",
        messages=messages,
        options={
            "temperature": 0.7,
            "num_predict": 200  # Limit tokens for faster response
        }
    )

    return response['message']['content']

asyncio.run(chat_with_ollama())
```

### OpenRouter via OpenAI SDK
```python
# Source: https://openrouter.ai/docs/quickstart
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="sk-or-v1-..."  # Get from OpenRouter dashboard
)

async def chat_with_openrouter():
    completion = await client.chat.completions.create(
        model="qwen/qwen2.5-coder-7b-instruct",
        messages=[
            {"role": "system", "content": "You are a tactical combat agent."},
            {"role": "user", "content": "Choose your action."}
        ],
        temperature=0.7,
        max_tokens=200
    )

    return completion.choices[0].message.content
```

### Pydantic Strict Validation
```python
# Source: https://docs.pydantic.dev/latest/concepts/validators/
from pydantic import BaseModel, Field, field_validator

class ActionOutput(BaseModel):
    """Strict LLM output validation."""

    action_type: str = Field(
        description="Type of action to take"
    )
    target_id: str | None = Field(
        default=None,
        description="ID of target creature"
    )

    @field_validator('action_type')
    @classmethod
    def validate_action_type(cls, v: str) -> str:
        """Ensure action type is valid."""
        allowed = ['attack', 'move', 'move_and_attack', 'dodge', 'death_save']
        v_clean = v.lower().strip()
        if v_clean not in allowed:
            raise ValueError(
                f"Invalid action_type '{v}'. Must be one of: {allowed}"
            )
        return v_clean

    @field_validator('target_id')
    @classmethod
    def validate_target_format(cls, v: str | None) -> str | None:
        """Ensure target ID is properly formatted if present."""
        if v is None or v.lower() in ['none', 'null', '']:
            return None
        # Allow alphanumeric + underscore
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Invalid target_id format: {v}")
        return v.strip()
```

### Tenacity Retry Decorator
```python
# Source: https://tenacity.readthedocs.io/
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

logger = logging.getLogger(__name__)

@retry(
    # Exponential backoff: 2^x * 1 second, max 10 seconds
    wait=wait_exponential(multiplier=1, min=1, max=10),
    # Stop after 3 attempts
    stop=stop_after_attempt(3),
    # Only retry on specific exceptions
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    # Log before sleeping
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def call_llm_with_retry(provider: LLMProvider, messages: list[dict]) -> str:
    """
    Call LLM with automatic retry on transient failures.

    Retries ConnectionError and TimeoutError with exponential backoff.
    Other exceptions (ValueError, ValidationError) propagate immediately.
    """
    return await provider.chat_completion(messages)
```

### Regex XML Extraction
```python
# Source: Regex pattern for XML tags with malformed handling
import re

def extract_thinking_tag(text: str) -> str:
    """
    Extract content from <thinking> tag, handling malformed XML.

    Handles:
    - Extra whitespace
    - Case variations
    - Missing closing tag (takes rest of text)
    - Extra text before/after tags
    """
    # Try standard extraction
    match = re.search(
        r'<thinking>\s*(.*?)\s*</thinking>',
        text,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        return match.group(1).strip()

    # Fallback: find opening tag, take next 150 words
    match = re.search(r'<thinking>\s*(.+)', text, re.DOTALL | re.IGNORECASE)
    if match:
        content = match.group(1)
        words = content.split()[:150]
        return ' '.join(words)

    return ""

def extract_key_value(text: str, key: str) -> str | None:
    """
    Extract value for uppercase key like 'ACTION: attack'.

    Handles:
    - Leading/trailing whitespace
    - Case variations
    - "none" as null value
    - Missing key (returns None)
    """
    pattern = rf'^{key}:\s*(.+?)(?:\n|$)'
    match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)

    if not match:
        return None

    value = match.group(1).strip()

    # Treat common null values as None
    if value.lower() in ['none', 'null', 'n/a', '-', '']:
        return None

    return value
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| JSON.parse() for LLM output | Pydantic models with validators | 2024-2025 | Automatic validation, retries, type safety |
| LangChain for everything | Purpose-specific libraries (Instructor, tenacity) | 2025-2026 | Reduced dependencies, faster, clearer code |
| Synchronous LLM calls | Async/await with AsyncClient | 2024-2025 | Non-blocking I/O, parallel execution possible |
| Custom retry logic | tenacity library | Stable since 2020 | Exponential backoff with jitter, exception filtering |
| Separate error handling | Circuit breaker pattern | 2025-2026 | Prevents cascade failures, faster fallback |

**Deprecated/outdated:**
- **LangChain's XMLOutputParser for simple formats**: Adds heavy dependencies when regex + Pydantic suffices. Use for complex nested XML only.
- **requests library for LLM APIs**: Official SDKs (ollama, openai) handle retries, streaming, auth better.
- **Manual JSON schema in prompts**: Pydantic can generate JSON schema automatically. Don't duplicate definitions.
- **Instructor's function calling mode for Qwen2.5**: Qwen2.5-7B doesn't support native tool calling. Use text output mode.

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal token budget for combat state prompt**
   - What we know: Qwen2.5-7B-Instruct has 131K context window, but 7B models are most reliable with 2K-4K token prompts
   - What's unclear: Exact threshold where prompt length degrades output quality for tactical decisions
   - Recommendation: Start with 1500-2000 token budget. Test with combats of varying sizes (2v2, 4v4, 8v8). Measure parse success rate vs prompt length. Implement prompt truncation (summarize distant creatures) if needed.

2. **Qwen2.5-7B-Instruct vs Qwen2.5-Coder-7B-Instruct for tactical reasoning**
   - What we know: Coder variant excels at structured output (HumanEval: 84.8) but may be optimized for code, not prose reasoning
   - What's unclear: Whether instruct or coder variant performs better for tactical decision-making with mixed reasoning + structured output
   - Recommendation: Use qwen2.5:7b-instruct for Ollama (general instruct), qwen/qwen2.5-coder-7b-instruct for OpenRouter (cheaper, better structured output). A/B test if quality differs significantly.

3. **Circuit breaker failure threshold**
   - What we know: After N consecutive failures, should disable LLM for combat. Prevents wasted latency.
   - What's unclear: Optimal N value. Too low (N=2) disables prematurely on transient issues. Too high (N=10) wastes 20+ seconds.
   - Recommendation: Start with N=3 failures. Track in production: what's typical failure pattern? Isolated (1 failure, then success) or systematic (Ollama not running)? Adjust threshold based on data.

4. **Creature role archetypes influence on prompt**
   - What we know: AGENT-06 requires creature roles (tank/striker/controller/support) to influence behavior
   - What's unclear: How to represent role in prompt. Explicit instruction ("You are a striker")? Implicit in stat block? Few-shot examples?
   - Recommendation: Add role as system message prefix: "You are a STRIKER. Prioritize high-value targets and maximize damage." Test if LLM behavior changes meaningfully. May need few-shot examples showing role-appropriate decisions.

5. **Streaming vs non-streaming for latency**
   - What we know: Ollama supports streaming, could show partial output earlier
   - What's unclear: Whether streaming reduces perceived latency or complicates parsing (need to accumulate full response before parsing)
   - Recommendation: Start with non-streaming (simpler). Output format requires full response to parse. Streaming only useful if we show real-time thinking (not needed for batch simulation).

## Sources

### Primary (HIGH confidence)
- [Ollama Python GitHub](https://github.com/ollama/ollama-python) - API documentation, v0.6.1 features
- [Ollama Python PyPI](https://pypi.org/project/ollama/) - Installation, version 0.6.1 release
- [OpenRouter Quickstart](https://openrouter.ai/docs/quickstart) - OpenAI SDK integration
- [Qwen2.5-7B-Instruct HuggingFace](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) - Context length (131K), benchmarks
- [Pydantic Validators Documentation](https://docs.pydantic.dev/latest/concepts/validators/) - Custom validators, strict mode
- [Tenacity Documentation](https://tenacity.readthedocs.io/) - Exponential backoff, retry decorators
- [Anthropic XML Tags Documentation](https://docs.anthropic.com/en/docs/use-xml-tags) - Structured prompt format with thinking tags

### Secondary (MEDIUM confidence)
- [Instructor Library](https://python.useinstructor.com/) - Verified WebFetch, Pydantic integration patterns
- [LLM Fallback Patterns 2026](https://medium.com/@mota_ai/building-ai-that-never-goes-down-the-graceful-degradation-playbook-d7428dc34ca3) - Circuit breaker patterns
- [Qwen OpenRouter Pricing](https://pricepertoken.com/pricing-page/provider/qwen) - Cost analysis: $0.03/M input, $0.09/M output
- [Ollama Async Streaming](https://deepwiki.com/ollama/ollama-python/4.6-streaming-responses) - AsyncClient streaming patterns

### Tertiary (LOW confidence)
- [7B Model Prompt Engineering 2026](https://www.analyticsvidhya.com/blog/2026/01/master-prompt-engineering/) - General best practices, output consistency claim (100% for 7B vs 12.5% for 120B)
- [LLM Wargaming Research](https://arxiv.org/html/2403.13433v1) - Tactical decision-making patterns, needs validation for D&D combat
- [XML Parsing Libraries](https://github.com/ocherry341/llm-xml-parser) - Specialized LLM XML parsers, may be overkill for simple format

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified via official docs/PyPI, versions confirmed
- Architecture: HIGH - Patterns verified via official SDK examples, Pydantic docs
- Pitfalls: MEDIUM - Based on common LLM integration patterns and existing agent architecture, not D&D-specific testing

**Research date:** 2026-02-08
**Valid until:** 2026-03-08 (30 days - stable stack, but LLM ecosystem evolves quickly)
