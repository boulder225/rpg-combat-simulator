from dataclasses import dataclass, field, replace


@dataclass
class Attack:
    name: str
    attack_bonus: int
    damage_dice: str
    damage_type: str
    reach: int = 0
    range: int = 0

    @property
    def range_feet(self) -> int:
        return self.reach if self.reach else self.range


@dataclass
class Action:
    name: str
    attacks: list[Attack] = field(default_factory=list)


@dataclass
class Creature:
    id: str
    name: str
    team: str
    position: str
    max_hp: int
    current_hp: int
    ac: int
    speed: int
    actions: list[Action] = field(default_factory=list)
    stable: bool = False


@dataclass
class CombatState:
    creatures: dict
    initiative_order: list

    def update_creature(self, cid, creature):
        new = dict(self.creatures)
        new[cid] = creature
        return replace(self, creatures=new)
