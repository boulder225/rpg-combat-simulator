import random
import re
from src.domain.dice import AdvantageState, roll_d20, roll_damage


class AttackResult:
    """Result of an attack roll in D&D 5e."""

    def __init__(self, natural_roll, bonus, ac, is_critical=False, is_auto_miss=False):
        self.natural_roll = natural_roll
        self.bonus = bonus
        self.total = natural_roll + bonus
        self.ac = ac
        self.is_critical = is_critical
        self.is_auto_miss = is_auto_miss

        # Determine hit: natural 20 always hits, natural 1 always misses
        if is_auto_miss:
            self.is_hit = False
        elif is_critical:
            self.is_hit = True
        else:
            self.is_hit = self.total >= ac

        # Generate description
        if is_critical:
            self.description = f"Natural 20! Critical hit! (total {self.total} vs AC {ac})"
        elif is_auto_miss:
            self.description = f"Natural 1! Automatic miss! (total {self.total} vs AC {ac})"
        elif self.is_hit:
            self.description = f"Hit! (rolled {natural_roll}+{bonus}={self.total} vs AC {ac})"
        else:
            self.description = f"Miss. (rolled {natural_roll}+{bonus}={self.total} vs AC {ac})"


def make_attack_roll(bonus, ac, advantage=None):
    """
    Make a d20 attack roll with advantage/disadvantage.

    Args:
        bonus: Attack bonus to add to the roll
        ac: Target's Armor Class
        advantage: AdvantageState, or None/True/False for backward compatibility
            - AdvantageState.ADVANTAGE or True: advantage
            - AdvantageState.DISADVANTAGE or False: disadvantage
            - AdvantageState.NORMAL or None: normal roll

    Returns:
        AttackResult with hit/miss, critical, and description
    """
    # Handle backward compatibility with True/False/None
    if advantage is True:
        advantage_state = AdvantageState.ADVANTAGE
    elif advantage is False:
        advantage_state = AdvantageState.DISADVANTAGE
    elif advantage is None:
        advantage_state = AdvantageState.NORMAL
    elif isinstance(advantage, AdvantageState):
        advantage_state = advantage
    else:
        advantage_state = AdvantageState.NORMAL

    # Use dice module for d20 roll
    natural_roll, _ = roll_d20(advantage_state)

    # Natural 20 is always a critical hit
    is_critical = (natural_roll == 20)
    # Natural 1 is always a miss
    is_auto_miss = (natural_roll == 1)

    return AttackResult(natural_roll, bonus, ac, is_critical, is_auto_miss)


def parse_dice_expression(dice_str):
    """
    Parse a dice expression like "1d8+3" or "2d6" or "1d10-1".

    Returns:
        tuple: (num_dice, die_size, modifier)
    """
    # Handle simple integer damage (legacy support)
    if dice_str.isdigit():
        return (0, 0, int(dice_str))

    # Parse dice expression: XdY+Z or XdY-Z or XdY
    match = re.match(r"(\d+)d(\d+)([+-]\d+)?", dice_str.strip())
    if not match:
        # Fallback: treat as flat damage
        return (0, 0, 1)

    num_dice = int(match.group(1))
    die_size = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0

    return (num_dice, die_size, modifier)


def roll_dice(num_dice, die_size):
    """Roll multiple dice and return the total."""
    return sum(random.randint(1, die_size) for _ in range(num_dice))


def roll_damage_for_attack(damage_dice_str, is_critical=False):
    """
    Roll damage dice for an attack using d20 library.

    Args:
        damage_dice_str: Dice expression like "1d8+3"
        is_critical: If True, double the dice (not the modifier)

    Returns:
        int: Total damage rolled
    """
    if is_critical:
        # Critical hits double the dice, not the modifier
        # Parse to extract dice and modifier, then reconstruct
        num_dice, die_size, modifier = parse_dice_expression(damage_dice_str)

        if num_dice > 0 and die_size > 0:
            # Double the dice for critical
            crit_dice_expr = f"{num_dice * 2}d{die_size}"
            if modifier > 0:
                crit_dice_expr += f"+{modifier}"
            elif modifier < 0:
                crit_dice_expr += f"{modifier}"

            damage_total, _ = roll_damage(crit_dice_expr)
            return damage_total
        else:
            # Flat damage only (no dice to double)
            return modifier
    else:
        # Normal damage roll
        damage_total, _ = roll_damage(damage_dice_str)
        return damage_total


def apply_damage_modifiers(damage, damage_type, creature):
    """
    Apply damage resistance, immunity, and vulnerability.

    Order: immunity -> resistance -> vulnerability

    Args:
        damage: Base damage amount
        damage_type: Type of damage (e.g., "slashing", "fire")
        creature: Creature receiving damage

    Returns:
        tuple: (final_damage, modifier_applied)
            modifier_applied is one of: "immunity", "resistance", "vulnerability", None
    """
    # Check for immunity
    immunities = getattr(creature, 'damage_immunities', [])
    if damage_type and damage_type.lower() in [i.lower() for i in immunities]:
        return (0, "immunity")

    # Check for resistance
    resistances = getattr(creature, 'damage_resistances', [])
    if damage_type and damage_type.lower() in [r.lower() for r in resistances]:
        damage = damage // 2  # Floor division (round down)
        return (damage, "resistance")

    # Check for vulnerability
    vulnerabilities = getattr(creature, 'damage_vulnerabilities', [])
    if damage_type and damage_type.lower() in [v.lower() for v in vulnerabilities]:
        damage = damage * 2
        return (damage, "vulnerability")

    return (damage, None)


def apply_damage(creature, dmg, damage_type=None):
    """
    Apply damage to a creature, reducing HP.

    Args:
        creature: Creature taking damage
        dmg: Base damage amount (before resistances/immunities)
        damage_type: Type of damage (optional)

    Returns:
        Creature with updated HP (mutates in place for now)
    """
    # Apply damage modifiers (resistance, immunity, vulnerability)
    final_damage, modifier = apply_damage_modifiers(dmg, damage_type, creature)

    # Reduce HP, clamped at 0
    creature.current_hp = max(0, creature.current_hp - final_damage)

    return creature


class DeathSaveResult:
    """Result of a death saving throw."""

    def __init__(self, roll, successes, failures, is_stable=False, is_conscious=False):
        self.roll = roll
        self.successes = successes
        self.failures = failures
        self.is_stable = is_stable
        self.is_conscious = is_conscious

        # Generate description
        if is_conscious:
            self.description = f"Natural 20! Regained 1 HP and is conscious!"
        elif roll == 1:
            self.description = f"Natural 1! 2 failures. ({successes} successes, {failures} failures)"
        elif is_stable and successes >= 3:
            self.description = f"Success! Stabilized. ({successes} successes)"
        elif failures >= 3:
            self.description = f"Failure. Dead. ({failures} failures)"
        elif roll >= 10:
            self.description = f"Success. ({successes} successes, {failures} failures)"
        else:
            self.description = f"Failure. ({successes} successes, {failures} failures)"


def make_death_save(creature):
    """
    Make a death saving throw.

    D&D 5e rules:
    - Roll d20 (no modifiers)
    - Natural 20: Regain 1 HP and become conscious
    - Natural 1: Count as 2 failures
    - 10 or higher: Success
    - Below 10: Failure
    - 3 successes: Stabilized (unconscious but not dying)
    - 3 failures: Dead

    Args:
        creature: Creature making the death save

    Returns:
        DeathSaveResult with updated death save state
        Note: Also mutates creature in place (for backward compatibility)
    """
    from src.domain.creature import DeathSaves

    # Use dice module for d20 roll (death saves are always normal, no advantage)
    roll, _ = roll_d20(AdvantageState.NORMAL)

    # Get current death saves from Pydantic model
    current_saves = creature.death_saves
    successes = current_saves.successes
    failures = current_saves.failures

    if roll == 20:
        # Natural 20: Regain 1 HP, become conscious
        creature.current_hp = 1
        creature.death_saves = DeathSaves(successes=0, failures=0, stable=True)
        result = DeathSaveResult(roll, 0, 0, is_stable=True, is_conscious=True)
    elif roll == 1:
        # Natural 1: 2 failures
        failures += 2
        is_stable = failures < 3
        creature.death_saves = DeathSaves(successes=successes, failures=failures, stable=is_stable)
        result = DeathSaveResult(roll, successes, failures, is_stable=is_stable, is_conscious=False)
    elif roll >= 10:
        # Success
        successes += 1
        if successes >= 3:
            # Stabilized
            creature.death_saves = DeathSaves(successes=0, failures=0, stable=True)
            result = DeathSaveResult(roll, successes, failures, is_stable=True, is_conscious=False)
        else:
            creature.death_saves = DeathSaves(successes=successes, failures=failures, stable=False)
            result = DeathSaveResult(roll, successes, failures, is_stable=False, is_conscious=False)
    else:
        # Failure
        failures += 1
        is_stable = failures < 3
        creature.death_saves = DeathSaves(successes=successes, failures=failures, stable=is_stable)
        result = DeathSaveResult(roll, successes, failures, is_stable=is_stable, is_conscious=False)

    return creature


class SavingThrowResult:
    """Result of a saving throw."""

    def __init__(self, roll, modifier, dc, is_success):
        self.roll = roll
        self.modifier = modifier
        self.total = roll + modifier
        self.dc = dc
        self.is_success = is_success

        if is_success:
            self.description = f"Success! (rolled {roll}+{modifier}={self.total} vs DC {dc})"
        else:
            self.description = f"Failed. (rolled {roll}+{modifier}={self.total} vs DC {dc})"


def make_saving_throw(ability_modifier, dc, advantage=None):
    """
    Make a saving throw.

    Args:
        ability_modifier: Ability modifier (e.g., Dex mod for Dex save)
        dc: Difficulty Class
        advantage: AdvantageState, or None/True/False for backward compatibility
            - AdvantageState.ADVANTAGE or True: advantage
            - AdvantageState.DISADVANTAGE or False: disadvantage
            - AdvantageState.NORMAL or None: normal roll

    Returns:
        SavingThrowResult with success/failure and description
    """
    # Handle backward compatibility with True/False/None
    if advantage is True:
        advantage_state = AdvantageState.ADVANTAGE
    elif advantage is False:
        advantage_state = AdvantageState.DISADVANTAGE
    elif advantage is None:
        advantage_state = AdvantageState.NORMAL
    elif isinstance(advantage, AdvantageState):
        advantage_state = advantage
    else:
        advantage_state = AdvantageState.NORMAL

    # Use dice module for d20 roll
    roll, _ = roll_d20(advantage_state)

    total = roll + ability_modifier
    is_success = total >= dc

    return SavingThrowResult(roll, ability_modifier, dc, is_success)
