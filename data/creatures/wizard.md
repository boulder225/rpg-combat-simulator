---
name: Wizard
ac: 12
hp_max: 22
speed: 30
initiative_bonus: 2
team: party
position: A1
ability_scores:
  str: 8
  dex: 14
  con: 12
  int_: 16
  wis: 10
  cha: 10
damage_resistances: []
damage_immunities: []
damage_vulnerabilities: []
actions:
  - name: Fireball
    description: "Spell: 20-foot-radius sphere, DEX save for half."
    area_shape: sphere
    radius_squares: 4
    save_ability: dex
    save_dc: 14
    damage:
      dice: "8d6"
      damage_type: fire
    attacks: []
  - name: Fire Bolt
    description: "Spell attack"
    attacks:
      - name: Fire Bolt
        attack_bonus: 5
        damage:
          dice: "1d10"
          damage_type: fire
        range: 120
---
A spellcaster who prefers Fireball when multiple enemies are grouped.
