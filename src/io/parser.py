import yaml
from pathlib import Path
from src.domain.combat_state import Creature, Action, Attack


def parse_creature_file(filepath: str, creature_id: str) -> Creature:
    text = Path(filepath).read_text()
    parts = text.split("---")
    if len(parts) < 3:
        raise ValueError(f"Invalid creature file (missing YAML frontmatter): {filepath}")
    front = yaml.safe_load(parts[1])

    actions = []
    for act_data in front.get("actions", []):
        attacks = []
        for atk_data in act_data.get("attacks", []):
            dmg = atk_data.get("damage", {})
            attacks.append(Attack(
                name=atk_data["name"],
                attack_bonus=atk_data.get("attack_bonus", 0),
                damage_dice=dmg.get("dice", "1d4"),
                damage_type=dmg.get("damage_type", "bludgeoning"),
                reach=atk_data.get("reach", 0),
                range=atk_data.get("range", 0),
            ))
        actions.append(Action(name=act_data["name"], attacks=attacks))

    return Creature(
        id=creature_id,
        name=front["name"],
        team="",  # set by caller
        position=front.get("position", "A1"),
        max_hp=front["hp_max"],
        current_hp=front["hp_max"],
        ac=front["ac"],
        speed=front.get("speed", 30),
        actions=actions,
    )
