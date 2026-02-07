# Technology Stack Research

**Project:** D&D 5e Combat Simulator
**Domain:** Terminal-based tactical combat simulator with AI agents
**Researched:** 2026-02-07
**Confidence:** HIGH

## Recommended Stack

### Core Framework

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Python** | 3.11+ | Runtime environment | M1-optimized, stable async, modern typing features. 3.11 offers 25% performance improvement over 3.10. Avoid 3.14 (too new, library compatibility concerns). |
| **Textual** | 7.5.0 | Terminal UI framework | Modern reactive TUI framework with live updates, rich widgets (tables, progress bars, logs), CSS-like styling. Built by Textualize (same team as Rich). Active maintenance, released Jan 30, 2026. |
| **Pydantic** | 2.12.5 | Data validation & models | Industry standard for D&D stat modeling. Runtime validation, YAML deserialization with type safety, computed fields for derived stats. v2 has major performance improvements. |
| **python-frontmatter** | 1.1.0 | Markdown+YAML parsing | Community standard for frontmatter extraction. Simple API, stable (production/stable status). Parses creature .md files with YAML headers seamlessly. |

### LLM Integration

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| **ollama** | 0.6.1 | Local LLM inference | Official Ollama Python SDK. Simple API (`chat()`, `generate()`, `embed()`). Runs on M1 hardware, supports 7B models (Mistral, Llama 3.3). No GPU required. |
| **openrouter** | 0.6.0 | Cloud LLM fallback | Official OpenRouter SDK with 300+ models. Type-safe, async support, automatic retries. Recent release (Feb 6, 2026) shows active development. Beta status acceptable for this use case. |
| **httpx** | 0.28.1 | HTTP client | Modern async HTTP client for API calls. Connection pooling, HTTP/2 support. Drop-in async replacement for requests. Required for robust LLM API interactions. |

### D&D Domain

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| **d20** | 1.1.2 | Dice engine | Fast, secure dice parser for D&D notation (`4d6kh3`, advantage, etc.). Tree-based result structure enables detailed combat logging. Security features prevent malicious expressions. |
| **dnd5epy** | 1.0.7 | SRD API client | Auto-generated OpenAPI client for dnd5eapi.co. Covers all SRD 2014 content (monsters, spells, conditions, etc.). No auth required. MIT licensed. |

### Development Tools

| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| **uv** | 0.10.0 | Package manager | 10-100x faster than pip. Manages Python versions, dependencies, lockfiles. Rust-based, production-stable. Replaces pip, venv, pyenv in one tool. |
| **ruff** | 0.15.0 | Linter & formatter | 10-100x faster than flake8/black. Replaces 8+ tools (isort, pyupgrade, etc.). Rust-based. Released with 2026 style guide support (Feb 3, 2026). |
| **mypy** | 1.19.1 | Static type checker | Industry standard for Python type checking. Required for Pydantic integration. Gradual typing allows incremental adoption. |
| **pytest** | latest | Test framework | Standard Python testing. Plugin ecosystem (pytest-asyncio, pytest-cov). |
| **pytest-asyncio** | 1.3.0 | Async test support | Official async support for pytest. Required for testing LLM agents and async combat logic. Requires Python 3.10+. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **rich** | 14.3.2 | Console rendering | Textual dependency. Used for markdown rendering in logs, syntax highlighting. Compatible with Textual (sister project). |
| **pathlib** | stdlib | Path manipulation | Object-oriented path handling. Cross-platform. Modern replacement for os.path (15% slower but vastly more readable). |
| **typing** | stdlib | Type annotations | Use modern syntax: `list[str]` (3.9+), `X \| Y` (3.10+). Avoid typing.List, typing.Union. |
| **dataclasses** | stdlib | Data structures | Use with Pydantic for clean stat blocks. Standard library, zero overhead. |

## Installation

```bash
# Use uv for package management (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python 3.11
uv python install 3.11

# Create project
uv init dnd-simulator
cd dnd-simulator

# Core dependencies
uv add textual pydantic python-frontmatter

# LLM dependencies
uv add ollama openrouter httpx

# D&D domain
uv add d20 dnd5epy

# Supporting libraries
uv add rich

# Dev dependencies
uv add --dev ruff mypy pytest pytest-asyncio pytest-cov
```

## Alternatives Considered

| Category | Recommended | Alternative | Why Not Alternative |
|----------|-------------|-------------|---------------------|
| **TUI Framework** | Textual | Rich + Blessed | Rich lacks TUI widgets. Blessed is low-level, no reactive model. Textual is modern, actively developed. |
| **TUI Framework** | Textual | urwid | urwid uses callback-based model (hard to reason about). Textual is async-first, better for LLM integration. |
| **Data Validation** | Pydantic v2 | marshmallow | Pydantic v2 is 17x faster. Better type inference, computed fields, strict mode. Industry momentum behind Pydantic. |
| **Data Validation** | Pydantic v2 | attrs + cattrs | Good combo but more manual. Pydantic has YAML integration, validators, computed properties built-in. |
| **LLM Local** | ollama | llama.cpp bindings | ollama wraps llama.cpp with better UX. Model management, API server, simpler Python SDK. |
| **LLM Cloud** | OpenRouter | direct OpenAI/Anthropic | OpenRouter aggregates 300+ models with unified API. Cost optimization, fallback logic. Better for experimentation. |
| **Dice Engine** | d20 | custom dice roller | d20 has security features (execution limits), supports full D&D notation, tree-based results for logging. Don't reinvent. |
| **Package Manager** | uv | pip + venv | uv is 10-100x faster, manages Python versions, lockfiles, workspaces. Poetry-like UX. Modern standard. |
| **Linter** | ruff | flake8 + black + isort | ruff replaces 8+ tools, 10-100x faster. Single config file. Active development (Feb 2026 release). |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **requests** | No async support, development stalled | httpx (async + sync, actively maintained) |
| **os.path** | String-based, platform-specific code | pathlib (object-oriented, cross-platform) |
| **typing.List, typing.Dict** | Deprecated in Python 3.9+ | Built-in `list[T]`, `dict[K, V]` |
| **Python 3.8** | EOL October 2024, no modern typing | Python 3.11+ (performance, typing improvements) |
| **Python 3.14** | Too new (released Oct 2025), library compatibility issues | Python 3.11 or 3.12 (stable, widely supported) |
| **Pydantic v1** | 17x slower than v2, deprecated | Pydantic v2 (current: 2.12.5) |
| **black** | Slower, less configurable | ruff format (compatible, 10x faster) |
| **transformers (Hugging Face)** | Too heavy for 7B models on 16GB RAM | ollama (optimized for consumer hardware) |

## Stack Patterns by Variant

### For Heuristic Agents (Phase 1-2)
- Use Pydantic models + d20 + dnd5epy
- No LLM dependencies
- Focus on combat engine correctness
- **Rationale:** Validate core mechanics before adding LLM complexity

### For LLM Agents (Phase 3+)
- Add ollama for local inference
- Add openrouter for cloud fallback
- Use httpx for robust API calls
- **Rationale:** Local-first (privacy, latency), cloud for experimentation

### For Testing
- pytest for sync tests
- pytest-asyncio for LLM agent tests
- Use fixtures for creature data (load from .md files)
- **Rationale:** Test heuristic logic synchronously, LLM calls asynchronously

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| **textual 7.5.0** | Python 3.9-3.13 | Requires rich (auto-installed). Works on M1 macOS. |
| **pydantic 2.12.5** | Python 3.9+ | Breaking changes from v1. Use migration guide if needed. |
| **pytest-asyncio 1.3.0** | Python 3.10+ | **Constraint: Requires Python 3.10+** (blocks 3.9). Textual works on 3.9, but async testing requires 3.10. |
| **ollama 0.6.1** | Python 3.8+ | Requires Ollama server installed separately (`brew install ollama`). |
| **openrouter 0.6.0** | Python 3.9.2+ | Beta status. API may change between minor versions. Pin version in production. |
| **d20 1.1.2** | Python 3.6+ | Older but stable. No updates since 2021 (feature-complete). |
| **dnd5epy 1.0.7** | Python 3.7-3.11 | Auto-generated from OpenAPI. May need updates if API changes. |

**Python Version Decision: 3.11**
- Lower bound: 3.10 (pytest-asyncio requirement)
- Upper bound: 3.13 (avoid 3.14 for stability)
- **Choose 3.11:** Performance boost over 3.10, stable, M1-optimized

## M1 Mac Specific Considerations

| Concern | Recommendation |
|---------|----------------|
| **Python Distribution** | Use uv-managed Python (ARM64-native). Avoid system Python 2.7. |
| **Ollama Models** | Use GGUF quantized models (Q4_K_M). Mistral 7B: ~4.5GB RAM, Llama 3.3 7B: ~5GB RAM. Leaves ~10GB for OS + app. |
| **Memory Budget** | 16GB total. Reserve 6GB for OS, 6GB for largest LLM, 4GB for app/data. Monitor with `ollama ps`. |
| **Performance** | M1 runs 7B models at ~20 tokens/sec. Acceptable for turn-based combat (not real-time). |

## Sources

### Official Documentation & PyPI (HIGH Confidence)
- [Textual 7.5.0 - PyPI](https://pypi.org/project/textual/) - Current version verified Jan 30, 2026
- [Pydantic 2.12.5 - PyPI](https://pypi.org/project/pydantic/) - Current version verified Nov 26, 2025
- [python-frontmatter 1.1.0 - PyPI](https://pypi.org/project/python-frontmatter/) - Current version verified Jan 16, 2024
- [ollama 0.6.1 - PyPI](https://pypi.org/project/ollama/) - Current version verified Nov 13, 2025
- [openrouter 0.6.0 - PyPI](https://pypi.org/project/openrouter/) - Current version verified Feb 6, 2026
- [httpx 0.28.1 - PyPI](https://pypi.org/project/httpx/) - Current version verified Dec 6, 2024
- [d20 1.1.2 - PyPI](https://pypi.org/project/d20/) - Current version verified Jul 8, 2021
- [dnd5epy 1.0.7 - PyPI](https://pypi.org/project/dnd5epy/) - Current version verified Jun 24, 2023
- [rich 14.3.2 - PyPI](https://pypi.org/project/rich/) - Current version verified Feb 1, 2026
- [ruff 0.15.0 - PyPI](https://pypi.org/project/ruff/) - Current version verified Feb 3, 2026
- [mypy 1.19.1 - PyPI](https://pypi.org/project/mypy/) - Current version verified Dec 15, 2025
- [pytest-asyncio 1.3.0 - PyPI](https://pypi.org/project/pytest-asyncio/) - Current version verified Nov 10, 2025
- [uv 0.10.0 - PyPI](https://pypi.org/project/uv/) - Current version verified Feb 5, 2026

### Community & Best Practices (MEDIUM Confidence)
- [Python Typing Best Practices](https://typing.python.org/en/latest/reference/best_practices.html) - Official typing docs
- [Pathlib vs os.path](https://www.pythonsnacks.com/p/paths-in-python-comparing-os-path-and-pathlib) - Pathlib strongly recommended for modern Python
- [Ollama Python Integration - Real Python](https://realpython.com/ollama-python/) - Tutorial on local LLM usage
- [Textual Documentation](https://textual.textualize.io/) - Official framework docs

### API & Domain Sources (HIGH Confidence)
- [D&D 5e API](https://www.dnd5eapi.co/) - SRD 2014 data source
- [OpenRouter API Docs](https://openrouter.ai/docs/quickstart) - Cloud LLM aggregator

---
*Stack research for: D&D 5e Combat Simulator with LLM Agents*
*Researched: 2026-02-07*
*Constraints: M1 Mac 16GB RAM, Python, SRD 2014, local 7B LLMs*
