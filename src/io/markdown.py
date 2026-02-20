"""Markdown creature file parser using python-frontmatter."""

from pathlib import Path
import frontmatter
from src.domain.creature import (
    Creature,
    Action,
    Attack,
    DamageRoll,
    AbilityScores,
)


def load_creature(filepath: Path) -> tuple[str, Creature]:
    """Load a creature from a markdown file with YAML frontmatter.

    Args:
        filepath: Path to creature markdown file

    Returns:
        Tuple of (creature_id, Creature instance)
        creature_id is derived from filename
    """
    # Parse frontmatter
    post = frontmatter.load(filepath)
    data = post.metadata

    # Parse ability scores
    ability_data = data.get("ability_scores", {})
    ability_scores = AbilityScores(**ability_data) if ability_data else AbilityScores()

    # Parse actions
    actions = []
    for action_data in data.get("actions", []):
        attacks = []
        for attack_data in action_data.get("attacks", []):
            damage_data = attack_data.get("damage", {})
            damage_roll = DamageRoll(
                dice=damage_data.get("dice", "1d4"),
                damage_type=damage_data.get("damage_type", "bludgeoning"),
            )
            attack = Attack(
                name=attack_data["name"],
                attack_bonus=attack_data.get("attack_bonus", 0),
                damage=damage_roll,
                reach=attack_data.get("reach"),
                range=attack_data.get("range"),
            )
            attacks.append(attack)

        # AoE action (e.g. Fireball): optional area_shape, radius_squares, save_ability, save_dc, damage
        area_shape = action_data.get("area_shape")
        radius_squares = action_data.get("radius_squares")
        save_ability = action_data.get("save_ability")
        save_dc = action_data.get("save_dc")
        damage_data = action_data.get("damage")
        aoe_damage = None
        if damage_data and isinstance(damage_data, dict):
            aoe_damage = DamageRoll(
                dice=damage_data.get("dice", "1d6"),
                damage_type=damage_data.get("damage_type", "fire"),
            )
        action = Action(
            name=action_data["name"],
            description=action_data.get("description", ""),
            attacks=attacks,
            area_shape=area_shape,
            radius_squares=radius_squares,
            save_ability=save_ability,
            save_dc=save_dc,
            damage=aoe_damage,
        )
        actions.append(action)

    # Bio: body content after frontmatter (e.g. "A sturdy fighter...") or explicit "bio" in YAML
    bio = data.get("bio") or (post.content.strip() if post.content and post.content.strip() else None)

    # Class/race/level: optional (YAML "class" -> character_class to avoid reserved word)
    character_class = data.get("class") or data.get("character_class")
    race = data.get("race")
    raw_level = data.get("level")
    level = int(raw_level) if raw_level is not None else None

    # Create creature
    creature_id = filepath.stem  # filename without extension
    creature = Creature(
        name=data["name"],
        ac=data["ac"],
        hp_max=data["hp_max"],
        current_hp=data.get("current_hp"),
        speed=data.get("speed", 30),
        initiative_bonus=data.get("initiative_bonus", 0),
        team=data.get("team", ""),
        position=data.get("position", "A1"),
        ability_scores=ability_scores,
        actions=actions,
        damage_resistances=data.get("damage_resistances", []),
        damage_immunities=data.get("damage_immunities", []),
        damage_vulnerabilities=data.get("damage_vulnerabilities", []),
        creature_id=creature_id,
        bio=bio,
        race=race,
        character_class=character_class,
        level=level,
    )

    return creature_id, creature


def load_creatures_from_dir(dirpath: Path) -> dict[str, Creature]:
    """Load all creatures from markdown files in a directory.

    Args:
        dirpath: Path to directory containing creature markdown files

    Returns:
        Dict of creature_id -> Creature
    """
    creatures = {}
    for filepath in Path(dirpath).glob("*.md"):
        creature_id, creature = load_creature(filepath)
        creatures[creature_id] = creature
    return creatures


def load_creature_files(filepaths: list[Path]) -> dict[str, Creature]:
    """Load creatures from a list of markdown files.

    Args:
        filepaths: List of paths to creature markdown files

    Returns:
        Dict of creature_id -> Creature
    """
    creatures = {}
    for filepath in filepaths:
        creature_id, creature = load_creature(filepath)
        creatures[creature_id] = creature
    return creatures
