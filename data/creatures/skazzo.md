---
name: Skazzo
race: Dragonborn
class: Paladin
level: 2
ac: 16
hp_max: 12
speed: 30
initiative_bonus: 1
team: party
position: B2
ability_scores:
  str: 17
  dex: 12
  con: 14
  int_: 8
  wis: 10
  cha: 14
damage_resistances: [fire]
damage_immunities: []
damage_vulnerabilities: []
actions:
  - name: Multiattack
    description: "Two melee attacks (longsword); can use Divine Smite on a hit."
    attacks:
      - name: Longsword
        attack_bonus: 5
        damage:
          dice: "1d8+3"
          damage_type: slashing
        reach: 5
      - name: Longsword
        attack_bonus: 5
        damage:
          dice: "1d8+3"
          damage_type: slashing
        reach: 5
  - name: Longsword
    description: "Melee weapon attack"
    attacks:
      - name: Longsword
        attack_bonus: 5
        damage:
          dice: "1d8+3"
          damage_type: slashing
        reach: 5
  - name: Divine Smite
    description: "Melee attack; expend spell slot for +2d8 radiant (1st-level slot)."
    attacks:
      - name: Longsword (Smite)
        attack_bonus: 5
        damage:
          dice: "3d8+3"
          damage_type: radiant
        reach: 5
  - name: Breath Weapon
    description: "Draconic Ancestry (Red): 15-ft cone, fire, DEX save for half. Recharge on short rest."
    area_shape: sphere
    radius_squares: 3
    save_ability: dex
    save_dc: 12
    damage:
      dice: "2d6"
      damage_type: fire
    attacks: []
---
Dragonborn Paladin (Red ancestry). +2 Strength, +1 Charisma; fire resistance; breath weapon (cone of fire). Uses heavy armor and longsword; Divine Smite for burst radiant damage, Lay on Hands for healing. Tactics: frontline when needed, breath when enemies are grouped; favor smite on important targets.