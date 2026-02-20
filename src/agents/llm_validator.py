"""LLM move validator - validates LLM responses against combat state."""

import re
from typing import Optional
from src.agents.llm_parser import LLMResponse
from src.agents.base import AgentAction
from src.domain.combat_state import CombatState
from src.domain.distance import distance_in_feet


def _parse_movement_destination(movement_text: Optional[str]) -> Optional[str]:
    """Parse movement text to extract destination coordinate.

    Handles:
    - "from E5 to D5" -> "D5"
    - "D5" -> "D5"
    - "stay" / None -> None

    Args:
        movement_text: Raw movement text from LLM

    Returns:
        Destination coordinate or None
    """
    if not movement_text:
        return None

    # Check for "from X to Y" format
    from_to_match = re.search(r'to\s+([A-Z]\d+)', movement_text, re.IGNORECASE)
    if from_to_match:
        return from_to_match.group(1).upper()

    # Check for bare coordinate (e.g., "D5")
    coord_match = re.search(r'^([A-Z]\d+)$', movement_text.strip(), re.IGNORECASE)
    if coord_match:
        return coord_match.group(1).upper()

    return None


def _parse_cell(text: Optional[str]) -> Optional[str]:
    """If text looks like a grid cell (e.g. A1, D4), return it normalized; else None."""
    if not text:
        return None
    m = re.match(r"^\s*([A-Za-z])\s*(\d+)\s*$", text.strip())
    if m:
        return m.group(1).upper() + m.group(2)
    return None


def _resolve_target_id(target_text: Optional[str], state: CombatState) -> Optional[str]:
    """Resolve target name/text to creature_id.

    Handles:
    - "Fighter (D4)" -> strips position, matches "Fighter"
    - Case-insensitive matching
    - Returns creature_id (e.g., "fighter_0")

    Args:
        target_text: Raw target text from LLM
        state: Current combat state

    Returns:
        creature_id or None if not found
    """
    if not target_text:
        return None

    # Strip parenthetical position info: "Fighter (D4)" -> "Fighter"
    clean_target = re.sub(r'\s*\([^)]+\)\s*', '', target_text).strip()

    # Case-insensitive match against creature names
    for creature_id, creature in state.creatures.items():
        if creature.name.lower() == clean_target.lower():
            return creature_id

    return None


def _resolve_action_name(action_text: str, creature_id: str, state: CombatState) -> Optional[str]:
    """Resolve action text to actual action name.

    Fuzzy matching:
    - If action text contains "multiattack" -> find Multiattack action
    - If action text contains an attack name -> match that attack
    - If action text is "dodge"/"Dodge" -> return "dodge"

    Args:
        action_text: Raw action text from LLM
        creature_id: ID of creature performing action
        state: Current combat state

    Returns:
        Action name or "dodge" or None if not found
    """
    action_lower = action_text.lower()

    # Special case: dodge
    if action_lower == "dodge":
        return "dodge"

    creature = state.creatures[creature_id]

    # Check for multiattack
    if "multiattack" in action_lower:
        for action in creature.actions:
            if action.is_multiattack:
                return action.name

    # Try to match action/attack names
    for action in creature.actions:
        # Check action name
        if action.name.lower() in action_lower:
            return action.name

        # Check attack names within action
        for attack in action.attacks:
            if attack.name.lower() in action_lower:
                return action.name

    return None


def validate_move(
    response: LLMResponse,
    state: CombatState,
    creature_id: str
) -> tuple[bool, str]:
    """Validate LLM response against combat state rules.

    Checks:
    - Movement distance <= creature speed
    - Target exists and is alive
    - Attack range from final position (after movement)
    - Attack actions have targets

    Args:
        response: Parsed LLM response
        state: Current combat state
        creature_id: ID of creature making the move

    Returns:
        Tuple of (valid: bool, error_message: str)
        If valid, error_message is empty string
    """
    creature = state.creatures[creature_id]
    current_position = creature.position

    # Parse movement destination
    move_to = _parse_movement_destination(response.movement)
    final_position = move_to if move_to else current_position

    # Validate movement distance
    if move_to:
        move_distance = distance_in_feet(current_position, move_to)
        if move_distance > creature.speed:
            return (False, f"Movement from {current_position} to {move_to} ({move_distance}ft) exceeds speed ({creature.speed}ft)")

    # Resolve action
    action_name = _resolve_action_name(response.action, creature_id, state)

    # If it's dodge, no further validation needed
    if action_name == "dodge":
        return (True, "")

    # For attack actions, validate target (or AoE center)
    if action_name and action_name != "dodge":
        action_obj = None
        for a in creature.actions:
            if a.name == action_name:
                action_obj = a
                break
        if action_obj and getattr(action_obj, "is_aoe", False):
            # AoE: target is optional center cell; if provided, must look like a cell
            if response.target and not _parse_cell(response.target):
                return (False, "AoE target should be a cell (e.g. D4)")
            return (True, "")

        # Attack requires target creature
        if not response.target:
            return (False, "Attack requires a target")

        # Resolve target
        target_id = _resolve_target_id(response.target, state)
        if not target_id:
            return (False, f"Target '{response.target}' does not exist")

        target = state.creatures[target_id]

        # Check if target is alive
        if target.current_hp <= 0:
            return (False, f"Target '{target.name}' is already dead")

        # Find the attack range
        # Get the action to check attack range
        attack_range = 5  # Default melee reach
        for action in creature.actions:
            if action.name == action_name:
                if action.attacks:
                    # Use first attack's range (they should be similar)
                    attack_range = action.attacks[0].range_feet
                break

        # Check if target is in range from final position
        target_distance = distance_in_feet(final_position, target.position)
        if target_distance > attack_range:
            return (False, f"Target '{target.name}' at {target.position} is {target_distance}ft away (out of range: {attack_range}ft) from final position {final_position}")

    return (True, "")


def to_agent_action(
    response: LLMResponse,
    state: CombatState,
    creature_id: str
) -> AgentAction:
    """Convert validated LLM response to AgentAction.

    Args:
        response: Parsed LLM response
        state: Current combat state
        creature_id: ID of creature making the move

    Returns:
        AgentAction with appropriate action_type and fields

    Raises:
        ValueError: If move is invalid
    """
    # Validate first
    valid, error = validate_move(response, state, creature_id)
    if not valid:
        raise ValueError(f"Invalid move: {error}")

    # Parse movement
    move_to = _parse_movement_destination(response.movement)

    # Resolve action
    action_name = _resolve_action_name(response.action, creature_id, state)

    # AoE: if this action is AoE, target is the center cell (target_position)
    creature = state.creatures[creature_id]
    action_obj = None
    for a in creature.actions:
        if a.name == action_name:
            action_obj = a
            break
    if action_obj and getattr(action_obj, "is_aoe", False):
        target_position = _parse_cell(response.target) or creature.position
        return AgentAction(
            action_type="aoe",
            attack_name=action_name,
            target_id=None,
            target_position=target_position,
            move_to=move_to,
            description=response.thinking,
            strategy_summary=response.thinking or None,
        )

    # Resolve target (creature)
    target_id = _resolve_target_id(response.target, state)

    # Determine action_type
    if action_name == "dodge":
        action_type = "dodge"
        attack_name = None
    elif move_to and action_name:
        action_type = "move_and_attack"
        attack_name = action_name
    elif move_to:
        action_type = "move"
        attack_name = None
    elif action_name:
        action_type = "attack"
        attack_name = action_name
    else:
        # Default to dodge if nothing specified
        action_type = "dodge"
        attack_name = None

    return AgentAction(
        action_type=action_type,
        attack_name=attack_name,
        target_id=target_id,
        target_position=None,
        move_to=move_to,
        description=response.thinking,
        strategy_summary=response.thinking or None,
    )
