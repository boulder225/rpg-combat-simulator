---
name: Prescold
race: Human
class: Ranger
level: 2
ac: 14
hp_max: 11
speed: 30
initiative_bonus: 3
team: party
position: A1
ability_scores:
  str: 14
  dex: 16
  con: 13
  int_: 11
  wis: 15
  cha: 9
damage_resistances: []
damage_immunities: []
damage_vulnerabilities: []
actions:
  - name: Multiattack
    description: "Two ranged attacks with longbow (Archery +2)."
    attacks:
      - name: Longbow
        attack_bonus: 8
        damage:
          dice: "1d8+3"
          damage_type: piercing
        range: 150
      - name: Longbow
        attack_bonus: 8
        damage:
          dice: "1d8+3"
          damage_type: piercing
        range: 150
  - name: Longbow
    description: "Ranged weapon attack (Archery fighting style)."
    attacks:
      - name: Longbow
        attack_bonus: 8
        damage:
          dice: "1d8+3"
          damage_type: piercing
        range: 150
  - name: Shortsword
    description: "Melee weapon attack when forced into close range."
    attacks:
      - name: Shortsword
        attack_bonus: 6
        damage:
          dice: "1d6+3"
          damage_type: piercing
        reach: 5
  - name: Hunter's Mark (Longbow)
    description: "Ranged attack with Hunter's Mark; weapon + 1d6 (expressed as 2d8+3 for dice parser)."
    attacks:
      - name: Longbow (Hunter's Mark)
        attack_bonus: 8
        damage:
          dice: "2d8+3"
          damage_type: piercing
        range: 150
---
Human Ranger (Archery). +1 to all abilities; medium armor, martial weapons; Archery fighting style (+2 ranged). Scout and tracker; Favored Enemy and Natural Explorer. Prefers longbow at range; uses shortsword in melee. Tactics: keep distance, focus fire with longbow; Hunter's Mark on priority targets.