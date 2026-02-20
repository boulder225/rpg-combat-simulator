"""Pydantic models for D&D 5e creatures, actions, and attacks."""

from pydantic import BaseModel, computed_field, model_validator
from typing import Literal, Optional


class AbilityScores(BaseModel):
    """D&D 5e ability scores (STR, DEX, CON, INT, WIS, CHA)."""

    str: int = 10
    dex: int = 10
    con: int = 10
    int_: int = 10
    wis: int = 10
    cha: int = 10

    @staticmethod
    def modifier(score: int) -> int:
        """Calculate ability modifier from ability score."""
        return (score - 10) // 2

    def get_modifier(self, ability: str) -> int:
        """Get modifier for a specific ability."""
        score = getattr(self, ability, 10)
        return self.modifier(score)


class DeathSaves(BaseModel):
    """Death saving throw tracking."""

    model_config = {"frozen": True}

    successes: int = 0
    failures: int = 0
    stable: bool = False


class DamageRoll(BaseModel):
    """Represents a damage roll with dice notation and damage type."""

    dice: str  # e.g., "1d6+3"
    damage_type: str  # e.g., "slashing", "fire"


class Attack(BaseModel):
    """Represents a single attack (melee or ranged)."""

    name: str
    attack_bonus: int
    damage: DamageRoll
    reach: Optional[int] = None  # in feet, for melee
    range: Optional[int] = None  # in feet, for ranged

    @computed_field
    @property
    def range_feet(self) -> int:
        """Get the effective range in feet (prefer reach for melee)."""
        if self.reach is not None:
            return self.reach
        if self.range is not None:
            return self.range
        return 0


class Action(BaseModel):
    """Represents a creature action (can contain multiple attacks for Multiattack or AoE)."""

    name: str
    description: str = ""
    attacks: list[Attack] = []
    # AoE (e.g. Fireball): sphere, save, damage
    area_shape: Optional[Literal["sphere"]] = None
    radius_squares: Optional[int] = None
    save_ability: Optional[str] = None  # e.g. "dex"
    save_dc: Optional[int] = None
    damage: Optional[DamageRoll] = None  # for AoE damage

    @computed_field
    @property
    def is_multiattack(self) -> bool:
        """Check if this is a Multiattack action."""
        return len(self.attacks) > 1

    @computed_field
    @property
    def is_aoe(self) -> bool:
        """Check if this action is an area-of-effect (e.g. Fireball)."""
        return self.area_shape is not None and self.radius_squares is not None


class Creature(BaseModel):
    """Represents a D&D 5e creature with all combat-relevant stats."""

    name: str
    ac: int
    hp_max: int
    current_hp: Optional[int] = None
    speed: int = 30
    initiative_bonus: int = 0
    team: str
    position: str = "A1"
    ability_scores: AbilityScores = AbilityScores()
    actions: list[Action] = []
    damage_resistances: list[str] = []
    damage_immunities: list[str] = []
    damage_vulnerabilities: list[str] = []
    death_saves: DeathSaves = DeathSaves()
    creature_id: str = ""
    bio: Optional[str] = None  # Optional character background; influences tactical strategy when present
    race: Optional[str] = None  # e.g. Dragonborn, Elf
    character_class: Optional[str] = None  # e.g. Paladin, Fighter (YAML key "class" in markdown)
    level: Optional[int] = None  # Character or creature level (e.g. 1–20); for display and prompts only, no auto-scaling

    @model_validator(mode="after")
    def set_current_hp_default(self):
        """Set current_hp to hp_max if not provided."""
        if self.current_hp is None:
            self.current_hp = self.hp_max
        return self
