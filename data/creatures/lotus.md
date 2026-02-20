---
name: Lotus
race: Half-Elf
class: Fighter
level: 2
ac: 18
hp_max: 12
speed: 30
initiative_bonus: 1
team: party
position: B2
ability_scores:
  str: 16
  dex: 13
  con: 14
  int_: 10
  wis: 12
  cha: 10
damage_resistances: []
damage_immunities: []
damage_vulnerabilities: []
actions:
  - name: Multiattack
    description: "The fighter makes two attacks with their longsword (Dueling style +2 damage)."
    attacks:
      - name: Longsword
        attack_bonus: 5
        damage:
          dice: "1d8+5"
          damage_type: slashing
        reach: 5
      - name: Longsword
        attack_bonus: 5
        damage:
          dice: "1d8+5"
          damage_type: slashing
        reach: 5
  - name: Longsword
    description: "Melee weapon attack (one-handed, Dueling +2)."
    attacks:
      - name: Longsword
        attack_bonus: 5
        damage:
          dice: "1d8+5"
          damage_type: slashing
        reach: 5
---
Half-Elf Fighter. +2 CHA, +1 STR, +1 CON; 60 ft darkvision; Fey Ancestry (advantage vs charm, can't be put to sleep); Skill Versatility (two extra skills). Fighter: Defense or Dueling style (here Dueling: +2 damage one-handed), Second Wind (1d10+level), Action Surge (extra action). Versatile in and out of combat; strong face and survivability. Tactics: frontline with longsword and shield, burst when using Action Surge.
