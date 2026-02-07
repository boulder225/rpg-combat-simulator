# D&D 5e Combat Simulator for Dungeon Masters – Master Document (February 2026)

## 1. Project Goal
Build a terminal-based software simulator for D&D 5th Edition combat (using 2014 SRD rules) to help a DM quickly evaluate encounter balance.

Core purpose:
- In 5–15 minutes, understand if a monster/group is appropriately challenging, too weak, or deadly for the current player party.
- Run multiple simulations with varying strategies to see a range of possible outcomes.
- No complex ASCII graphics needed – use simple chess-like coordinates (A1, C4, F7, …) to track positions.
- Creatures act as autonomous agents with tactical decision-making.
- Everything configurable via Markdown (.md) files (creatures, terrain, combat logs).
- Logs saved as Markdown → resume interrupted games.

## 2. Key Requirements
- Positions: text coordinates on implicit 5×5 ft grid (A1 = column A row 1).
- Distance calculation: Manhattan (with optional diagonal cost 5 ft extra).
- Advantage/disadvantage: based on range, cover (half/three-quarters from terrain/positioning), conditions.
- Combat log: append-only Markdown file (rounds, positions, HP, actions, results).
- Rules: strictly SRD 2014 (no 2024 changes like weapon masteries).
- Custom creatures & homebrew: defined in .md files with YAML frontmatter.

Example creature file (`goblin-boss.md`):

```yaml
---
name: Goblin Boss
ac: 17
hp_max: 21
speed: 30
initiative_bonus: 2
team: enemies
position: D5
---
Actions:
- name: Multiattack
  description: Makes two attacks with scimitar.
- name: Scimitar
  attack_bonus: 5
  damage: 1d6+3 slashing
  reach: 5
Bonus Actions:
- name: Disengage
- name: Hide
  skill: Stealth +6