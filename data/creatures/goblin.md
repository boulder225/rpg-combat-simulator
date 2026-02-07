---
name: Goblin
ac: 15
hp_max: 7
speed: 30
initiative_bonus: 2
team: enemies
position: E5
ability_scores:
  str: 8
  dex: 14
  con: 10
  int_: 10
  wis: 8
  cha: 8
damage_resistances: []
damage_immunities: []
damage_vulnerabilities: []
actions:
  - name: Scimitar
    description: "Melee weapon attack"
    attacks:
      - name: Scimitar
        attack_bonus: 4
        damage:
          dice: "1d6+2"
          damage_type: slashing
        reach: 5
  - name: Shortbow
    description: "Ranged weapon attack"
    attacks:
      - name: Shortbow
        attack_bonus: 4
        damage:
          dice: "1d6+2"
          damage_type: piercing
        range: 80
---
A nimble goblin warrior armed with a scimitar and shortbow.
