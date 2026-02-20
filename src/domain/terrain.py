"""Terrain and cover zone models for grid-based cover."""

from typing import Literal, Optional
from pydantic import BaseModel

from src.domain.distance import parse_coordinate, to_coordinate


class CoverZone(BaseModel):
    """A zone that provides half or three-quarters cover.

    Define either by explicit cells (chess notation) or by a rectangle from/to.
    """

    type: Literal["half", "three-quarters"]
    cells: Optional[list[str]] = None
    from_pos: Optional[str] = None
    to_pos: Optional[str] = None

    def cell_set(self) -> set[str]:
        """Return the set of cells in this zone (normalized to uppercase)."""
        if self.cells and len(self.cells) > 0:
            return {c.upper().strip() for c in self.cells}
        if self.from_pos and self.to_pos:
            fx, fy = parse_coordinate(self.from_pos)
            tx, ty = parse_coordinate(self.to_pos)
            x_lo, x_hi = min(fx, tx), max(fx, tx)
            y_lo, y_hi = min(fy, ty), max(fy, ty)
            return {
                to_coordinate(x, y)
                for x in range(x_lo, x_hi + 1)
                for y in range(y_lo, y_hi + 1)
            }
        return set()


class Terrain(BaseModel):
    """Terrain with named cover zones."""

    name: str
    cover_zones: list[CoverZone] = []
    description: str = ""

    def all_cover_cells(self) -> dict[str, Literal["half", "three-quarters"]]:
        """Return map of cell -> strongest cover type in that cell.

        If a cell is in both half and three-quarters zones, three-quarters wins.
        """
        result: dict[str, Literal["half", "three-quarters"]] = {}
        for zone in self.cover_zones:
            for cell in zone.cell_set():
                if cell not in result or zone.type == "three-quarters":
                    result[cell] = zone.type
        return result
