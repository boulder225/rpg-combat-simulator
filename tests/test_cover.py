"""Tests for get_cover calculation."""

import pytest
from src.domain.terrain import Terrain, CoverZone
from src.domain.cover import get_cover


def test_get_cover_no_terrain():
    """No terrain returns none."""
    assert get_cover("A1", "C3", None) == "none"


def test_get_cover_empty_terrain():
    """Terrain with no cover zones returns none."""
    t = Terrain(name="open", cover_zones=[])
    assert get_cover("A1", "C3", t) == "none"


def test_get_cover_same_position():
    """Attacker and target same cell returns none."""
    t = Terrain(name="x", cover_zones=[CoverZone(type="half", cells=["A1"])])
    assert get_cover("A1", "A1", t) == "none"


def test_get_cover_ray_through_half_zone():
    """Path from A1 to C3 passing through B2; B2 in half zone -> half cover."""
    # A1=(0,0), C3=(2,2). Manhattan path: A1 -> (1,0) or (0,1) -> ... -> C3.
    # One possible path is A1, B1, C1, C2, C3 - or A1, A2, A3, B3, C3 - or diagonal-ish A1, B2, C3.
    # Our _cells_on_path steps: first dx then dy. So from (0,0) to (2,2): cx<bx so cx=1, then cx=2; then cy<by so cy=1, then cy=2.
    # So path: (1,0), (2,0), (2,1), (2,2) but we exclude (2,2) so path = (1,0), (2,0), (2,1) = B1, C1, C2.
    # So if we put half cover at B2, path doesn't cross it. Let me use a path that clearly crosses: A1 to A3, path = A2. Zone at A2 -> half.
    t = Terrain(
        name="x",
        cover_zones=[CoverZone(type="half", cells=["A2"])],
    )
    assert get_cover("A1", "A3", t) == "half"


def test_get_cover_ray_through_three_quarters_zone():
    """Path through three-quarters zone returns three-quarters."""
    t = Terrain(
        name="x",
        cover_zones=[CoverZone(type="three-quarters", cells=["B2"])],
    )
    # A1 to B3: path is B1, B2 (B2 in zone)
    assert get_cover("A1", "B3", t) == "three-quarters"


def test_get_cover_ray_through_both_zones_returns_strongest():
    """Path through both half and three-quarters returns three-quarters."""
    t = Terrain(
        name="x",
        cover_zones=[
            CoverZone(type="half", cells=["B1"]),
            CoverZone(type="three-quarters", cells=["C1"]),
        ],
    )
    # A1 to C3: path is B1, C1, C2 (B1 half, C1 three-quarters)
    assert get_cover("A1", "C3", t) == "three-quarters"


def test_get_cover_open_field():
    """Path not through any zone returns none."""
    t = Terrain(
        name="x",
        cover_zones=[CoverZone(type="half", cells=["Z10"])],
    )
    assert get_cover("A1", "C3", t) == "none"
