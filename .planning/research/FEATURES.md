# Feature Research

**Domain:** D&D 5e Combat Simulator (Terminal-based, Monte Carlo)
**Researched:** 2026-02-07
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Basic 5e mechanics (AC, HP, attack rolls) | Core D&D rules - without this it's not a D&D simulator | LOW | SRD 5e via dnd5eapi.co covers this |
| Initiative system | Turn order is fundamental to D&D combat | LOW | Standard d20 + DEX modifier |
| Advantage/disadvantage | Ubiquitous 5e mechanic affecting most rolls | LOW | Roll 2d20, take higher/lower |
| Damage types and resistances | Critical for encounter balance accuracy | MEDIUM | Many creature interactions depend on this |
| Multiple attacks per creature | Higher CR creatures have multiattack | MEDIUM | Action economy is critical to balance |
| Hit point tracking | Fundamental combat state | LOW | Track current/max HP per combatant |
| Target selection logic | Simulator must decide who attacks whom | MEDIUM | Even basic "attack nearest" requires grid awareness |
| Win/loss determination | DMs need to know which side wins | LOW | Combat ends when one side drops to 0 HP |
| Difficulty rating (Easy/Medium/Hard/Deadly) | Standard D&D vocabulary for encounter balance | LOW | Based on XP budget vs party level |
| Monster CR calculation | DMs think in terms of CR when building encounters | LOW | Use official CR values from SRD |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **LLM-powered tactical AI** | Realistic creature behavior vs simple heuristics - this is THE differentiator | HIGH | Already planned - agent tiers (heuristic → LLM) |
| **Monte Carlo batch simulation** | Statistical certainty vs one-shot guess - shows win % not just difficulty label | MEDIUM | Already planned - 20+ runs for confidence intervals |
| **Grid + positioning + cover** | Tactical realism - most simulators ignore terrain entirely | HIGH | Already planned - coordinate grid with cover mechanics |
| **Markdown combat logs** | Reviewable play-by-play for understanding WHY encounters fail/succeed | MEDIUM | Already planned - append-only logs with resume |
| **Speed (8 minute target)** | Actionable feedback during session prep, not overnight batch jobs | MEDIUM | Performance optimization critical for UX |
| **Terminal TUI with live progress** | Professional DM tool feel vs web toy - shows simulation progress in real-time | MEDIUM | Already planned - Textual TUI |
| **Custom creature markdown files** | Easy homebrew without code - fits DM workflow (many DMs already use markdown notes) | LOW | Already planned - YAML frontmatter format |
| **Spell slot tracking** | Realistic resource depletion affects long encounter balance | HIGH | Casters behave very differently when conserving slots |
| **Conditions (prone, stunned, etc.)** | Major tactical impact - prone gives melee advantage, ranged disadvantage | HIGH | Critical for realistic monk/barbarian/control wizard behavior |
| **Action economy visualization** | Shows WHY 4 weak creatures beat 1 strong creature - educational for DMs | MEDIUM | Helps DMs understand the math behind balance |
| **Creature role archetypes** | Different AI behavior for tank/striker/controller/support | MEDIUM | Makes encounters feel realistic vs all creatures playing same |
| **Sensitivity analysis** | "What if I add +2 AC to the boss?" - shows balance tipping points | HIGH | Helps DMs tune encounters without re-running from scratch |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Real-time 3D visualization** | "Cool factor" - looks impressive in demos | Massive scope creep, requires graphics engine, breaks terminal focus, slow to render | ASCII/Unicode grid map in terminal is sufficient - focus on data not eye candy |
| **Every spell in the game** | "Completeness" - users want their favorite spell | SRD-only keeps it legally clean, 90% of combat spells covered, full spell implementation is months of work | Start with SRD damage/buff spells, defer niche utility spells to post-MVP |
| **Full D&D character sheet import** | "Convenience" - users have sheets in D&D Beyond | Requires reverse-engineering proprietary formats, legal gray area, unnecessary for encounter testing | Simple markdown creature format is faster to type than navigating import UX |
| **Multiplayer/shared session** | "Collaboration" - multiple DMs testing together | Adds networking layer, auth, sync conflicts - huge complexity for minimal value | Single-user terminal tool ships faster, users can share markdown files via git |
| **Perfect AI that never makes mistakes** | "Realism" - players don't play optimally either | LLMs should model realistic creature intelligence, not chess-engine perfection | Agent tiers let DMs choose "smart ogre" vs "tactical genius dragon" |
| **Web-based UI** | "Accessibility" - no install required | Scope creep, requires hosting/backend, dilutes terminal tool focus | Terminal TUI is the differentiator - embrace it, don't fight it |
| **2014 AND 2024 rules support** | "Future-proofing" - new rules coming | Trying to support both rulesets doubles testing surface, creates version conflicts | Pick one (2014 SRD), ship it, defer 2024 to v2 if there's demand |
| **Real-time encounter builder UI** | "User-friendly" - drag-and-drop monsters | Markdown files are faster for users comfortable with terminal (target audience) | Editing YAML in preferred editor > custom UI for this user base |

## Feature Dependencies

```
[Basic Combat Mechanics (AC, HP, attacks)]
    ├──requires──> [Initiative System]
    ├──requires──> [Damage Types & Resistances]
    └──requires──> [Hit Point Tracking]

[Target Selection Logic]
    └──requires──> [Grid + Positioning] (for distance calculations)

[Grid + Positioning]
    └──enables──> [Cover Mechanics]
    └──enables──> [Advantage/Disadvantage from positioning]

[LLM Tactical AI]
    ├──requires──> [Basic Combat Mechanics]
    ├──requires──> [Target Selection Logic]
    └──enhances──> [Creature Role Archetypes]

[Monte Carlo Simulation]
    ├──requires──> [Win/Loss Determination]
    └──enhances──> [Sensitivity Analysis]

[Spell Slot Tracking]
    └──requires──> [Multi-round simulation] (slots only matter over time)

[Conditions]
    ├──affects──> [Advantage/Disadvantage]
    ├──affects──> [Target Selection Logic] (stunned = priority target)
    └──requires──> [Turn tracking] (duration "until end of next turn")

[Combat Logs]
    └──enables──> [Resume capability]
    └──enables──> [Post-simulation analysis]

[Sensitivity Analysis]
    └──requires──> [Monte Carlo Simulation] (need baseline to compare against)
```

### Dependency Notes

- **Basic Combat Mechanics** is the foundation - everything depends on this
- **Grid + Positioning** unlocks tactical features (cover, flanking, movement)
- **LLM Tactical AI** is a late-stage integration requiring stable core mechanics
- **Spell Slot Tracking** only makes sense if simulations run long enough to deplete resources (3+ rounds)
- **Conditions** create circular dependencies with advantage/disadvantage - implement together
- **Sensitivity Analysis** is valuable but depends on fast simulation turnaround

## MVP Definition

### Launch With (v1)

Minimum viable product - what's needed to validate "LLM-powered tactical simulation beats static CR calculators."

- [x] Basic 5e mechanics (AC, HP, attack rolls, damage) - ESSENTIAL: Can't be D&D without this
- [x] Initiative system - ESSENTIAL: Turn order affects everything
- [x] Advantage/disadvantage - ESSENTIAL: Too common in 5e to skip
- [x] Damage types and resistances - ESSENTIAL: Affects 40%+ of creatures
- [x] Multiple attacks per creature - ESSENTIAL: Action economy is balance
- [x] Hit point tracking - ESSENTIAL: Core state management
- [x] Basic target selection (nearest enemy heuristic) - ESSENTIAL: Must make tactical choices
- [x] Win/loss determination - ESSENTIAL: Core output
- [x] Monte Carlo batch simulation (20+ runs) - ESSENTIAL: The differentiator
- [x] Grid + positioning (basic) - ESSENTIAL: Enables tactical AI
- [x] Markdown combat logs - ESSENTIAL: Debugging and transparency
- [x] Textual TUI with progress - ESSENTIAL: UX differentiator
- [x] Markdown creature files - ESSENTIAL: User input format
- [x] SRD 2014 integration (dnd5eapi.co) - ESSENTIAL: Content source
- [x] Difficulty rating calculation - ESSENTIAL: Standard DM vocabulary

### Add After Validation (v1.x)

Features to add once core is working and users validate the approach.

- [ ] **Cover mechanics** - ADD WHEN: Grid is stable and users request tactical depth (Trigger: "Can the simulator handle archer tactics?")
- [ ] **LLM tactical AI (basic)** - ADD WHEN: Heuristic baseline proves Monte Carlo works (Trigger: Core simulation hits <5min for 20 runs)
- [ ] **Spell slot tracking** - ADD WHEN: Users test long adventuring days (Trigger: "Casters feel overpowered in simulations")
- [ ] **Conditions (prone, stunned, grappled)** - ADD WHEN: Users complain about monk/grappler inaccuracy (Trigger: "Simulation doesn't model control tactics")
- [ ] **Resume from log files** - ADD WHEN: Users hit simulation crashes (Trigger: "Lost 15 minutes of simulation progress")
- [ ] **Creature role archetypes** - ADD WHEN: LLM AI is working (Trigger: "All creatures use same tactics")
- [ ] **Healing actions** - ADD WHEN: Users test cleric/paladin heavy parties (Trigger: "Healer parties seem weaker than they should be")

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Sensitivity analysis** - DEFER: Nice-to-have optimization tool, not core validation
- [ ] **Action economy visualization** - DEFER: Educational but not essential for encounter testing
- [ ] **Legendary actions/resistances** - DEFER: High-CR only, affects <10% of encounters
- [ ] **Lair actions** - DEFER: Single-monster boss fights, niche use case
- [ ] **Multi-encounter day simulation** - DEFER: Complex resource tracking, long runtime
- [ ] **Terrain effects (difficult terrain, hazards)** - DEFER: Edge cases, high complexity
- [ ] **Flanking rules** - DEFER: Optional rule, not universal
- [ ] **Custom AI prompt templates** - DEFER: Power user feature after LLM AI proves valuable
- [ ] **Export to PDF/HTML reports** - DEFER: Markdown logs are sufficient initially
- [ ] **2024 rules support** - DEFER: Wait for 2024 SRD release, user demand unclear

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Basic 5e mechanics | HIGH | MEDIUM | P1 |
| Initiative system | HIGH | LOW | P1 |
| Advantage/disadvantage | HIGH | LOW | P1 |
| Damage types/resistances | HIGH | MEDIUM | P1 |
| Multiple attacks | HIGH | LOW | P1 |
| Hit point tracking | HIGH | LOW | P1 |
| Target selection logic | HIGH | MEDIUM | P1 |
| Win/loss determination | HIGH | LOW | P1 |
| Monte Carlo simulation | HIGH | MEDIUM | P1 |
| Grid + positioning (basic) | HIGH | MEDIUM | P1 |
| Markdown combat logs | HIGH | LOW | P1 |
| Textual TUI | HIGH | MEDIUM | P1 |
| Markdown creature files | HIGH | LOW | P1 |
| SRD integration | HIGH | LOW | P1 |
| Difficulty rating | HIGH | LOW | P1 |
| Cover mechanics | MEDIUM | MEDIUM | P2 |
| LLM tactical AI | HIGH | HIGH | P2 |
| Spell slot tracking | MEDIUM | MEDIUM | P2 |
| Conditions | MEDIUM | HIGH | P2 |
| Resume capability | MEDIUM | MEDIUM | P2 |
| Creature role archetypes | MEDIUM | MEDIUM | P2 |
| Healing actions | MEDIUM | LOW | P2 |
| Sensitivity analysis | LOW | HIGH | P3 |
| Action economy viz | LOW | MEDIUM | P3 |
| Legendary actions | LOW | MEDIUM | P3 |
| Lair actions | LOW | MEDIUM | P3 |
| Multi-encounter day | LOW | HIGH | P3 |
| Terrain effects | LOW | HIGH | P3 |
| Flanking | LOW | LOW | P3 |

**Priority key:**
- P1: Must have for launch - core validation
- P2: Should have - add when core is stable
- P3: Nice to have - future consideration

## Competitor Feature Analysis

| Feature | D&D Beyond | Kobold Fight Club | MCDM Codex | Open-Source Sims | Our Approach |
|---------|------------|-------------------|------------|------------------|--------------|
| Difficulty calculation | XP-based, static | XP-based, static | Unknown (VTT) | Varies | **Monte Carlo win % - statistical vs guess** |
| Tactical AI | None - manual play | None - calculator | Player-driven | Basic heuristics | **LLM-powered agents - realistic behavior** |
| Grid/positioning | VTT maps (paid) | None | Yes (VTT) | Rare | **Terminal grid - free, fast** |
| Combat simulation | None - theory only | None - theory only | Manual play | Yes (limited) | **Automated batch runs** |
| Custom creatures | Homebrew UI | Manual CR calc | Unknown | CSV/code | **Markdown files - DM-friendly** |
| Speed | Instant (calc only) | Instant (calc only) | Real-time play | Slow (minutes) | **8 min target for 20 runs** |
| Output format | Difficulty label | Difficulty label | Battle map | Varies | **Win % + markdown logs** |
| Rules coverage | Full (paid) | SRD only | 2024 (paid) | Partial SRD | **SRD 2014 - legally clean** |
| Platform | Web | Web | Desktop VTT | Mostly web | **Terminal - pro DM tool** |

### Competitive Positioning

**D&D Beyond / Kobold Fight Club**: They give you a difficulty label (Easy/Medium/Hard/Deadly). We give you a win percentage based on actual simulated combat. They're calculators; we're a simulator.

**MCDM Codex / VTTs**: They're for playing sessions with players. We're for testing encounters in prep. They're real-time; we're batch. They require graphical UI; we're terminal-native.

**Open-source simulators**: They use basic AI (attack nearest, attack weakest). We use LLM agents that model realistic creature intelligence and tactics. They output raw data; we output readable markdown logs.

**Our niche**: Terminal-based, LLM-powered, Monte Carlo simulator for DMs who want data-driven encounter balance during session prep. Fast enough to iterate (8 min), realistic enough to trust (LLM tactics), transparent enough to understand (markdown logs).

## Sources

### Encounter Builder Tools
- [D&D Beyond Encounter Builder](https://www.dndbeyond.com//encounter-builder) - Official tool, XP-based difficulty
- [Kobold Plus Fight Club](https://koboldplus.club/) - Community fork of legendary encounter calculator
- [MCDM on D&D Beyond, Character Creation and Encounter Design](https://goblinpoints.com/2405) - MCDM Codex VTT features
- [D&D Beyond Encounter Builder Updates](https://www.dndbeyond.com/forums/d-d-beyond-general/d-d-beyond-feedback/178683-encounter-builder-updates) - User feedback on missing features

### Combat Simulators
- [DnD-battler GitHub](https://github.com/matteoferla/DnD-battler) - Python 5e simulator with 1000-run Monte Carlo
- [dnd-combat-sim GitHub](https://github.com/Eddykasp/dnd-combat-sim) - Tactical grid-based simulator
- [DnD5e-CombatSimulator GitHub](https://github.com/asahala/DnD5e-CombatSimulator) - Creature combat simulator
- [combatsim GitHub](https://github.com/lemonade512/combatsim) - Grid-based tactical simulator
- [dnd_combat_simulation GitHub](https://github.com/5ecombatsimulator/dnd_combat_simulation) - Full combat API

### AI & Tactical Decision Making
- [AI Researchers Test LLMs With D&D Combat](https://www.ttrpginsider.news/p/news-roundup-ai-researchers-test-its-ability-to-experience-d-d-combat) - December 2025 research on LLM tactical decisions
- [From Chatbots to Dice Rolls: Researchers Use D&D to Test AI](https://today.ucsd.edu/story/from-chatbots-to-dice-rolls-researchers-use-dd-to-test-ais-long-term-decision-making-abilities) - Claude 3.5 Haiku performed best for tactical optimality
- [AI for Dungeons & Dragons - Ian W. Davis](https://ianwdavis.com/dnd-battle-ai.html) - Combat AI patterns

### Balance & Accuracy
- [Encounter balance in 2024: better or worse?](https://scrollforinitiative.com/2024/12/01/encounter-balance-in-2024-better-or-worse/) - Known problems with XP-based balance
- [How to Balance Encounters in D&D](https://scrollforinitiative.com/2022/07/25/how-to-balance-encounters-in-dd/) - Limitations of DMG encounter rules
- [DnD Metrics](https://dndmetrics.com/) - 87% accuracy from 15,000 real encounters
- [Will the Encounter Builder Ever be Updated Again?](https://www.dndbeyond.com/forums/d-d-beyond-general/d-d-beyond-feedback/212428-will-the-encounter-builder-ever-be-updated-again) - User frustration with stale tools

### Combat Mechanics
- [Mastering Cover in D&D 5e](https://onixshu.com/blogs/articles/cover-in-dnd-5e) - Cover rules and tactical positioning
- [Monte Carlo simulation GitHub](https://github.com/andrei-gorbatch/monte_carlo) - Monte Carlo encounter simulation on GCP
- [RAWR: Algorithm for D&D Strategy Optimization](https://web.stanford.edu/class/aa228/reports/2020/final98.pdf) - Stanford research on D&D optimization

### Homebrew & Custom Creatures
- [Monsterbrew](https://www.monsterbrew.app/) - D&D 5e monster creator with CR calculation
- [Falindrith's D&D Monster Maker](https://ebshimizu.github.io/5emm/) - Auto-compute CR and format statblocks
- [How to Homebrew Monsters on D&D Beyond](https://www.dndbeyond.com/posts/1140-tutorial-how-to-homebrew-monsters-on-d-d-beyond) - Official homebrew guide

---
*Feature research for: D&D 5e Combat Simulator (Terminal-based, Monte Carlo)*
*Researched: 2026-02-07*
*Confidence: MEDIUM - Based on web search results, GitHub repository analysis, and recent (Dec 2025) AI research. No access to private/paywalled tools for full feature comparison.*
