"""Cover calculation: whether a target has cover from an attacker given terrain."""

from typing import Literal, Optional

from src.domain.distance import parse_coordinate, to_coordinate
from src.domain.terrain import Terrain


def _cells_on_path(from_pos: str, to_pos: str) -> list[str]:
    """Return cells on the Manhattan path from from_pos to to_pos (excluding endpoints)."""
    ax, ay = parse_coordinate(from_pos)
    bx, by = parse_coordinate(to_pos)
    out = []
    cx, cy = ax, ay
    while (cx, cy) != (bx, by):
        if cx < bx:
            cx += 1
        elif cx > bx:
            cx -= 1
        elif cy < by:
            cy += 1
        elif cy > by:
            cy -= 1
        if (cx, cy) != (bx, by):
            out.append(to_coordinate(cx, cy))
    return out


def get_cover(
    attacker_pos: str,
    target_pos: str,
    terrain: Optional[Terrain] = None,
) -> Literal["none", "half", "three-quarters"]:
    """Determine cover type for target from attacker's perspective.

    If terrain is None or has no cover zones, returns "none".
    Otherwise steps along the path from attacker to target; any cell on the path
    (excluding attacker and target) that lies in a cover zone grants the target
    that cover type. Strongest type wins (three-quarters > half).

    Args:
        attacker_pos: Attacker position in chess notation (e.g. "A1").
        target_pos: Target position in chess notation.
        terrain: Terrain with cover zones, or None for open field.

    Returns:
        "none", "half", or "three-quarters".
    """
    if attacker_pos.strip().upper() == target_pos.strip().upper():
        return "none"
    if terrain is None or not terrain.cover_zones:
        return "none"
    cover_cells = terrain.all_cover_cells()
    if not cover_cells:
        return "none"
    path = _cells_on_path(attacker_pos.strip().upper(), target_pos.strip().upper())
    best: Literal["half", "three-quarters"] | None = None
    for cell in path:
        cell_upper = cell.upper()
        if cell_upper in cover_cells:
            t = cover_cells[cell_upper]
            if t == "three-quarters":
                return "three-quarters"
            best = "half"
    return "none" if best is None else best
