---
name: Eckardius
race: Dwarf
class: Cleric
level: 2
ac: 16
hp_max: 11
speed: 25
initiative_bonus: 0
team: party
position: B2
ability_scores:
  str: 14
  dex: 8
  con: 16
  int_: 10
  wis: 16
  cha: 12
damage_resistances: [poison]
damage_immunities: []
damage_vulnerabilities: []
actions:
  - name: Warhammer
    description: "Melee weapon attack (dwarf + cleric proficiency)."
    attacks:
      - name: Warhammer
        attack_bonus: 4
        damage:
          dice: "1d8+1"
          damage_type: bludgeoning
        reach: 5
  - name: Guiding Bolt
    description: "Spell: ranged spell attack, 4d6 radiant; next attack roll vs target has advantage."
    attacks:
      - name: Guiding Bolt
        attack_bonus: 6
        damage:
          dice: "4d6"
          damage_type: radiant
        range: 120
  - name: Spiritual Weapon
    description: "Bonus action spell: spectral weapon, 1d8+3 force, melee spell attack."
    attacks:
      - name: Spiritual Weapon
        attack_bonus: 6
        damage:
          dice: "1d8+3"
          damage_type: force
        reach: 5
---
Hill Dwarf Cleric. +2 CON, +1 WIS; poison resistance; speed 25 ft (not reduced by heavy armor). Full caster (Wisdom); heavy armor and shield. Uses warhammer in melee, Guiding Bolt at range, Spiritual Weapon for extra damage. Tactics: support and damage from mid-range; frontline with warhammer when needed.