import random


class AttackResult:
    def __init__(self, total, ac):
        self.total = total
        self.ac = ac
        self.is_hit = total >= ac
        self.is_critical = False


def make_attack_roll(bonus, ac, _):
    roll = random.randint(1, 20)
    return AttackResult(roll + bonus, ac)


def roll_damage_for_attack(damage, is_critical=False):
    return damage


def apply_damage(creature, dmg, _type):
    creature.current_hp = max(0, creature.current_hp - dmg)
    return creature


def make_death_save(creature):
    creature.stable = True
    return creature
