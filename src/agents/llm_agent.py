"""LLM Agent orchestrator with circuit breaker and heuristic fallback."""

import logging
from tenacity import RetryError, retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.agents.base import BaseAgent
from src.agents.heuristic import HeuristicAgent
from src.agents.llm_parser import parse_llm_output
from src.agents.llm_validator import validate_move, to_agent_action
from src.agents.llm_providers import LLMProvider
from src.agents.llm_prompt import build_prompt
from src.domain.combat_state import CombatState

logger = logging.getLogger("dnd_sim.llm_agent")


class LLMAgent(BaseAgent):
    """LLM-powered agent with circuit breaker and heuristic fallback.
    
    The agent calls the LLM provider, parses the response, validates the move,
    and returns an AgentAction. If any step fails, it falls back to the
    HeuristicAgent. After 3 consecutive failures, the circuit breaker opens
    and the agent uses the heuristic for the rest of the combat.
    """
    
    def __init__(
        self,
        provider: LLMProvider,
        model: str = "qwen2.5:7b-instruct",
        role: str = "default",
        max_retries: int = 2,
        circuit_breaker_threshold: int = 3,
    ):
        """Initialize LLMAgent.
        
        Args:
            provider: LLM provider instance (Ollama or OpenRouter)
            model: LLM model name
            role: Creature role archetype for prompt (tank/striker/controller/support/default)
            max_retries: Maximum retries per LLM call for transient errors
            circuit_breaker_threshold: Consecutive failures before disabling LLM
        """
        self.provider = provider
        self.fallback = HeuristicAgent()
        self.model = model
        self.role = role
        self.max_retries = max_retries
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self._consecutive_failures = 0
        self._circuit_open = False
    
    def reset_circuit_breaker(self):
        """Reset circuit breaker between combat runs."""
        self._consecutive_failures = 0
        self._circuit_open = False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError))
    )
    def _call_provider(self, messages):
        """Call LLM provider with retry logic."""
        return self.provider.chat_completion(
            messages=messages,
            model=self.model,
            temperature=0.7,
            max_tokens=600
        )
    
    def choose_action(self, state: CombatState, creature_id: str) -> "AgentAction":
        """Choose action using LLM or fallback to heuristic.
        
        Args:
            state: Current combat state
            creature_id: ID of creature making the decision
            
        Returns:
            AgentAction with the chosen action
        """
        # Circuit breaker check
        if self._circuit_open:
            logger.warning("Circuit breaker open, using heuristic fallback")
            return self.fallback.choose_action(state, creature_id)
        
        # Death save shortcut
        if state.creatures[creature_id].current_hp <= 0:
            return self.fallback.choose_action(state, creature_id)
        
        try:
            # Build prompt
            messages = build_prompt(state, creature_id, self.role)
            logger.info(f"Calling LLM for {creature_id} with role {self.role}")
            
            # Call LLM with retry
            response_text = self._call_provider(messages)
            logger.debug(f"LLM response: {response_text[:200]}...")
            
            # Parse response
            parsed_response = parse_llm_output(response_text)
            logger.debug(f"Parsed response: {parsed_response}")
            
            # Validate move
            valid, error = validate_move(parsed_response, state, creature_id)
            if not valid:
                logger.warning(f"Invalid move: {error}")
                raise ValueError(f"Invalid move: {error}")
            
            # Convert to action
            action = to_agent_action(parsed_response, state, creature_id)
            self._consecutive_failures = 0  # Reset on success
            logger.info(f"LLM action chosen: {action}")
            return action
            
        except Exception as e:
            msg = _format_llm_error(e)
            logger.warning(f"LLM agent failed: {msg}")
            self._consecutive_failures += 1

            if self._consecutive_failures >= self.circuit_breaker_threshold:
                self._circuit_open = True
                logger.warning("Circuit breaker opened: falling back to heuristic for remaining combat")

            return self.fallback.choose_action(state, creature_id)


def _format_llm_error(e: Exception) -> str:
    """Turn LLM/provider errors into a short, actionable message."""
    if isinstance(e, RetryError) and e.last_attempt is not None:
        try:
            exc = e.last_attempt.exception()
        except Exception:
            exc = None
        if exc is not None:
            e = exc
    text = str(e)
    if not text or text.strip() == "":
        text = type(e).__name__
    if isinstance(e, (ConnectionError, OSError)):
        return f"{text}. Is the LLM service running? (Ollama: ollama serve; then ollama pull <model>)"
    return text