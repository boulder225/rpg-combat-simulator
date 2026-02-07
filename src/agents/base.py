from dataclasses import dataclass
from typing import Protocol, Optional


@dataclass(frozen=True)
class AgentAction:
    action_type: str
    attack_name: Optional[str] = None
    target_id: Optional[str] = None
    move_to: Optional[str] = None
    description: str = ""


class BaseAgent(Protocol):
    def choose_action(self, state, creature_id: str) -> AgentAction:
        ...
