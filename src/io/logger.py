# Strings that are translated when lang != "en" (strategy evolution and round headers)
_TRANSLATIONS = {
    "en": {
        "strategy_evolution": "Strategy evolution",
        "round_header": "Round",
        "combat_over": "Combat Over. Winner: {winner} in {rounds} rounds",
    },
    "it": {
        "strategy_evolution": "Evoluzione della strategia",
        "round_header": "Turno",
        "combat_over": "Combattimento terminato. Vincitore: {winner} in {rounds} turni",
    },
}


def _t(lang: str, key: str, **kwargs) -> str:
    """Return translated string for key; fallback to en if lang missing."""
    d = _TRANSLATIONS.get(lang, _TRANSLATIONS["en"])
    msg = d.get(key, _TRANSLATIONS["en"][key])
    return msg.format(**kwargs) if kwargs else msg


class CombatLogger:
    """Logger for structured combat events."""

    def __init__(self, verbose=True, lang: str = "en"):
        self.entries = []
        self.verbose = verbose
        self.lang = lang if lang in _TRANSLATIONS else "en"
        self._strategy_entries = []  # (round, creature_name, summary) for end-of-fight strategy evolution
        self._combat_stats = []  # list of {attacker_name, action_name, attack_name, damage, is_aoe} for fight summary
        self._deaths_by_type = []  # (victim_name, victim_team, damage_type, killer_name, killer_team) for deaths-by-character stats

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
        label = _t(self.lang, "round_header")
        msg = f"\n=== {label} {round_number} ==="
        self.log(msg)

    def log_opportunity_attack(self, attacker_name, target_name, attack_name, attack_result):
        """Log an opportunity attack (reaction)."""
        msg = f"  {attacker_name} opportunity attack on {target_name} with {attack_name}: {attack_result.description}"
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

    def log_death(
        self,
        creature_name: str,
        team: str,
        damage_type: str | None = None,
        killer_name: str | None = None,
        killer_team: str | None = None,
    ):
        """Log when a creature falls to 0 HP. Records damage type and killer for deaths-by-character stats."""
        side = "party" if team == "party" else "enemy"
        msg = f"  >> {creature_name} ({side}) has fallen."
        self.log(msg)
        self._deaths_by_type.append(
            (creature_name, team, damage_type or "unknown", killer_name, killer_team)
        )

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

    def log_turn_strategy(self, round_number: int, creature_name: str, summary: str):
        """Record one creature's strategy/reasoning for this turn (used for strategy evolution summary)."""
        if summary and summary.strip():
            self._strategy_entries.append((round_number, creature_name, summary.strip()))

    def log_strategy_evolution_for_round(self, round_number: int):
        """Log strategy evolution for a single round (at beginning of next round). No-op if round_number < 1 or no entries."""
        if round_number < 1:
            return
        entries = [(rnd, name, s) for rnd, name, s in self._strategy_entries if rnd == round_number]
        if not entries:
            return
        label = _t(self.lang, "strategy_evolution")
        round_label = _t(self.lang, "round_header")
        self.log(f"\n=== {label} ===")
        self.log(f"\n{round_label} {round_number}:")
        for _, creature_name, summary in entries:
            for line in summary.splitlines():
                self.log(f"  {creature_name}: {line.strip()}")
        self.log("")

    def log_strategy_evolution(self):
        """Append a Strategy Evolution section to the log from recorded turn-by-turn strategy."""
        if not self._strategy_entries:
            return
        label = _t(self.lang, "strategy_evolution")
        round_label = _t(self.lang, "round_header")
        self.log(f"\n=== {label} ===")
        current_round = None
        for round_number, creature_name, summary in self._strategy_entries:
            if round_number != current_round:
                current_round = round_number
                self.log(f"\n{round_label} {round_number}:")
            for line in summary.splitlines():
                self.log(f"  {creature_name}: {line.strip()}")
        self.log("")

    def record_attack_use(self, attacker_name: str, action_name: str, attack_name: str, damage: int, is_aoe: bool = False):
        """Record one weapon/spell attack use for combat stats summary."""
        self._combat_stats.append({
            "attacker_name": attacker_name,
            "action_name": action_name,
            "attack_name": attack_name,
            "damage": damage,
            "is_aoe": is_aoe,
        })

    def record_aoe_use(self, attacker_name: str, action_name: str, total_damage: int):
        """Record one AoE spell/ability use (total damage across all targets)."""
        self._combat_stats.append({
            "attacker_name": attacker_name,
            "action_name": action_name,
            "attack_name": action_name,
            "damage": total_damage,
            "is_aoe": True,
        })

    def get_combat_stats(self):
        """Return list of combat stat records for end-of-fight summary."""
        return list(self._combat_stats)

    def get_deaths_by_type(self):
        """Return list of (victim_name, victim_team, damage_type, killer_name, killer_team) for deaths-by-character stats."""
        return list(self._deaths_by_type)

    def log_combat_end(self, winner, rounds):
        """Log the end of combat."""
        self.log_strategy_evolution_for_round(rounds)
        msg = _t(self.lang, "combat_over", winner=winner, rounds=rounds)
        self.log(f"\n{msg}")

    def get_full_log(self):
        """Return the complete combat log as a single string."""
        return "\n".join(self.entries)
