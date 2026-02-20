# Phase 4: Terminal UI & Advanced Combat — Context

**Gathered:** 2026-02-08  
**Status:** Discussion complete, ready for planning

---

<domain>
## Phase Boundary

Two pillars:

1. **Terminal UI (TUI)** — DM sees a professional Textual app: live progress during batch runs (X of N), scrollable combat log, colored result tables, keyboard navigation. CLI remains the primary way to *configure* runs; TUI is the preferred way to *watch* batch simulation and inspect results.

2. **Advanced combat mechanics** — Rules that depend on grid position: cover (+2/+5 AC and DEX saves), opportunity attacks when leaving melee reach, and at least one AoE (Fireball-style sphere) hitting creatures in radius. Terrain is defined in .md files and influences cover/positioning.

Success = DM runs the same encounter from CLI or TUI, sees live progress and readable results in TUI, and combat resolution correctly applies cover, opportunity attacks, and Fireball AoE.
</domain>

---

<decisions>
## Implementation Decisions (Proposed)

### TUI

- **Entry point:** Same CLI (`run.py`) with a `--tui` flag. When `--tui`, launch Textual app instead of printing to terminal; when absent, current CLI behavior unchanged (headless).
- **Batch in worker:** Run `BatchRunner` (or equivalent) inside a Textual worker; post progress messages (e.g. `ProgressUpdate(run_index, total_runs, win_rate_so_far)`). Main thread only updates widgets via `post_message` / reactive attributes — no blocking simulation in event loop (PITFALLS: use `call_from_thread` if worker posts from background).
- **Widgets:** (1) Progress bar + run count and live win %; (2) Scrollable combat log (last N lines or full log for current run); (3) Results panel: win rate, CI, difficulty, top damage sources, colored (e.g. Rich/Textual styles). Optional: tab or panel switch between “progress”, “log”, “results”.
- **Scope:** Phase 4 TUI is “batch run viewer” — single-run verbose mode (LOG-03) and step-through combat are Phase 5 or later. No map/ASCII grid rendering — text coordinates only.
- **Dependencies:** Add `textual` to pyproject.toml if not already present. No new runtimes.

### Cover (GRID-04)

- **Rules:** Half-cover: +2 AC, +2 DEX saves; three-quarters cover: +5 AC, +5 DEX saves. Apply when attacker’s line to target passes through a cover zone (or another creature) per 5e rules.
- **Model:** Terrain .md defines *cover zones* (e.g. list of cells or rectangles in chess notation). At resolution time: given attacker position, target position, and terrain, compute whether target has half or three-quarters cover (e.g. ray from attacker to target, count covered squares or use zone flags).
- **Who provides cover:** Phase 4 can start with *terrain only* (walls, obstacles). “Another creature between attacker and target” (creature-as-cover) can be same pass or deferred if time-boxed.
- **Integration:** `domain/distance.py` or new `domain/cover.py`: e.g. `cover_bonus(attacker_pos, target_pos, terrain) -> Literal["none", "half", "three-quarters"]`. Rules layer applies bonus to AC and DEX saves when resolving attacks/saves.

### Opportunity attacks (GRID-05)

- **Trigger:** When a creature *leaves* another creature’s melee reach (moves from a cell within reach to a cell outside) during its movement, the creature whose reach is left gets one reaction: opportunity attack (single melee attack).
- **Reach:** Use creature’s reach from stat block (default 5 ft = 1 square). Stored on Creature or action; distance in feet = Manhattan distance × 5.
- **One reaction per round:** Track “reaction used” per creature per round; opportunity attack consumes it. No other reactions in Phase 4 unless we add a second (e.g. Shield) in a later phase.
- **Order:** Resolve movement in segments if we want RAW “leave on first square” vs “leave after full move”; minimal implementation: when creature’s position changes from “in reach” to “out of reach”, trigger one opportunity attack from each creature that had them in reach.

### AoE — Fireball (GRID-06)

- **In scope for success criteria:** At least one AoE: *sphere* (e.g. Fireball, 20 ft radius = 4 squares from center). Creatures whose position is within the sphere (by grid distance) are in the area; resolve damage/saves for each.
- **Distance in squares:** Sphere: Manhattan distance from center ≤ 4 (or use “within 4 squares” for 5e’s “20-foot radius sphere”). Research suggests “within 4 squares” is a common simplification for grid play.
- **Targeting:** Caster chooses center cell. No “partial cover” from terrain for AoE in Phase 4 unless we explicitly add it (defer if needed).
- **Cone/line:** Defer to post–Phase 4 or v2; success criteria require only sphere.

### Terrain (TERRAIN-01)

- **Format:** Terrain defined in .md files with YAML frontmatter (e.g. name, dimensions, list of cover zones). Cover zone = list of cells (e.g. `cells: ["B2","B3","C2","C3"]`) or rectangle `from: B2, to: C4` and a type (`half` | `three-quarters`).
- **Loading:** Similar to creatures: `data/terrain/` or `data/arenas/`, loaded by name via CLI (`--terrain arena-name`). One active terrain per encounter.
- **Default:** If no `--terrain`, no cover zones (open field). No need for “default arena” in Phase 4.
</decisions>

---

<specifics>
## Specific Ideas

- **TUI:** Reuse existing `BatchRunner` and result structures; TUI only consumes progress and `BatchResults` to render. No duplicate simulation logic.
- **Cover:** Pure function in domain: `get_cover(attacker_pos, target_pos, terrain_zones) -> "none" | "half" | "three-quarters"`. Rules layer calls it and adds bonus to AC / DEX save before resolving.
- **Opportunity attacks:** In simulator turn loop, when applying movement: before updating position, check “current cell in reach of any enemy?”; when updating to new cell, if “new cell out of reach” for an enemy who had them in reach, that enemy gets opportunity attack (reaction). Resolve attack immediately (before rest of movement if we do segment movement later).
- **Fireball:** One action type (e.g. “Fireball”) with `area: sphere`, `radius_squares: 4`, `save: DEX`, `damage: 8d6 fire`. Simulator: given center cell, collect all creatures in sphere, apply save/damage. Heuristic/LLM agent can choose center cell when choosing action.
- **Files:** `src/tui/` for app, widgets, screens. `src/domain/cover.py` (or extend `distance.py`), `src/domain/terrain.py` for terrain model. Opportunity logic in `simulation/simulator.py` or `domain/rules.py`.
</specifics>

---

<open_questions>
## Open Questions for User

1. **TUI vs CLI default:** Should `python run.py ...` (no flags) stay pure CLI, or do you want a config/default to open TUI when run from a terminal? (Proposal: default remains CLI; TUI only with `--tui`.)

2. **Combat log in TUI:** Show log for “last run only”, “all runs concatenated”, or “selected run” (e.g. first loss)? (Proposal: last run only for Phase 4 to keep UI simple.)

3. **Terrain complexity:** Start with “list of cells that block line of sight” only, or do you want difficult terrain / hazards in Phase 4? (Proposal: cover only; difficult terrain deferred to Phase 5 or v2.)

4. **Creature-as-cover:** Should another creature between attacker and target grant half cover? (Proposal: defer to keep Phase 4 scope manageable; add in a follow-up if needed.)
</open_questions>

---

<deferred>
## Deferred

- Single-run verbose mode (watch LLM thinking + rolls live) — LOG-03, Phase 5
- Step-through combat (one turn at a time) — Phase 5 or v2
- Cone/line AoE — post–Phase 4
- Difficult terrain (half movement) — ADV-06, v2
- Flanking rules — optional rule, v2
- ASCII/graphical grid map — out of scope (text coordinates only)
- Creature-as-cover — optional, follow-up
</deferred>

---

*Phase: 04-terminal-ui-advanced-combat*  
*Context gathered: 2026-02-08*
