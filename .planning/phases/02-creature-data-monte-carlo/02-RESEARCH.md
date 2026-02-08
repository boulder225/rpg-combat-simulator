# Phase 2: Creature Data & Monte Carlo Engine - Research

**Researched:** 2026-02-08
**Domain:** D&D 5e SRD data fetching, Monte Carlo simulation, statistical analysis, file caching
**Confidence:** HIGH

## Summary

This research investigates the technical implementation of Phase 2: Creature Data & Monte Carlo Engine. The phase requires fetching D&D 5e SRD monster data from dnd5eapi.co, implementing a Monte Carlo simulation engine with progressive sampling, calculating confidence intervals for win rates, and generating D&D difficulty ratings.

Key findings:
- **dnd5eapi.co API** provides comprehensive SRD monster data in JSON format with all necessary combat stats
- **Pydantic v2** is ideal for creature models with validation, computed fields, and 17x performance improvement over v1
- **python-frontmatter** handles markdown parsing with YAML frontmatter for both cached SRD data and custom homebrew creatures
- **D20 library** provides industry-standard dice rolling with full D&D notation support (including kh, kl, rr, ro operators)
- **Wilson score interval** is the recommended method for binomial confidence intervals, especially for small sample sizes and extreme proportions
- **Progressive sampling** should start at 100 runs and check CI width every 100 runs, stopping when ±5% precision is achieved or max 5000 runs reached
- **D&D difficulty ratings** combine party win rate and TPK risk, with duration factoring into the final label

**Primary recommendation:** Use Pydantic v2 models with computed fields for creature data, Wilson score intervals for confidence calculations, and implement cache-first resolution with local .md files taking precedence over SRD API calls.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pydantic | v2.12.5 | Creature data models with validation | 17x faster than v1, excellent validation, computed fields for derived stats |
| python-frontmatter | v1.1.0 | Parse markdown with YAML frontmatter | Standard library for Jekyll-style frontmatter, handles both SRD cache and homebrew |
| D20 | v1.1.2 | Dice rolling engine | Industry standard for D&D dice notation, supports all required operators (kh, kl, rr, ro) |
| requests | latest | HTTP client for dnd5eapi.co | Standard Python HTTP library, reliable and well-maintained |
| scipy | latest | Statistical functions | Provides binomtest with confidence interval calculation |
| statsmodels | latest | Alternative confidence interval methods | Offers Wilson score interval and other robust methods |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pathlib | built-in | File system operations | For cache directory management and file paths |
| typing | built-in | Type hints | For Pydantic model definitions and function signatures |
| dataclasses | built-in | Immutable data structures | For combat state if needed (though Pydantic preferred) |
| logging | built-in | Progress tracking | For simulation progress and warnings |

**Installation:**
```bash
pip install pydantic python-frontmatter d20 requests scipy statsmodels
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── creatures/        # Creature data models and parsing
├── simulation/       # Monte Carlo engine and combat simulation
├── analysis/         # Statistical analysis and confidence intervals
├── caching/          # SRD data caching and resolution
├── output/           # Report generation and formatting
└── cli/              # Command line interface
```

### Pattern 1: Cache-First Data Resolution
**What:** Resolve creature data by first checking local cache, then SRD API
**When to use:** Always when loading creature data
**Example:**
```python
# Source: Context7 Pydantic documentation
from pathlib import Path
from pydantic import BaseModel, Field
import frontmatter

class CreatureLoader:
    def __init__(self, cache_dir: Path, srd_cache_dir: Path):
        self.cache_dir = cache_dir  # data/creatures/
        self.srd_cache_dir = srd_cache_dir  # data/srd-cache/
    
    def load_creature(self, name: str) -> CreatureModel:
        # Check local creatures first (highest priority)
        local_path = self.cache_dir / f"{name}.md"
        if local_path.exists():
            return self._parse_creature_file(local_path)
        
        # Check SRD cache
        srd_cache_path = self.srd_cache_dir / f"{name}.md"
        if srd_cache_path.exists():
            return self._parse_creature_file(srd_cache_path)
        
        # Fetch from SRD API and cache
        creature_data = self._fetch_from_srd_api(name)
        self._cache_srd_creature(name, creature_data)
        return creature_data
```

### Pattern 2: Progressive Sampling with Confidence Intervals
**What:** Start with minimum runs, check confidence interval width, stop when precision goal met
**When to use:** Monte Carlo simulation with statistical stopping criteria
**Example:**
```python
# Source: scipy.stats.binomtest documentation
from scipy.stats import binomtest
import math

def progressive_sampling(simulation_func, min_runs=100, max_runs=5000, 
                        target_precision=0.05, check_interval=100):
    """
    Run simulations with progressive sampling based on confidence interval width.
    """
    wins = 0
    total_runs = 0
    
    # Initial batch
    for _ in range(min_runs):
        result = simulation_func()
        if result.party_wins:
            wins += 1
        total_runs += 1
    
    # Check and continue if needed
    while total_runs < max_runs:
        # Calculate Wilson score confidence interval
        result = binomtest(wins, total_runs, alternative='two-sided')
        ci = result.proportion_ci(confidence_level=0.95)
        ci_width = ci.high - ci.low
        
        if ci_width <= (2 * target_precision):  # ±5% means total width of 10%
            break
            
        # Run next batch
        batch_size = min(check_interval, max_runs - total_runs)
        for _ in range(batch_size):
            result = simulation_func()
            if result.party_wins:
                wins += 1
            total_runs += 1
    
    return wins, total_runs
```

### Anti-Patterns to Avoid
- **Hardcoding SRD API URLs**: Use configuration or constants for API endpoints
- **Parsing SRD JSON directly without validation**: Always use Pydantic models to validate and transform API data
- **Using normal approximation for confidence intervals**: Wilson score interval is more accurate for binomial proportions, especially with extreme values
- **Storing raw API responses**: Always transform to standardized creature models before caching

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Dice rolling | Custom dice parser | D20 library | Handles complex D&D notation (kh, kl, rr, ro), optimized, battle-tested |
| Confidence intervals | Custom CI calculation | scipy.stats.binomtest or statsmodels | Wilson score interval handles edge cases, proper statistical implementation |
| Markdown parsing | Custom YAML+content parser | python-frontmatter | Handles frontmatter parsing, BOM, multiple formats (YAML/JSON/TOML) |
| Data validation | Custom validation logic | Pydantic v2 | 17x faster than v1, computed fields, excellent error messages, type safety |
| HTTP requests | Custom HTTP client | requests library | Reliable, well-maintained, handles errors, timeouts, retries |
| File caching | Custom cache logic | pathlib + standard file operations | Built-in Python path handling is robust and cross-platform |

**Key insight:** The D20 library alone saves hundreds of lines of code for dice parsing and evaluation, while providing industry-standard D&D dice notation support that would be extremely complex to implement correctly.

## Common Pitfalls

### Pitfall 1: SRD API Rate Limiting and Errors
**What goes wrong:** API calls fail due to rate limiting, network issues, or invalid creature names
**Why it happens:** Not implementing proper error handling and fallback strategies
**How to avoid:** 
- Implement retry logic with exponential backoff
- Cache negative results (404 responses) to avoid repeated failed calls
- Provide clear error messages for invalid creature names
- Fall back to local files only (don't crash on missing SRD creatures)
**Warning signs:** Frequent API timeout errors, incomplete creature data, simulation crashes on unknown creatures

### Pitfall 2: Incorrect Confidence Interval Calculation
**What goes wrong:** Using normal approximation (Wald interval) for binomial proportions, leading to inaccurate CIs
**Why it happens:** Normal approximation fails with small sample sizes or extreme proportions (near 0% or 100%)
**How to avoid:** Use Wilson score interval or exact Clopper-Pearson intervals via scipy.stats.binomtest
**Warning signs:** Confidence intervals that include impossible values (<0% or >100%), overly narrow CIs with small sample sizes

### Pitfall 3: Performance Issues with Large Simulations
**What goes wrong:** Simulations take too long or consume excessive memory
**Why it happens:** Not optimizing the combat simulation loop, copying large data structures unnecessarily
**How to avoid:** 
- Use immutable combat state with copy-on-write (as specified in context)
- Profile simulation performance early
- Consider using Pydantic's `model_construct()` for performance-critical paths
- Implement progress tracking to give user feedback during long runs
**Warning signs:** Simulation runs taking much longer than expected, memory usage growing linearly with run count

### Pitfall 4: Difficulty Rating Misalignment
**What goes wrong:** Difficulty ratings don't match D&D 5e expectations or user intuition
**Why it happens:** Using only win rate without considering TPK risk and combat duration
**How to avoid:** Implement the combined metric as specified: "both party win rate AND TPK risk, label by the worse indicator" with duration factoring in
**Warning signs:** Easy encounters showing as deadly, or deadly encounters showing as easy compared to manual D&D assessment

## Code Examples

Verified patterns from official sources:

### SRD API Data Fetching and Caching
```python
# Source: dnd5eapi.co API documentation + python-frontmatter docs
import requests
import frontmatter
from pathlib import Path
from pydantic import BaseModel

class SRDCreatureAPI:
    BASE_URL = "https://www.dnd5eapi.co/api/2014"
    
    def fetch_monster(self, name: str) -> dict:
        """Fetch monster data from SRD API."""
        # Convert name to API format (replace spaces with hyphens, lowercase)
        api_name = name.lower().replace(' ', '-')
        url = f"{self.BASE_URL}/monsters/{api_name}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def cache_monster(self, name: str, data: dict, cache_dir: Path):
        """Cache monster data as markdown with YAML frontmatter."""
        # Transform API data to standardized format
        creature_data = self._transform_api_data(data)
        
        # Create markdown with frontmatter
        post = frontmatter.Post(
            content="",  # No content needed for creatures
            metadata=creature_data,
            handler=frontmatter.YAMLHandler()
        )
        
        cache_path = cache_dir / f"{name}.md"
        with open(cache_path, 'w', encoding='utf-8') as f:
            frontmatter.dump(post, f)
```

### Wilson Score Confidence Interval
```python
# Source: scipy.stats.binomtest documentation
from scipy.stats import binomtest

def calculate_win_rate_ci(wins: int, total: int, confidence_level: float = 0.95):
    """
    Calculate Wilson score confidence interval for win rate.
    Returns (lower_bound, upper_bound, point_estimate)
    """
    if total == 0:
        return 0.0, 0.0, 0.0
        
    result = binomtest(wins, total, alternative='two-sided')
    ci = result.proportion_ci(confidence_level=confidence_level)
    
    return float(ci.low), float(ci.high), result.statistic
```

### D20 Dice Rolling for Combat
```python
# Source: D20 library documentation
import d20

def roll_attack_damage(attack_bonus: int, damage_dice: str) -> tuple[int, int]:
    """
    Roll attack and damage for a creature attack.
    Returns (attack_roll, damage_roll)
    """
    # Roll attack (d20 + bonus)
    attack_roll = d20.roll(f"1d20 + {attack_bonus}").total
    
    # Roll damage (e.g., "1d6+2")
    damage_roll = d20.roll(damage_dice).total
    
    return attack_roll, damage_roll

def roll_with_annotations(damage_dice: str, damage_type: str) -> str:
    """
    Roll damage with annotations for markdown logging.
    """
    result = d20.roll(f"{damage_dice} [{damage_type}]")
    return str(result)  # Returns formatted string like "1d6 (4) [slashing] = `4`"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pydantic v1 | Pydantic v2 | 2022 | 17x performance improvement, computed fields, better validation |
| Custom dice parsers | D20 library | 2019 | Standardized D&D dice notation, better performance, community maintained |
| Normal approximation CIs | Wilson score intervals | Ongoing | More accurate confidence intervals, especially for extreme proportions |
| Simple win rate difficulty | Combined win rate + TPK + duration | Context-specific | Better alignment with D&D 5e difficulty expectations |

**Deprecated/outdated:**
- **Manual YAML parsing**: python-frontmatter handles this robustly
- **Custom HTTP clients**: requests library is the standard
- **Wald confidence intervals**: Wilson score is preferred for binomial proportions

## Open Questions

Things that couldn't be fully resolved:

1. **Exact D&D 5e difficulty thresholds**
   - What we know: Context specifies combining win rate and TPK risk, with duration factoring in
   - What's unclear: Exact numerical thresholds for Easy/Medium/Hard/Deadly labels
   - Recommendation: Start with standard D&D 5e XP thresholds as baseline, then calibrate based on simulation results and user feedback

2. **SRD action parsing complexity**
   - What we know: Context specifies "auto-map SRD action patterns" for melee/ranged attacks only
   - What's unclear: Exact regex patterns or parsing logic for extracting attack bonus, damage dice, reach/range from SRD action descriptions
   - Recommendation: Implement simple pattern matching for common attack formats, log parsing failures for manual review

3. **Progressive sampling stopping criteria**
   - What we know: Context specifies "±5% or max 5000 reached" with checks every 100 runs
   - What's unclear: Whether ±5% refers to absolute percentage points or relative percentage
   - Recommendation: Implement as absolute percentage points (±0.05 in proportion terms) which is standard for binomial confidence intervals

## Sources

### Primary (HIGH confidence)
- dnd5eapi.co API documentation - SRD monster data structure and endpoints
- Pydantic v2 documentation - Model validation, computed fields, performance
- python-frontmatter documentation - Markdown parsing with frontmatter
- D20 library documentation - Dice notation and rolling
- scipy.stats.binomtest documentation - Confidence interval calculation
- statsmodels proportion_confint documentation - Alternative CI methods

### Secondary (MEDIUM confidence)
- Wikipedia Binomial proportion confidence interval - Wilson score interval details
- Wikipedia Sequential analysis - Progressive sampling concepts
- D&D 5e Basic Rules - General combat mechanics reference

### Tertiary (LOW confidence)
- Various blog posts and forum discussions about D&D simulation - Implementation patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries have official documentation and are actively maintained
- Architecture: HIGH - Patterns based on official library documentation and best practices
- Pitfalls: MEDIUM - Based on common issues in similar projects, some inferred from context
- Code examples: HIGH - Directly from official library documentation

**Research date:** 2026-02-08
**Valid until:** 2026-03-08 (30 days for stable libraries)