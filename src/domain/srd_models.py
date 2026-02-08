"""Pydantic models for SRD API responses and transformation to standard creature format."""

import re
from typing import Optional

from pydantic import BaseModel, Field

from src.domain.creature import (
    AbilityScores,
    Action,
    Attack,
    Creature,
    DamageRoll,
)


class SRDDamageType(BaseModel):
    """SRD API damage type reference."""

    index: str
    name: str
    url: str


class SRDDamage(BaseModel):
    """SRD API damage specification."""

    damage_type: SRDDamageType
    damage_dice: str


class SRDMultiattackAction(BaseModel):
    """SRD API multiattack sub-action reference."""

    action_name: str
    count: str
    type: str


class SRDAction(BaseModel):
    """SRD API action model."""

    name: str
    desc: str
    attack_bonus: Optional[int] = None
    damage: list[SRDDamage] = []
    actions: list[SRDMultiattackAction] = []  # For Multiattack actions
    multiattack_type: Optional[str] = None


class SRDArmorClass(BaseModel):
    """SRD API armor class specification."""

    type: str
    value: int


class SRDSpeed(BaseModel):
    """SRD API speed specification."""

    walk: Optional[str] = None
    fly: Optional[str] = None
    swim: Optional[str] = None


class SRDCreature(BaseModel):
    """
    SRD API creature model.

    Validates and parses JSON responses from dnd5eapi.co.
    """

    index: str
    name: str
    size: str
    type: str
    alignment: str
    armor_class: list[SRDArmorClass]
    hit_points: int
    hit_dice: str
    speed: SRDSpeed
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    damage_vulnerabilities: list[str] = []
    damage_resistances: list[str] = []
    damage_immunities: list[str] = []
    actions: list[SRDAction] = []
    challenge_rating: float = Field(alias="challenge_rating")

    @staticmethod
    def _extract_reach_from_description(desc: str) -> Optional[int]:
        """
        Extract reach in feet from action description.

        Args:
            desc: Action description (e.g., "...reach 5 ft...")

        Returns:
            Reach in feet, or None if not found
        """
        match = re.search(r"reach (\d+) ft", desc, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def _extract_range_from_description(desc: str) -> Optional[int]:
        """
        Extract range in feet from action description.

        Args:
            desc: Action description (e.g., "...range 80/320 ft...")

        Returns:
            Normal range in feet (not max range), or None if not found
        """
        # Match "range X/Y ft" or "range X ft"
        match = re.search(r"range (\d+)(?:/\d+)? ft", desc, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    def _transform_action_to_attack(self, srd_action: SRDAction) -> Optional[Attack]:
        """
        Transform an SRD action to a standard Attack.

        Args:
            srd_action: SRD API action

        Returns:
            Attack object, or None if action cannot be parsed
        """
        # Skip actions without attack bonus (not weapon attacks)
        if srd_action.attack_bonus is None or not srd_action.damage:
            return None

        # Extract reach or range from description
        reach = self._extract_reach_from_description(srd_action.desc)
        range_normal = self._extract_range_from_description(srd_action.desc)

        # Use first damage entry (most actions have single damage type)
        primary_damage = srd_action.damage[0]

        return Attack(
            name=srd_action.name,
            attack_bonus=srd_action.attack_bonus,
            damage=DamageRoll(
                dice=primary_damage.damage_dice,
                damage_type=primary_damage.damage_type.index,
            ),
            reach=reach,
            range=range_normal,
        )

    def _transform_multiattack(self, multiattack_action: SRDAction) -> Optional[Action]:
        """
        Transform a Multiattack action by resolving sub-action references.

        Args:
            multiattack_action: SRD Multiattack action

        Returns:
            Action with multiple attacks, or None if cannot be resolved
        """
        attacks = []
        action_map = {action.name: action for action in self.actions}

        for sub_action_ref in multiattack_action.actions:
            # Find the referenced action
            action_name = sub_action_ref.action_name
            referenced_action = action_map.get(action_name)

            if referenced_action:
                attack = self._transform_action_to_attack(referenced_action)
                if attack:
                    # Add attack for each count (usually 1, but could be "2")
                    count = int(sub_action_ref.count) if sub_action_ref.count.isdigit() else 1
                    for _ in range(count):
                        attacks.append(attack)

        if attacks:
            return Action(
                name=multiattack_action.name,
                description=multiattack_action.desc,
                attacks=attacks,
            )
        return None

    def to_creature(self, team: str = "enemy", position: str = "A1") -> Creature:
        """
        Transform SRD creature data to standard Creature format.

        Args:
            team: Team assignment (default "enemy")
            position: Starting position (default "A1")

        Returns:
            Standard Creature object
        """
        # Extract AC value (use first armor_class entry)
        ac = self.armor_class[0].value if self.armor_class else 10

        # Extract speed (prefer walking speed)
        speed_str = self.speed.walk or "30 ft."
        speed_value = int(re.search(r"\d+", speed_str).group()) if re.search(r"\d+", speed_str) else 30

        # Calculate initiative bonus from DEX
        initiative_bonus = AbilityScores.modifier(self.dexterity)

        # Build ability scores
        ability_scores = AbilityScores(
            str=self.strength,
            dex=self.dexterity,
            con=self.constitution,
            int_=self.intelligence,
            wis=self.wisdom,
            cha=self.charisma,
        )

        # Transform actions to standard format
        actions: list[Action] = []

        # Separate multiattack and regular actions
        multiattack = None
        regular_actions = []

        for srd_action in self.actions:
            if srd_action.multiattack_type is not None:
                # This is a Multiattack action
                multiattack = self._transform_multiattack(srd_action)
            else:
                # Regular action
                attack = self._transform_action_to_attack(srd_action)
                if attack:
                    regular_actions.append(
                        Action(
                            name=srd_action.name,
                            description=srd_action.desc,
                            attacks=[attack],
                        )
                    )

        # Add Multiattack first if it exists, then regular actions
        if multiattack:
            actions.append(multiattack)
        actions.extend(regular_actions)

        return Creature(
            name=self.name,
            ac=ac,
            hp_max=self.hit_points,
            speed=speed_value,
            initiative_bonus=initiative_bonus,
            team=team,
            position=position,
            ability_scores=ability_scores,
            actions=actions,
            damage_resistances=self.damage_resistances,
            damage_immunities=self.damage_immunities,
            damage_vulnerabilities=self.damage_vulnerabilities,
            creature_id=self.index,
        )
