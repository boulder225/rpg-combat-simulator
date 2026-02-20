from dataclasses import dataclass
from typing import Protocol, Optional


@dataclass(frozen=True)
class AgentAction:
    action_type: str
    attack_name: Optional[str] = None
    target_id: Optional[str] = None
    target_position: Optional[str] = None  # For AoE: center cell (e.g. "D4")
    move_to: Optional[str] = None
    description: str = ""
    strategy_summary: Optional[str] = None  # For end-of-fight strategy evolution (LLM thinking or heuristic label)


class BaseAgent(Protocol):
    def choose_action(self, state, creature_id: str) -> AgentAction:
        ...
