from dataclasses import dataclass, replace


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
    actions: list
    stable: bool = False


@dataclass
class CombatState:
    creatures: dict
    initiative_order: list

    def update_creature(self, cid, creature):
        new = dict(self.creatures)
        new[cid] = creature
        return replace(self, creatures=new)
