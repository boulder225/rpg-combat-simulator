"""Tests for terrain and cover zone models and loader."""

import pytest
from pathlib import Path

from src.domain.terrain import Terrain, CoverZone
from src.io.terrain_loader import load_terrain, TerrainLoader


def test_cover_zone_cells():
    """CoverZone with explicit cells."""
    z = CoverZone(type="half", cells=["B2", "B3"])
    assert z.type == "half"
    assert z.cell_set() == {"B2", "B3"}


def test_cover_zone_rectangle():
    """CoverZone with from/to rectangle expands to cell set."""
    z = CoverZone(type="three-quarters", from_pos="B2", to_pos="C3")
    assert z.type == "three-quarters"
    # B2=(1,1), C3=(2,2) -> B2, B3, C2, C3
    assert z.cell_set() == {"B2", "B3", "C2", "C3"}


def test_terrain_all_cover_cells():
    """Terrain.all_cover_cells returns cell -> type; three-quarters overrides half."""
    t = Terrain(
        name="x",
        cover_zones=[
            CoverZone(type="half", cells=["A1", "A2"]),
            CoverZone(type="three-quarters", cells=["A2"]),
        ],
    )
    cells = t.all_cover_cells()
    assert cells.get("A1") == "half"
    assert cells.get("A2") == "three-quarters"


def test_load_terrain_from_file():
    """Load terrain from fixture markdown."""
    path = Path(__file__).parent / "fixtures" / "terrain_arena.md"
    t = load_terrain(path)
    assert t.name == "Test Arena"
    assert len(t.cover_zones) == 2
    assert t.cover_zones[0].type == "half"
    assert "B2" in t.cover_zones[0].cell_set()
    assert t.cover_zones[1].type == "three-quarters"
    assert "D4" in t.cover_zones[1].cell_set()


def test_terrain_loader():
    """TerrainLoader loads by name from directory."""
    # Use fixtures path as terrain dir for test
    fixtures = Path(__file__).parent / "fixtures"
    loader = TerrainLoader(terrain_dir=str(fixtures))
    t = loader.load("terrain_arena")
    assert t.name == "Test Arena"
    assert len(t.cover_zones) >= 1
