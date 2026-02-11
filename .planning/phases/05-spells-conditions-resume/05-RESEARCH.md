# Phase 5: Spells, Conditions & Resume - Research

**Researched:** 2026-02-11
**Domain:** D&D 5e spell mechanics, condition system, Python serialization/checkpointing
**Confidence:** HIGH (codebase analysis), HIGH (D&D rules from SRD), HIGH (Python serialization patterns)

---

## Summary

Phase 5 adds three interacting systems to an already-working combat simulator. The codebase is clean, consistent Python with Pydantic v2 models, immutable frozen dataclasses for combat state, and a well-understood rules engine. All three Phase 5 pillars (spell slots, conditions, resume) have clear, low-risk implementation paths using existing patterns.

**Spell slots** require adding two fields to the Creature Pydantic model (`spell_slots: dict[int, int]` and `concentration: Optional[str]`) and extending the Action model with `spell_level: Optional[int]` and `is_concentration: bool`. The rules engine and simulator need small additions: decrement slots on cast, end concentration on new concentration spell, and trigger a CON save on damage while concentrating.

**Conditions** (prone, frightened, stunned, grappled) require adding `conditions: list[str]` to Creature and a new `src/domain/conditions.py` module that maps condition names to advantage/disadvantage sources. The existing `resolve_advantage()` ternary state machine already handles the interaction correctly — conditions are just inputs. The `make_attack_roll()` and `make_saving_throw()` call sites in `simulator.py` need to query active conditions before calling.

**Batch resume** (checkpoint/restart) requires JSON serialization of `BatchRunner` progress to disk every N runs. `CombatState` is a frozen dataclass containing Pydantic models — manual `model_dump()` + `dataclasses.asdict()`-style serialization roundtrips cleanly (verified in-repo). The checkpoint stores runs completed, wins, and the random state. On resume, the `MonteCarloSimulator` skips already-completed runs and loads the partial win counts.

**Primary recommendation:** Implement spell slots and conditions first (domain + rules changes), then integrate into simulator, then add checkpoint/resume as a batch runner concern. All three can be delivered in 4-5 lean plans matching Phase 4's plan style.

---

## Standard Stack

### Core (already in project)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | >=2.12 (currently 2.12.5) | Creature/Action model extension | Already in use; `model_copy(update=...)` handles immutable updates |
| python-frontmatter | >=1.1.0 | Markdown data loading | Already used for all creature/terrain files |
| d20 | >=1.1.2 | Dice rolls for concentration saves | Already handles all dice notation |
| dataclasses (stdlib) | Python 3.11+ | CombatState immutable updates | `replace()` already used throughout |
| json (stdlib) | Python 3.11+ | Checkpoint serialization | Sufficient for simple scalar + dict state |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pathlib (stdlib) | Python 3.11+ | Checkpoint file path management | For `--checkpoint` CLI flag path handling |
| random (stdlib) | Python 3.11+ | Saving/restoring RNG state | `random.getstate()` / `random.setstate()` for exact resume |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| json (stdlib) | pickle | Pickle is faster but produces binary, not human-inspectable, and is unsafe for untrusted input. JSON is better for checkpoint files DMs might edit or inspect. |
| list[str] for conditions | list[ConditionEntry(name, duration)] | Full duration tracking adds complexity. Phase 5 only requires 4 conditions with fixed behavior; duration as optional field suffices. |
| conditions on Creature | conditions dict on CombatState | Keeping conditions on Creature means `update_creature()` handles them — zero changes to copy-on-write machinery. |

**Installation:** No new dependencies needed for Phase 5 core. All required libraries are already in `pyproject.toml`.

---

## Architecture Patterns

### Recommended Project Structure (additions only)

```
src/
├── domain/
│   ├── creature.py        # ADD: conditions, spell_slots, concentration fields
│   ├── conditions.py      # NEW: condition name -> mechanical effects (advantage sources)
│   └── rules.py           # ADD: concentration save, condition-aware attack/save resolution
├── simulation/
│   ├── simulator.py       # ADD: spell slot deduction, condition effects at attack resolution
│   ├── monte_carlo.py     # ADD: checkpoint save/load hooks
│   └── batch_runner.py    # ADD: checkpoint file write every N runs
├── io/
│   └── checkpoint.py      # NEW: serialize/deserialize batch progress to JSON
└── cli/
    └── batch_args.py      # ADD: --checkpoint flag
```

### Pattern 1: Extend Creature with Optional Spell Fields

**What:** Add three optional fields to `Creature` with safe defaults so existing creature markdown files require zero changes.

**When to use:** Any time existing data files must keep working without migration. Use `Optional` with defaults.

**Example (verified in-repo):**
```python
# src/domain/creature.py additions
class Creature(BaseModel):
    # ... existing fields ...
    conditions: list[str] = []                    # e.g. ["prone", "frightened"]
    spell_slots: dict[int, int] = {}              # level -> remaining (e.g. {1: 4, 2: 3, 3: 2})
    concentration: Optional[str] = None          # name of active concentration spell, None if none
```

`model_copy(update=...)` already handles these — no change to `CombatState.update_creature()`.

### Pattern 2: Extend Action with Spell Metadata

**What:** Add optional spell-specific fields to `Action` so spellcasting actions carry their slot level and concentration flag.

**When to use:** When an action consumes a resource (spell slot) or has global state effects (concentration).

**Example:**
```python
# src/domain/creature.py additions to Action
class Action(BaseModel):
    # ... existing fields ...
    spell_level: Optional[int] = None             # None = cantrip/not a spell; 1-9 = leveled spell
    is_concentration: bool = False                # True if casting this requires concentration
```

Existing `wizard.md` `Fireball` action gets `spell_level: 3, is_concentration: false` added. `Fire Bolt` stays `spell_level: null` (cantrip).

### Pattern 3: Condition Registry Module

**What:** A pure-function module `src/domain/conditions.py` that maps condition names to their mechanical effects. No state, no classes — just `get_attack_advantage_sources(creature)` and `get_save_advantage_sources(creature, save_ability)` functions.

**When to use:** Any time the rules engine needs to compute advantage from active conditions. Single source of truth, easily testable.

**Example:**
```python
# src/domain/conditions.py
CONDITION_ATTACK_DISADVANTAGE = {"prone", "frightened", "poisoned", "blinded"}
CONDITION_ATTACK_ADVANTAGE_WHEN_TARGET = {"prone", "stunned", "blinded", "paralyzed", "restrained"}
CONDITION_SAVE_AUTO_FAIL_STR_DEX = {"stunned", "paralyzed"}
CONDITION_SAVE_DISADVANTAGE_DEX = {"restrained"}

def get_attacker_disadvantage_sources(attacker) -> list[str]:
    """Returns list of active conditions that cause disadvantage on attacker's attack rolls."""
    return [c for c in attacker.conditions if c in CONDITION_ATTACK_DISADVANTAGE]

def get_target_advantage_sources(attacker, target, is_melee: bool) -> list[str]:
    """Returns list of sources that grant attacker advantage vs target."""
    sources = []
    if "stunned" in target.conditions or "paralyzed" in target.conditions:
        sources.append("target_stunned_or_paralyzed")
    if "prone" in target.conditions and is_melee:
        sources.append("target_prone_melee")
    return sources

def get_target_disadvantage_sources(attacker, target, is_melee: bool) -> list[str]:
    """Returns disadvantage sources when attacking a target (e.g. prone at range)."""
    sources = []
    if "prone" in target.conditions and not is_melee:
        sources.append("target_prone_ranged")
    return sources
```

This plugs directly into the existing `resolve_advantage()` call that already accepts source lists.

### Pattern 4: Concentration Save in Rules Engine

**What:** After dealing damage to a concentrating creature, immediately check if they were concentrating and trigger a CON save.

**D&D 5e Rule (verified from SRD and multiple community sources):**
- DC = max(10, damage_taken // 2)
- Roll: d20 + CON modifier
- Success: concentration maintained; Failure: concentration ends
- If multiple sources of damage hit simultaneously, separate save for each

**Where it lives:** After `state.update_creature(target_id, current_hp=new_hp)` in `simulator.py`, call `check_concentration_save(state, target_id, final_damage, logger)`.

**Example:**
```python
# src/domain/rules.py
def make_concentration_save(creature, damage_taken: int) -> SavingThrowResult:
    """CON save to maintain concentration after taking damage. DC = max(10, damage // 2)."""
    dc = max(10, damage_taken // 2)
    con_mod = creature.ability_scores.get_modifier("con")
    return make_saving_throw(con_mod, dc)
```

### Pattern 5: Batch Checkpoint Serialization

**What:** After every N runs (e.g., 100), serialize batch progress to a JSON checkpoint file. On restart with `--checkpoint`, load the file, skip completed runs, restore win count.

**Serialization (verified roundtrip in-repo):**
```python
# src/io/checkpoint.py
import json
from pathlib import Path
from src.domain.combat_state import CombatState
from src.domain.creature import Creature

def save_checkpoint(path: Path, runs_done: int, wins: int, template_creatures: dict,
                    random_state) -> None:
    """Save batch progress checkpoint."""
    data = {
        "format_version": 1,
        "runs_done": runs_done,
        "wins": wins,
        "template_creatures": {cid: c.model_dump() for cid, c in template_creatures.items()},
        "random_state": list(random_state[1]),  # Only the state tuple, not the function
    }
    path.write_text(json.dumps(data, indent=2))

def load_checkpoint(path: Path) -> dict:
    """Load batch progress checkpoint."""
    return json.loads(path.read_text())
```

**Note on `random.getstate()`:** The Python random state tuple `(version, internalstate, gauss_next)` where internalstate is a tuple of 625 integers. This serializes fine as a JSON array. `random.setstate()` restores exact RNG sequence.

### Anti-Patterns to Avoid

- **Mutable Creature for conditions:** Do NOT mutate `creature.conditions` in place. Always use `state.update_creature(cid, conditions=[...])` to produce a new CombatState.
- **Conditions on CombatState dict:** Do NOT add a separate `conditions: dict[str, list[str]]` field to CombatState. Keeping conditions on Creature keeps the existing `update_creature()` workflow intact.
- **Concentration on CombatState:** Keep `concentration` on Creature (not CombatState) for the same reason.
- **Pickle for checkpoints:** Pickle is Python-version-specific and unsafe. Use JSON. The performance difference is irrelevant at 100-run checkpoint intervals.
- **Spell slots in Action:** Spell slot *counts* (remaining slots) belong on Creature. `spell_level` (what level a spell costs) belongs on Action. These are different concerns.
- **Complex duration objects for Phase 5 conditions:** Phase 5 only needs 4 conditions. A `list[str]` on Creature is sufficient. Full duration tracking (condition expires after N rounds) can be added in Phase 6 if needed.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Advantage/disadvantage from conditions | Custom advantage resolver | Existing `resolve_advantage()` in `src/domain/dice.py` | Already handles ternary cancellation; just pass condition-derived sources |
| CON saving throw for concentration | Custom save logic | Existing `make_saving_throw()` in `src/domain/rules.py` | Already handles advantage, DC comparison, result description |
| Condition → attack modifier mapping | Ad-hoc if/elif chain in simulator | `src/domain/conditions.py` pure functions | Centralized, testable, single source of truth |
| JSON checkpoint | Custom format parser | stdlib `json` + `model_dump()` | Pydantic already serializes all creature fields correctly |
| Random state persistence | Custom PRNG | `random.getstate()` / `random.setstate()` | Python stdlib, exact resume from any point |

**Key insight:** The existing `resolve_advantage(advantage_sources, disadvantage_sources)` function was designed from the start to accept lists of string sources. Conditions are just a new source of entries for those lists. No API change required.

---

## Common Pitfalls

### Pitfall 1: Forgetting to Decrement Spell Slots Before Checking

**What goes wrong:** Simulator checks if slots are available, then resolves AoE/spell, but forgets to actually decrement. Or decrements before checking whether the action is actually a leveled spell (not a cantrip).

**Why it happens:** The `_resolve_aoe()` path in `simulator.py` currently has no slot awareness. Easy to add the check but forget the mutation.

**How to avoid:** In the simulator, before calling `_resolve_aoe()` or any spell-action path: (1) check `action_obj.spell_level is not None`, (2) check `caster.spell_slots.get(action_obj.spell_level, 0) > 0`, (3) deduct slot via `update_creature(cid, spell_slots={...})`, THEN resolve. Keep it in one block.

**Warning signs:** Integration test where wizard casts Fireball more than `spell_slots[3]` times.

### Pitfall 2: Concentration Not Ending When New Concentration Spell Cast

**What goes wrong:** Simulator applies new concentration spell without clearing the old one. Both "Haste" and "Bless" are active simultaneously. Success criterion 2 fails.

**Why it happens:** The concentration clear happens at cast-time, not at damage-time. Easy to implement the damage-time save but forget the cast-time clear.

**How to avoid:** In the simulator's spell-casting path, before applying new concentration: check `if action_obj.is_concentration and caster.concentration is not None`. If so, log "Concentration on [old spell] ends." and clear it with `update_creature(cid, concentration=None)`. Then set new concentration.

**Warning signs:** Check `creature.concentration` immediately after casting second concentration spell in a test.

### Pitfall 3: Concentration Save After Zero-Damage Events

**What goes wrong:** `make_concentration_save` triggered even when `final_damage == 0` (e.g., immunity applied). Per 5e RAW, "if you take damage" — immunity means you don't take damage.

**Why it happens:** The concentration check call is placed after the damage application regardless of final amount.

**How to avoid:** Only call concentration save if `final_damage > 0`. The `apply_damage_modifiers()` function already returns `(0, "immunity")` — check the returned amount.

**Warning signs:** A fire-immune creature concentrating on a spell loses concentration after taking fire damage.

### Pitfall 4: Checkpoint Random State Deserialization

**What goes wrong:** `random.getstate()` returns `(3, (625-int tuple), None_or_float)`. When saving to JSON, the tuple becomes a list. When restoring, pass `(3, tuple(loaded_state), gauss_next)` to `random.setstate()`.

**Why it happens:** JSON arrays deserialize as lists; Python random expects a tuple for the inner state.

**How to avoid:** Wrap: `random.setstate((3, tuple(data["random_state"]), None))`. Test the roundtrip explicitly.

**Warning signs:** Simulation produces different results on resume than if it had run uninterrupted (test with seed=42, run 200, checkpoint at 100, resume from 100, compare final state to straight 200-run).

### Pitfall 5: Prone Condition Melee vs. Ranged Attack Direction

**What goes wrong:** Success criterion 4 says "Prone gives advantage to melee attacks, disadvantage to ranged attacks" — but this is from the *attacker's* perspective when attacking a prone target. Easy to confuse with "prone creature's own attacks have disadvantage."

**Why it happens:** The D&D prone condition has TWO effects: (a) prone creature's attack rolls have disadvantage; (b) attacks AGAINST the prone creature have advantage if attacker is within 5 ft (melee), disadvantage if attacker is further (ranged).

**How to avoid:** Implement both in `conditions.py`:
1. `get_attacker_disadvantage_sources(attacker)` — if attacker is prone, add disadvantage
2. `get_target_advantage_sources(attacker, target, is_melee)` — if target is prone AND is_melee (within 5ft), add advantage
3. `get_target_disadvantage_sources(attacker, target, is_melee)` — if target is prone AND NOT is_melee, add disadvantage

**Warning signs:** Integration test: fighter attacks prone enemy from 5ft (advantage) vs. 30ft (disadvantage).

### Pitfall 6: Fresh Creature Copies in Monte Carlo Reset Conditions

**What goes wrong:** `_create_fresh_creatures()` in `MonteCarloSimulator` currently resets `current_hp` but won't automatically reset `conditions`, `spell_slots`, or `concentration` if those are set on template creatures.

**Why it happens:** The existing fresh copy logic uses `model_copy(deep=True)` then manually resets `current_hp`. Any new fields added to Creature need explicit resets.

**How to avoid:** After `model_copy(deep=True)`, also reset:
```python
fresh_copy.current_hp = fresh_copy.hp_max
fresh_copy.conditions = []
fresh_copy.concentration = None
# spell_slots: restore from hp_max-equivalent — need a spell_slots_max field, or reset to template value
```

For spell slots: store the *template* creature's slots (from the markdown file) and restore them, not just clear them. The template `fresh_copy` from `model_copy(deep=True)` already has the correct `spell_slots` from the markdown file, so just don't touch them (they're already fresh from the deep copy). Just clear `conditions` and `concentration`.

---

## Code Examples

Verified patterns from in-repo investigation:

### Creature with New Spell and Condition Fields

```python
# Additions to src/domain/creature.py
class Creature(BaseModel):
    # ... all existing fields unchanged ...
    conditions: list[str] = []
    spell_slots: dict[int, int] = {}
    concentration: Optional[str] = None

# In Action model:
class Action(BaseModel):
    # ... all existing fields unchanged ...
    spell_level: Optional[int] = None
    is_concentration: bool = False
```

### Spell Slot Check and Deduction (in simulator.py)

```python
# Before resolving a spell action:
def _can_cast_spell(creature, action_obj) -> bool:
    """Check if creature has spell slot for this spell level."""
    if action_obj.spell_level is None:
        return True  # cantrip or non-spell, always castable
    return creature.spell_slots.get(action_obj.spell_level, 0) > 0

def _deduct_spell_slot(state: CombatState, caster_id: str, spell_level: int) -> CombatState:
    """Deduct one spell slot of given level. Returns new CombatState."""
    caster = state.creatures[caster_id]
    new_slots = dict(caster.spell_slots)
    new_slots[spell_level] = max(0, new_slots.get(spell_level, 0) - 1)
    return state.update_creature(caster_id, spell_slots=new_slots)
```

### Concentration Clear at Cast-Time

```python
# Before applying a concentration spell effect:
def _start_concentration(state: CombatState, caster_id: str, spell_name: str,
                          logger: CombatLogger) -> CombatState:
    """End existing concentration (if any) and start new concentration spell."""
    caster = state.creatures[caster_id]
    if caster.concentration is not None:
        logger.log(f"  {caster.name}'s concentration on {caster.concentration} ends.")
        state = state.update_creature(caster_id, concentration=None)
    state = state.update_creature(caster_id, concentration=spell_name)
    return state
```

### Concentration Save After Damage

```python
# In simulator.py, after apply damage block:
if final_damage > 0:
    target = state.creatures[target_id]
    if target.concentration is not None:
        dc = max(10, final_damage // 2)
        con_mod = target.ability_scores.get_modifier("con")
        save_result = rules.make_saving_throw(con_mod, dc)
        logger.log(f"  {target.name} concentration save (DC {dc}): {save_result.description}")
        if not save_result.is_success:
            logger.log(f"  {target.name} loses concentration on {target.concentration}.")
            state = state.update_creature(target_id, concentration=None)
```

### Condition-Aware Attack Roll (in simulator.py)

```python
# Before calling make_attack_roll(), compute advantage sources from conditions:
from src.domain.conditions import get_attacker_disadvantage_sources, \
    get_target_advantage_sources, get_target_disadvantage_sources
from src.domain.dice import resolve_advantage

is_melee = atk.reach is not None
dist = distance_in_feet(c.position, target.position)
is_within_melee_reach = dist <= (atk.reach or 5)

adv_sources = get_target_advantage_sources(c, target, is_within_melee_reach)
disadv_sources = (
    get_attacker_disadvantage_sources(c)
    + get_target_disadvantage_sources(c, target, is_within_melee_reach)
)
# Cover adds to AC, not disadvantage, so keep cover_bonus separate (existing pattern)
advantage_state = resolve_advantage(adv_sources, disadv_sources)
res = rules.make_attack_roll(atk.attack_bonus, target.ac, advantage_state, cover_bonus=cover_bonus)
```

### Checkpoint Serialization Roundtrip (verified in-repo)

```python
# src/io/checkpoint.py
import json
import random
from pathlib import Path
from src.domain.creature import Creature

def save_checkpoint(path: Path, runs_done: int, wins: int,
                    template_creatures: dict) -> None:
    rng_state = random.getstate()
    data = {
        "format_version": 1,
        "runs_done": runs_done,
        "wins": wins,
        "template_creatures": {cid: c.model_dump() for cid, c in template_creatures.items()},
        "rng_version": rng_state[0],
        "rng_state": list(rng_state[1]),
        "rng_gauss": rng_state[2],
    }
    path.write_text(json.dumps(data, indent=2))

def load_checkpoint(path: Path) -> dict:
    data = json.loads(path.read_text())
    # Restore creatures
    data["template_creatures"] = {
        cid: Creature(**cr) for cid, cr in data["template_creatures"].items()
    }
    # Restore RNG state
    random.setstate((data["rng_version"], tuple(data["rng_state"]), data["rng_gauss"]))
    return data
```

### Wizard Markdown with Spell Slots

```yaml
# data/creatures/wizard.md (additions to existing frontmatter)
spell_slots:
  1: 4
  2: 3
  3: 2

actions:
  - name: Fireball
    description: "Spell: 20-foot-radius sphere, DEX save for half."
    spell_level: 3
    is_concentration: false
    area_shape: sphere
    # ... rest unchanged
  - name: Haste
    description: "Concentration. Target gains +2 AC, doubled speed, extra attack."
    spell_level: 3
    is_concentration: true
    attacks: []
    # ... (Haste is a buff, needs different handling in Phase 5)
```

---

## D&D 5e Rules Reference (Verified)

### Spell Slots
- Each leveled spell costs one slot of its level or higher
- Cantrips (level 0) never cost slots
- Long rest restores all slots (not relevant for single-combat simulation)
- Warlock exception (Pact Magic) — out of scope for Phase 5

### Concentration
- Only one concentration spell active at a time
- Casting a new concentration spell immediately ends the previous one (no save)
- When taking damage while concentrating: CON save DC = max(10, damage_taken // 2)
- Multiple simultaneous damage sources: separate save for each
- Becoming incapacitated automatically ends concentration
- Dying ends concentration

### Conditions (Phase 5 required subset)

| Condition | Effect on Attacker | Effect When Targeted | Movement |
|-----------|-------------------|---------------------|----------|
| **Prone** | Disadvantage on attack rolls | Advantage if attacker within 5ft (melee); disadvantage if farther (ranged) | Must crawl (half speed) or spend half movement to stand |
| **Frightened** | Disadvantage on attack rolls while source in line of sight | No change | Cannot move closer to source of fear |
| **Stunned** | Incapacitated (no actions/reactions), auto-fails STR/DEX saves | Advantage on attacks | Cannot move |
| **Grappled** | No direct effect on attacks | No direct effect on incoming attacks | Speed becomes 0 |

### Concentration Save Formula
DC = max(10, floor(damage_taken / 2))

Source: D&D 5e SRD, confirmed by arcaneeye.com, flutesloot.com, dndbeyond.com — consistent across all sources.

---

## Phase 5 Plan Structure Recommendation

Based on complexity, the phase should be delivered in 4-5 plans:

**Plan 05-01: Spell Slot and Concentration Domain** (domain only, no simulator changes)
- Extend `Creature` with `conditions`, `spell_slots`, `concentration`
- Extend `Action` with `spell_level`, `is_concentration`
- Add `src/domain/conditions.py` with pure functions
- Add `make_concentration_save()` to `rules.py`
- Update creature loader / markdown parser to load new fields
- Tests for model round-trip, conditions module, concentration save
- Update `wizard.md` with `spell_slots` and spell metadata

**Plan 05-02: Spell Slots and Concentration in Simulator**
- `simulator.py`: check slot availability before casting, deduct slot, end-old-concentration at cast, concentration save after damage
- `monte_carlo.py`: reset `conditions=[]`, `concentration=None` in `_create_fresh_creatures()`
- Integration tests: wizard exhausts slots, second concentration spell ends first, damage breaks concentration

**Plan 05-03: Conditions in Combat Resolution**
- `simulator.py`: compute condition-based advantage/disadvantage at attack roll sites
- Apply prone/stunned/grappled movement effects (speed=0 when grappled, etc.)
- `heuristic.py`: simple condition awareness (avoid attacking stunned target with ranged from close range)
- Integration tests: prone gives advantage/disadvantage, grappled speed=0

**Plan 05-04: Batch Checkpoint / Resume**
- `src/io/checkpoint.py`: save/load functions
- `batch_runner.py`: `--checkpoint-every N` (default 100), save checkpoint after N runs
- `run.py` + `batch_args.py`: `--resume checkpoint.json` flag; load and skip already-done runs
- Tests for checkpoint roundtrip, resume produces correct run count

**Plan 05-05: LOG-03 Verbose Single-Run Mode (TUI)**
- Extend `CombatLogger` with live-emit mode
- TUI single-run mode: show LLM thinking blocks + dice rolls as they happen
- Textual `RichLog` widget, stream updates via worker
- (This is the most standalone plan and can be skipped if time-boxed)

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|-----------------|--------|
| Mutable creature state | Pydantic v2 `model_copy(update=...)` | Adding fields to Creature is zero-risk — all copy-on-write already works |
| Custom dice logic | d20 library | Concentration save is just another `make_saving_throw()` call |
| No conditions | `list[str]` on Creature | Simple, sufficient for Phase 5; avoids over-engineering |
| No checkpointing | JSON file + `random.getstate()` | Human-readable, version-controllable checkpoint |

---

## Open Questions

1. **Should Stunned creatures still take actions this turn if stunned mid-turn?**
   - What we know: Stunned says "incapacitated" — cannot take actions or reactions
   - What's unclear: If a creature is stunned during another creature's turn, does it affect the stunned creature's *next* turn only, or also the current turn?
   - Recommendation: Apply immediately (current turn skipped if stunned) — conservative, easier to implement

2. **How does concentration interact with Haste specifically?**
   - What we know: Haste is a concentration buff that gives +2 AC, doubled speed, extra attack
   - What's unclear: Phase 5 success criteria only mention "Bless -> Haste ends Bless"; they don't require Haste's buff effects to work (no success criterion about Haste's mechanical benefits)
   - Recommendation: Implement concentration tracking (cast Haste = set `concentration="Haste"`) but defer Haste's buff effects. Just track that concentration is active.

3. **What spell triggers a condition for testing?**
   - What we know: No creature in the current data files applies conditions
   - What's unclear: Phase 5 success criteria don't specify which spell applies prone/frightened/stunned/grappled — just that the conditions work correctly when active
   - Recommendation: Add a test-only creature or action that applies "prone" condition directly, and test the mechanical effect. Don't need to implement full "Cause Fear" spell for the condition system to be testable.

4. **Should checkpoint include the seed for reproducibility?**
   - What we know: The CLI `--seed` flag currently seeds `random` before the run; checkpoints save RNG state mid-run
   - What's unclear: If user resumes with a different `--seed`, should the checkpoint's RNG state take precedence?
   - Recommendation: Checkpoint RNG state always wins on resume (it's the exact continuation point). Log a warning if `--seed` was specified alongside `--resume`.

---

## Sources

### Primary (HIGH confidence — codebase analysis)
- `/Users/enrico/workspace/myobsidian/dnd-simulator/src/domain/creature.py` — Pydantic v2 Creature model, verified `model_copy()` behavior
- `/Users/enrico/workspace/myobsidian/dnd-simulator/src/domain/combat_state.py` — Frozen dataclass with `update_creature()`, verified JSON serialization roundtrip
- `/Users/enrico/workspace/myobsidian/dnd-simulator/src/domain/dice.py` — `resolve_advantage()` ternary state machine accepting source lists
- `/Users/enrico/workspace/myobsidian/dnd-simulator/src/domain/rules.py` — `make_saving_throw()`, `apply_damage_modifiers()` existing patterns
- `/Users/enrico/workspace/myobsidian/dnd-simulator/src/simulation/simulator.py` — Attack resolution flow, AoE path, opportunity attacks
- `/Users/enrico/workspace/myobsidian/dnd-simulator/src/simulation/monte_carlo.py` — `_create_fresh_creatures()` pattern to extend
- `/Users/enrico/workspace/myobsidian/dnd-simulator/src/simulation/batch_runner.py` — `run_batch()` with `on_progress` callback to extend for checkpointing
- In-repo Python experiments confirming `Creature` extension, JSON serialization roundtrip, `random.getstate()/setstate()` behavior

### Secondary (HIGH confidence — official SRD)
- [5thsrd.org conditions](https://www.5esrd.com/gamemastering/conditions/) — Verified condition mechanical effects
- [5thsrd.org spells](https://5thsrd.org/spellcasting/what_is_a_spell/) — Verified spell slot rules

### Tertiary (MEDIUM confidence — community sources, consistent with SRD)
- [arcaneeye.com/mechanic-overview/concentration-5e/](https://arcaneeye.com/mechanic-overview/concentration-5e/) — Concentration DC = max(10, damage//2) confirmed
- [flutesloot.com concentration-rules](https://www.flutesloot.com/concentration-rules-explained-dnd-5e/) — Concentration break conditions confirmed

---

## Metadata

**Confidence breakdown:**
- D&D 5e rules: HIGH — Verified against official SRD and multiple consistent community sources
- Existing codebase patterns: HIGH — Direct code analysis and in-repo Python experiments run
- Serialization approach: HIGH — JSON roundtrip verified in-repo; `random.getstate()/setstate()` is stdlib behavior
- Plan structure: MEDIUM — Based on pattern from prior phases; actual complexity may require splitting or merging plans

**Research date:** 2026-02-11
**Valid until:** Phase 5 implementation (stable rules; no expiry concern)
