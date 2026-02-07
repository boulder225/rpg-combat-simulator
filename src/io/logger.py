class CombatLogger:
    """Logger for structured combat events."""

    def __init__(self, verbose=True):
        self.entries = []
        self.verbose = verbose

    def log(self, msg):
        """Log a generic message."""
        self.entries.append(msg)
        if self.verbose:
            print(msg)

    def log_initiative(self, creature_name, roll, bonus, total):
        """Log an initiative roll."""
        msg = f"Initiative: {creature_name} rolled {roll}+{bonus}={total}"
        self.log(msg)

    def log_round(self, round_number):
        """Log the start of a combat round."""
        msg = f"\n=== Round {round_number} ==="
        self.log(msg)

    def log_attack(self, attacker_name, target_name, attack_name, attack_result):
        """
        Log an attack roll.

        Args:
            attacker_name: Name of attacking creature
            target_name: Name of target creature
            attack_name: Name of the attack (e.g., "Longsword", "Bite")
            attack_result: AttackResult object with roll details
        """
        if attack_result.is_critical:
            msg = f"  {attacker_name} attacks {target_name} with {attack_name}: {attack_result.description}"
        elif attack_result.is_auto_miss:
            msg = f"  {attacker_name} attacks {target_name} with {attack_name}: {attack_result.description}"
        elif attack_result.is_hit:
            msg = f"  {attacker_name} attacks {target_name} with {attack_name}: {attack_result.description}"
        else:
            msg = f"  {attacker_name} attacks {target_name} with {attack_name}: {attack_result.description}"
        self.log(msg)

    def log_damage(self, target_name, amount, damage_type, modifier_applied, remaining_hp):
        """
        Log damage dealt to a creature.

        Args:
            target_name: Name of creature taking damage
            amount: Amount of damage (after modifiers)
            damage_type: Type of damage (e.g., "slashing", "fire")
            modifier_applied: "resistance", "immunity", "vulnerability", or None
            remaining_hp: Remaining HP after damage
        """
        damage_type_str = f" {damage_type}" if damage_type else ""

        if modifier_applied == "immunity":
            msg = f"    {target_name} is immune to{damage_type_str} damage! -> HP: {remaining_hp}"
        elif modifier_applied == "resistance":
            msg = f"    {amount}{damage_type_str} damage (resisted, halved) -> {target_name} HP: {remaining_hp}"
        elif modifier_applied == "vulnerability":
            msg = f"    {amount}{damage_type_str} damage (vulnerable, doubled) -> {target_name} HP: {remaining_hp}"
        else:
            msg = f"    {amount}{damage_type_str} damage -> {target_name} HP: {remaining_hp}"

        self.log(msg)

    def log_miss(self, attacker_name, target_name, attack_name, roll_total, target_ac):
        """
        Log a missed attack.

        Args:
            attacker_name: Name of attacking creature
            target_name: Name of target creature
            attack_name: Name of the attack
            roll_total: Total attack roll (d20 + bonus)
            target_ac: Target's AC
        """
        msg = f"  {attacker_name} attacks {target_name} with {attack_name}: Miss. (rolled {roll_total} vs AC {target_ac})"
        self.log(msg)

    def log_death_save(self, creature_name, result_description):
        """
        Log a death saving throw.

        Args:
            creature_name: Name of creature making death save
            result_description: Description of the result (from DeathSaveResult)
        """
        msg = f"  {creature_name} death save: {result_description}"
        self.log(msg)

    def log_movement(self, creature_name, from_pos, to_pos):
        """
        Log creature movement.

        Args:
            creature_name: Name of moving creature
            from_pos: Starting position (e.g., "A1")
            to_pos: Ending position (e.g., "B3")
        """
        msg = f"  {creature_name} moves from {from_pos} to {to_pos}"
        self.log(msg)

    def log_combat_end(self, winner, rounds):
        """Log the end of combat."""
        self.log(f"\nCombat Over. Winner: {winner} in {rounds} rounds")

    def get_full_log(self):
        """Return the complete combat log as a single string."""
        return "\n".join(self.entries)
