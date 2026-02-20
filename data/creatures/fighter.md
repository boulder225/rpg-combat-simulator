---
name: Fighter
level: 5
ac: 18
hp_max: 44
speed: 30
initiative_bonus: 1
team: party
position: B2
ability_scores:
  str: 16
  dex: 12
  con: 14
  int_: 10
  wis: 13
  cha: 8
damage_resistances: []
damage_immunities: []
damage_vulnerabilities: []
actions:
  - name: Multiattack
    description: "The fighter makes two attacks with their longsword"
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
---
A sturdy human fighter wielding a longsword and shield.
