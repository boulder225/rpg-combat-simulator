"""LLM output parser - converts raw LLM text to structured LLMResponse."""

import re
from pydantic import BaseModel, field_validator
from typing import Optional


class LLMResponse(BaseModel):
    """Structured representation of LLM tactical decision output.

    Fields:
        thinking: Content from <thinking> tags (reasoning about the decision)
        action: The main action to take (e.g., "Attack with Scimitar", "Dodge")
        target: Optional target creature (e.g., "Fighter (D4)")
        movement: Optional movement destination (e.g., "from E5 to D5", "D5", "stay")
        bonus: Optional bonus action (e.g., "Hide", "Dash")
        reaction: Optional reaction specification (e.g., "Opportunity attack")
    """

    thinking: str = ""
    action: str
    target: Optional[str] = None
    movement: Optional[str] = None
    bonus: Optional[str] = None
    reaction: Optional[str] = None

    @field_validator('target', 'movement', 'bonus', 'reaction', mode='before')
    @classmethod
    def normalize_none_values(cls, v):
        """Convert various null representations to None."""
        if v is None:
            return None

        # Strip whitespace
        if isinstance(v, str):
            v = v.strip()

        # Check for null-like values
        null_values = {'none', 'stay', 'n/a', '-', ''}
        if isinstance(v, str) and v.lower() in null_values:
            return None

        return v

    @field_validator('thinking', 'action', 'target', 'movement', 'bonus', 'reaction', mode='before')
    @classmethod
    def strip_whitespace(cls, v):
        """Strip leading/trailing whitespace from all string fields."""
        if isinstance(v, str):
            return v.strip()
        return v


def parse_llm_output(text: str) -> LLMResponse:
    """Parse raw LLM output text into structured LLMResponse.

    Handles:
    - Clean formatted output with all fields
    - Missing optional fields (TARGET, MOVEMENT, BONUS, REACTION)
    - Malformed thinking tags (missing close tag)
    - Extra preamble or markdown wrapping
    - Case-insensitive key matching
    - Various null value representations

    Args:
        text: Raw LLM output text

    Returns:
        LLMResponse with parsed fields

    Raises:
        ValueError: If no ACTION field found (completely malformed output)
    """

    # Extract thinking content (handle missing closing tag)
    thinking = ""
    thinking_match = re.search(
        r'<thinking>\s*(.*?)(?:</thinking>|$)',
        text,
        re.DOTALL | re.IGNORECASE
    )
    if thinking_match:
        thinking = thinking_match.group(1).strip()

    # Extract key-value pairs (case-insensitive)
    def extract_field(key: str) -> Optional[str]:
        """Extract a field value from the text."""
        pattern = rf'^\s*{key}\s*:\s*(.+?)(?:\n|$)'
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    # Extract all fields
    action = extract_field('ACTION')
    target = extract_field('TARGET')
    movement = extract_field('MOVEMENT')
    bonus = extract_field('BONUS')
    reaction = extract_field('REACTION')

    # ACTION is required - raise error if missing
    if not action:
        raise ValueError("No ACTION found in LLM output")

    return LLMResponse(
        thinking=thinking,
        action=action,
        target=target,
        movement=movement,
        bonus=bonus,
        reaction=reaction
    )
