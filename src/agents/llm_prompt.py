"""Combat prompt builder for LLM agents with role archetypes."""

from src.domain.combat_state import CombatState
from src.domain.distance import distance_in_feet


# Role-based system prompts for tactical archetypes (AGENT-06)
ROLE_PROMPTS = {
    "tank": "You are a TANK. Prioritize protecting weaker allies. Position yourself between enemies and your team. Use defensive abilities. Draw attacks to yourself.",
    "striker": "You are a STRIKER. Prioritize maximum damage on high-value targets. Focus fire on wounded enemies. Use positioning for advantage.",
    "controller": "You are a CONTROLLER. Prioritize area denial and crowd control. Target clusters of enemies. Limit enemy movement and options.",
    "support": "You are a SUPPORT. Prioritize keeping allies alive and buffed. Stay at range. Use healing and buff abilities before attacking.",
    "default": "You are a tactical monster agent. Maximize your side's chance of victory.",
}


def build_prompt(
    state: CombatState, creature_id: str, role: str = "default"
) -> list[dict]:
    """Build LLM prompt messages from combat state.

    Args:
        state: Current combat state
        creature_id: ID of the creature taking its turn
        role: Role archetype (tank/striker/controller/support/default)

    Returns:
        List of message dicts: [system_message, user_message]
    """
    creature = state.creatures[creature_id]

    # Build system prompt with role archetype + rules + output format
    role_instruction = ROLE_PROMPTS.get(role, ROLE_PROMPTS["default"])

    system_prompt = f"""{role_instruction}

Decide ONLY from your current shape (never the ideal):
- Your current shape is: the HP, position, and actions listed for you this turn—nothing else. Do not assume full HP, a different position, or abilities you do not have. Parties and enemies must take strategic decisions according to this current shape, not an ideal or past state.
- Reconsider strategy every round from scratch. Tactics must align with what you are right now (e.g. low HP → survive/kite; wounded enemies → focus fire). If your shape or the situation changed, adapt immediately.

Survival and strategy (use current shape and this turn's state only):
- Choose the best strategy to SURVIVE and WIN given your current shape, equipment, and enemy strength. "Current shape" = the stats, name, and actions listed for you this turn—tactics must fit this form only.
- If a character bio or background is provided, let it influence your choices within the rules and your current stat block.
- Equipment: Use bow/ranged when you have the range and are fragile or outnumbered in melee; use sword/melee when in reach and you can take the hit. Kite with ranged when low HP; close in when you are tougher than the target.
- When outmatched (low HP, outnumbered, or enemies much stronger): consider Hide, Disengage, Dash, or moving to cover instead of fighting. Running away or repositioning to survive is valid.
- Assess enemy strength this turn: compare total HP and numbers (your side vs theirs), who is the biggest threat, who is wounded. Act to maximize your side's survival and victory—not just this round's damage.

Fixed rules you MUST follow:
- Use ONLY actions, bonus actions, reactions, legendary/lair actions present in your stat block.
- Respect reach, range, concentration, somatic/material components (if hands free).
- Apply advantage/disadvantage when obvious (cover, conditions, Help action, etc.).
- Never exceed remaining movement speed.
- Opportunity attacks only when reaction available and trigger valid.
- Do not invent abilities or lie about average damage / probabilities.

MANDATORY output format ONLY (no extra text):

<thinking>
Short, brutal reasoning (max 120–150 words). Use only your CURRENT shape this turn: your listed HP, position, and actions. How do they fit the situation; enemy strength and threats; survival vs attack; which action fits this form (bow vs sword, etc.). Do not assume full HP, different position, or abilities you do not have. Do not reuse last round's plan—decide from this turn's state only.
</thinking>

ACTION:     [action name]
TARGET:     [target creature name, or for AoE the center cell e.g. D4]
MOVEMENT:   [new position or "stay"]
BONUS:      [bonus action or "none"]
REACTION:   [reaction setup or "none"]"""

    # Build user prompt with combat state
    user_prompt = _build_turn_prompt(state, creature_id)

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _build_turn_prompt(state: CombatState, creature_id: str) -> str:
    """Build the turn-specific user prompt with combat state.

    Args:
        state: Current combat state
        creature_id: ID of the creature taking its turn

    Returns:
        Formatted combat state string
    """
    creature = state.creatures[creature_id]

    # Separate creatures by team
    enemies = []
    allies = []
    for cid, c in state.creatures.items():
        if c.current_hp <= 0:
            continue  # Skip dead creatures
        if c.team != creature.team:
            enemies.append((cid, c))
        else:
            allies.append((cid, c))

    # Build enemy team section
    enemy_lines = []
    for cid, enemy in enemies:
        enemy_lines.append(
            f"- {enemy.name}  HP {enemy.current_hp}/{enemy.hp_max}  AC {enemy.ac}  Pos: {enemy.position}"
        )
    enemy_section = "\n".join(enemy_lines) if enemy_lines else "- None"

    # Build ally team section (mark current creature with "You")
    ally_lines = []
    for cid, ally in allies:
        if cid == creature_id:
            ally_lines.append(
                f"- You ({ally.name})  HP {ally.current_hp}/{ally.hp_max}  AC {ally.ac}  Pos: {ally.position}"
            )
        else:
            ally_lines.append(
                f"- {ally.name}  HP {ally.current_hp}/{ally.hp_max}  AC {ally.ac}  Pos: {ally.position}"
            )
    ally_section = "\n".join(ally_lines) if ally_lines else "- None"

    # Build available actions section
    action_lines = []
    for action in creature.actions:
        if getattr(action, "is_aoe", False):
            d = action.damage
            dmg_str = f"{d.dice} {d.damage_type}" if d else "—"
            action_lines.append(
                f"- {action.name}: AoE {action.area_shape} radius {action.radius_squares} squares, "
                f"{action.save_ability or 'DEX'} save DC {action.save_dc}, {dmg_str}. TARGET = center cell (e.g. D4)."
            )
        elif action.attacks:
            # Show attack details
            attack_details = []
            for attack in action.attacks:
                attack_details.append(
                    f"{attack.name} +{attack.attack_bonus}, {attack.damage.dice} {attack.damage.damage_type}, "
                    f"{'reach' if attack.reach else 'range'} {attack.range_feet}ft"
                )
            action_lines.append(f"- {action.name}: {'; '.join(attack_details)}")
        else:
            # Non-attack action
            action_lines.append(f"- {action.name}")
    actions_section = (
        "\n".join(action_lines) if action_lines else "- No actions available"
    )

    # Build tactical notes (distances to enemies)
    tactical_lines = []
    for cid, enemy in enemies:
        dist = distance_in_feet(creature.position, enemy.position)
        tactical_lines.append(f"- Distance to {enemy.name}: {dist}ft")
    tactical_section = (
        "\n".join(tactical_lines) if tactical_lines else "- No enemies in range"
    )

    # Strategy context: strength comparison and equipment summary for survival reasoning
    enemy_hp_total = sum(e.current_hp for _, e in enemies)
    ally_hp_total = sum(a.current_hp for _, a in allies)
    melee_attacks = []
    ranged_attacks = []
    for a in creature.actions:
        for atk in a.attacks or []:
            if atk.reach is not None:
                melee_attacks.append(f"{atk.name} ({atk.range_feet}ft)")
            elif atk.range is not None:
                ranged_attacks.append(f"{atk.name} ({atk.range_feet}ft)")
    equipment_note = "Melee: " + (", ".join(melee_attacks) if melee_attacks else "none")
    equipment_note += ". Ranged: " + (", ".join(ranged_attacks) if ranged_attacks else "none")
    strategy_note = f"Total HP: your side {ally_hp_total}, enemies {enemy_hp_total}. Numbers: {len(allies)} vs {len(enemies)}. {equipment_note}."

    # Class/race/level line for identity (e.g. "Dragonborn Paladin, level 5")
    identity_parts = []
    if getattr(creature, "race", None) and creature.race.strip():
        identity_parts.append(creature.race.strip())
    if getattr(creature, "character_class", None) and creature.character_class.strip():
        identity_parts.append(creature.character_class.strip())
    if getattr(creature, "level", None) is not None and creature.level >= 1:
        identity_parts.append(f"level {creature.level}")
    identity_line = f" ({', '.join(identity_parts)})" if identity_parts else ""

    # Current shape: explicit so strategy is tied to this form this turn (no ideal state)
    current_shape_note = (
        f"Current shape (this turn—decide from this only, not full HP or ideal position): "
        f"{creature.name}{identity_line} | HP {creature.current_hp}/{creature.hp_max} | "
        f"AC {creature.ac} | Speed {creature.speed}ft | Pos: {creature.position}. "
        f"The actions below are what you have in this form—choose tactics that fit this current shape only."
    )
    bio_section = ""
    if getattr(creature, "bio", None) and creature.bio.strip():
        bio_section = f"\n=== Character bio (influence your tactics to match) ===\n{creature.bio.strip()}\n"

    # Assemble full prompt
    prompt = f"""Round {state.round} | Your turn: {creature.name} (current position: {creature.position})

=== Current shape (reconsider strategy for this form every round) ===
{current_shape_note}
{bio_section}

=== Combat State ===
Enemy team:
{enemy_section}

Your team:
{ally_section}

Your stats this turn:
Speed: {creature.speed}ft  Remaining movement: {creature.speed}ft
Available actions (this shape only):
{actions_section}

Strategy context: {strategy_note}

Tactical notes:
{tactical_section}"""

    return prompt
