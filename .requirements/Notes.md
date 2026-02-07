## 3. Rules Source (SRD 2014)

- Primary (online/quick): [https://www.dnd5eapi.co/](https://www.dnd5eapi.co/) (REST + GraphQL endpoints)
    - Examples: /api/monsters/goblin, /api/spells/fireball, /api/rule/conditions
- Offline fallback: clone [https://github.com/5e-bits/5e-database](https://github.com/5e-bits/5e-database) (JSON files: monsters/, spells/, etc.)
- Avoid: using LLMs as primary rules source (too error-prone on exact details).

## 4. Agent Decision System (Core Feature)

Three tiers of intelligence (speed vs tactical quality trade-off):

|Tier|Decision Method|Speed|Strategy Variety|Balance Testing Utility|
|---|---|---|---|---|
|1|Fixed heuristics|Very fast|Low|★★★☆☆ (great for Monte-Carlo)|
|2|Heuristics + LLM for key choices|Medium|Medium|★★★★☆|
|3|Full LLM per turn|Slow–medium|High|★★★★★ (diverse strategies)|

Hardware constraints: Apple M1, 16 GB unified RAM, ~23 GB free space.

**Local (Ollama – free, offline) recommendations**:

- Best balance: qwen2.5:7b-instruct or qwen2.5-coder:7b-instruct (~4.5–6 GB quantized) → Strong reasoning & tactical performance for a 7B model → ~20–35 tokens/second on M1
- Lightweight alternatives: nemotron-mini:4b, llama3.2:3b-instruct
- Avoid: qwen2.5:14b (too much VRAM pressure / swap)

**Cloud (recommended for serious batch runs)**:

- **OpenRouter** – models:
    - qwen/qwen2.5-coder-7b-instruct
    - qwen/qwen2.5-14b-instruct
- Pricing (approx. 2026): $0.03–0.15 per million tokens input/output → Full simulation (10 creatures × 8 rounds): ~$0.01–0.03 → Latency: 0.6–2 seconds per decision → complete run < 2 minutes
- OpenAI-compatible API: base_url = "[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)"

## 7. Main Remaining Challenges & Pragmatic Compromises

- Precise cover / advantage without full grid → simple rules (adjacent ally = half cover possible, distance-based).
- Persistent conditions / concentration → per-creature condition dict + auto-triggers.
- Realistic target priority → heuristics (lowest HP? highest DPR threat? spellcaster?) + LLM evaluation.
- Speed vs intelligence → easy toggle between heuristic and LLM mode.
- LLM output parsing → enforce rigid format with <thinking> + uppercase keys.

## 8. Suggested Next Steps

1. Build minimal prototype: parse .md creatures → basic heuristic loop + initiative.
2. Add local LLM (Ollama qwen2.5:7b) for tactical decisions.
3. Switch to OpenRouter for fast Monte-Carlo batches.
4. Implement stats output: win %, average duration, damage taken by PCs.