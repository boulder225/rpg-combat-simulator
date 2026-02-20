# Plan 04-01: Terrain Model and Cover Calculation — Summary

## Overview
Implemented terrain and cover zone domain models, cover calculation via ray stepping, and terrain loader from markdown. No simulator or rules changes yet.

## Deliverables
- `src/domain/terrain.py` — Terrain and CoverZone Pydantic models; CoverZone supports cells list or from_pos/to_pos rectangle; cell_set() returns normalized set; Terrain.all_cover_cells() for cover lookup
- `src/domain/cover.py` — get_cover(attacker_pos, target_pos, terrain) with _cells_on_path (Manhattan path); returns "none" | "half" | "three-quarters"
- `src/io/terrain_loader.py` — load_terrain(path), TerrainLoader(terrain_dir).load(name); YAML name, cover_zones (type, cells or from/to)
- `tests/test_terrain.py` — CoverZone cells/rectangle, Terrain.all_cover_cells, load_terrain, TerrainLoader
- `tests/test_cover.py` — get_cover no/empty terrain, same position, ray through half/three-quarters/both, open field
- `data/terrain/.gitkeep` — terrain data directory
- `tests/fixtures/terrain_arena.md` — fixture terrain with half and three-quarters zones

## Verification
- `uv run pytest tests/test_terrain.py tests/test_cover.py -v` — 12 passed
- `python -c "from src.domain.terrain import Terrain, CoverZone; z = CoverZone(type='half', cells=['B2','B3']); t = Terrain(name='arena', cover_zones=[z]); print(t.name)"` — arena

## Issues/Deviations
- Pydantic v2 does not support returning a new instance from model_validator when validating via __init__; CoverZone.cell_set() computes rectangle from from_pos/to_pos on the fly instead of mutating cells.
