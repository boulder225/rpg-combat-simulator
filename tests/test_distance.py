"""Tests for grid system and distance calculations."""

import pytest
from src.domain.distance import (
    parse_coordinate,
    to_coordinate,
    manhattan_distance,
    distance_in_feet,
    move_toward,
)


def test_parse_coordinate_basic():
    """Test parsing basic chess notation."""
    assert parse_coordinate("A1") == (0, 0)
    assert parse_coordinate("B2") == (1, 1)
    assert parse_coordinate("C4") == (2, 3)
    assert parse_coordinate("Z20") == (25, 19)


def test_parse_coordinate_case_insensitive():
    """Test that parsing handles lowercase."""
    assert parse_coordinate("a1") == (0, 0)
    assert parse_coordinate("c4") == (2, 3)


def test_parse_coordinate_large_ranks():
    """Test parsing large rank numbers."""
    assert parse_coordinate("A99") == (0, 98)
    assert parse_coordinate("Z99") == (25, 98)


def test_parse_coordinate_invalid_empty():
    """Test that empty string raises ValueError."""
    with pytest.raises(ValueError, match="Invalid coordinate format"):
        parse_coordinate("")


def test_parse_coordinate_invalid_too_short():
    """Test that too-short string raises ValueError."""
    with pytest.raises(ValueError, match="Invalid coordinate format"):
        parse_coordinate("A")


def test_parse_coordinate_invalid_file():
    """Test that invalid file character raises ValueError."""
    with pytest.raises(ValueError, match="Invalid file"):
        parse_coordinate("11")
    with pytest.raises(ValueError, match="Invalid file"):
        parse_coordinate("@1")


def test_parse_coordinate_invalid_rank():
    """Test that invalid rank raises ValueError."""
    with pytest.raises(ValueError, match="Invalid rank"):
        parse_coordinate("Aabc")


def test_parse_coordinate_invalid_rank_range():
    """Test that rank out of range raises ValueError."""
    with pytest.raises(ValueError, match="Rank must be 1-99"):
        parse_coordinate("A0")
    with pytest.raises(ValueError, match="Rank must be 1-99"):
        parse_coordinate("A100")


def test_to_coordinate_basic():
    """Test converting coordinates to chess notation."""
    assert to_coordinate(0, 0) == "A1"
    assert to_coordinate(1, 1) == "B2"
    assert to_coordinate(2, 3) == "C4"
    assert to_coordinate(25, 19) == "Z20"


def test_to_coordinate_roundtrip():
    """Test that parse and to_coordinate are inverses."""
    coords = ["A1", "B2", "C4", "E5", "Z20"]
    for coord in coords:
        x, y = parse_coordinate(coord)
        assert to_coordinate(x, y) == coord


def test_manhattan_distance_basic():
    """Test basic Manhattan distance calculations."""
    assert manhattan_distance("A1", "A1") == 0
    assert manhattan_distance("A1", "B1") == 1
    assert manhattan_distance("A1", "A2") == 1
    assert manhattan_distance("A1", "B2") == 2
    assert manhattan_distance("A1", "C4") == 5


def test_manhattan_distance_symmetric():
    """Test that distance is symmetric."""
    assert manhattan_distance("A1", "C4") == manhattan_distance("C4", "A1")
    assert manhattan_distance("B2", "E5") == manhattan_distance("E5", "B2")


def test_manhattan_distance_large():
    """Test distance with larger coordinates."""
    assert manhattan_distance("A1", "Z20") == 44  # 25 + 19


def test_distance_in_feet():
    """Test distance conversion to feet."""
    assert distance_in_feet("A1", "A1") == 0
    assert distance_in_feet("A1", "B1") == 5
    assert distance_in_feet("A1", "A2") == 5
    assert distance_in_feet("A1", "C4") == 25  # 5 squares * 5 feet


def test_move_toward_no_movement():
    """Test move_toward with zero movement."""
    assert move_toward("A1", "C4", 0) == "A1"


def test_move_toward_reach_target():
    """Test move_toward that reaches target."""
    assert move_toward("A1", "C1", 2) == "C1"
    assert move_toward("A1", "A3", 2) == "A3"


def test_move_toward_partial():
    """Test move_toward with partial movement."""
    result = move_toward("A1", "C4", 2)
    # Should move toward C4, prioritizing horizontal/vertical
    assert manhattan_distance("A1", result) == 2
    assert manhattan_distance(result, "C4") < manhattan_distance("A1", "C4")


def test_move_toward_already_there():
    """Test move_toward when already at target."""
    assert move_toward("C4", "C4", 5) == "C4"


def test_move_toward_more_than_needed():
    """Test move_toward with excess movement."""
    # Distance from A1 to C1 is 2, but we have 5 movement
    assert move_toward("A1", "C1", 5) == "C1"


def test_move_toward_diagonal():
    """Test move_toward with diagonal movement (Manhattan style)."""
    result = move_toward("A1", "C3", 4)
    # Should reach C3 (2 right, 2 up = 4 Manhattan distance)
    assert result == "C3"
