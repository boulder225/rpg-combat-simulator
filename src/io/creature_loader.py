"""Cache-first creature loader with local file precedence and SRD caching."""

from pathlib import Path
from typing import Optional
import frontmatter

from src.domain.creature import Creature
from src.io.markdown import load_creature
from src.io.srd_api import SRDCreatureAPI
from src.domain.srd_models import SRDCreature


class CreatureLoader:
    """
    Cache-first creature loader with three-tier priority:
    1. Local creatures (data/creatures/{name}.md) - highest priority
    2. SRD cache (data/srd-cache/{name}.md)
    3. SRD API with automatic caching
    """

    def __init__(self, cache_dir: str = "data/creatures", srd_cache_dir: str = "data/srd-cache"):
        """
        Initialize the creature loader.

        Args:
            cache_dir: Directory for local creature files (highest priority)
            srd_cache_dir: Directory for cached SRD creatures
        """
        self.cache_dir = Path(cache_dir)
        self.srd_cache_dir = Path(srd_cache_dir)
        self.srd_api = SRDCreatureAPI()

        # Create SRD cache directory if it doesn't exist
        self.srd_cache_dir.mkdir(parents=True, exist_ok=True)

        # Track creature counts for auto-numbering duplicates
        self._creature_counts: dict[str, int] = {}

    def _get_next_creature_id(self, base_name: str) -> str:
        """
        Get next creature ID for duplicate creature names.

        Args:
            base_name: Base creature name

        Returns:
            Unique creature_id with auto-numbering (e.g., "goblin_0", "goblin_1")
        """
        if base_name not in self._creature_counts:
            self._creature_counts[base_name] = 0
        else:
            self._creature_counts[base_name] += 1

        count = self._creature_counts[base_name]
        return f"{base_name}_{count}"

    def _save_to_cache(self, name: str, creature: Creature) -> None:
        """
        Save creature to SRD cache as markdown file.

        Args:
            name: Creature name (used for filename)
            creature: Creature to cache
        """
        cache_path = self.srd_cache_dir / f"{name}.md"

        # Build frontmatter data
        data = {
            "name": creature.name,
            "ac": creature.ac,
            "hp_max": creature.hp_max,
            "speed": creature.speed,
            "initiative_bonus": creature.initiative_bonus,
            "team": creature.team,
            "position": creature.position,
            "ability_scores": {
                "str": creature.ability_scores.str,
                "dex": creature.ability_scores.dex,
                "con": creature.ability_scores.con,
                "int": creature.ability_scores.int_,
                "wis": creature.ability_scores.wis,
                "cha": creature.ability_scores.cha,
            },
            "actions": [
                {
                    "name": action.name,
                    "description": action.description,
                    "attacks": [
                        {
                            "name": attack.name,
                            "attack_bonus": attack.attack_bonus,
                            "damage": {
                                "dice": attack.damage.dice,
                                "damage_type": attack.damage.damage_type,
                            },
                            "reach": attack.reach,
                            "range": attack.range,
                        }
                        for attack in action.attacks
                    ],
                }
                for action in creature.actions
            ],
            "damage_resistances": creature.damage_resistances,
            "damage_immunities": creature.damage_immunities,
            "damage_vulnerabilities": creature.damage_vulnerabilities,
        }

        # Create frontmatter post
        post = frontmatter.Post("", **data)

        # Write to cache
        with open(cache_path, "w") as f:
            f.write(frontmatter.dumps(post))

    def load_creature(
        self, name: str, team: str = "enemy", position: str = "A1"
    ) -> Creature:
        """
        Load creature with cache-first resolution.

        Priority order:
        1. Local creatures directory (data/creatures/{name}.md)
        2. SRD cache directory (data/srd-cache/{name}.md)
        3. SRD API (with automatic caching)

        Args:
            name: Creature name (without .md extension)
            team: Team assignment for the creature
            position: Starting position for the creature

        Returns:
            Creature instance with auto-numbered creature_id if duplicate

        Raises:
            ValueError: If creature not found in any source
        """
        # Normalize name (remove .md extension if present)
        if name.endswith(".md"):
            name = name[:-3]

        # Simple alias mapping for common SRD names where the CLI name is shorter / ambiguous.
        # For example, \"bear\" -> \"Brown Bear\" in the SRD.
        alias_map = {
            "bear": "Brown Bear",
        }
        api_name = alias_map.get(name.lower(), name)

        # Priority 1: Check local creatures directory
        local_path = self.cache_dir / f"{name}.md"
        if local_path.exists():
            creature_id, creature = load_creature(local_path)
            # Override team and position
            creature.team = team
            creature.position = position
            # Auto-number for duplicates
            unique_id = self._get_next_creature_id(creature_id)
            creature.creature_id = unique_id
            return creature

        # Priority 2: Check SRD cache
        srd_cache_path = self.srd_cache_dir / f"{name}.md"
        if srd_cache_path.exists():
            creature_id, creature = load_creature(srd_cache_path)
            # Override team and position
            creature.team = team
            creature.position = position
            # Auto-number for duplicates
            unique_id = self._get_next_creature_id(creature_id)
            creature.creature_id = unique_id
            return creature

        # Priority 3: Fetch from SRD API
        try:
            raw_data = self.srd_api.fetch_monster(api_name)
            srd_creature = SRDCreature(**raw_data)
            creature = srd_creature.to_creature(team=team, position=position)

            # Cache for future use
            self._save_to_cache(name, creature)

            # Auto-number for duplicates
            base_id = creature.creature_id
            unique_id = self._get_next_creature_id(base_id)
            creature.creature_id = unique_id

            return creature

        except ValueError as e:
            raise ValueError(
                f"Creature '{name}' not found in local files, SRD cache, or SRD API. "
                f"Original error: {e}"
            ) from e
