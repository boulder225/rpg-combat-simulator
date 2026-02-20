"""Load terrain from markdown files with YAML frontmatter."""

from pathlib import Path
import frontmatter

from src.domain.terrain import Terrain, CoverZone


def load_terrain(filepath: Path) -> Terrain:
    """Load terrain from a markdown file with YAML frontmatter.

    Args:
        filepath: Path to terrain .md file (e.g. data/terrain/arena.md).

    Returns:
        Terrain instance with name and cover_zones from frontmatter.
    """
    post = frontmatter.load(filepath)
    data = post.metadata
    name = data.get("name", filepath.stem)
    description = (post.content or "").strip()
    zones_data = data.get("cover_zones", [])
    cover_zones = []
    for z in zones_data:
        if isinstance(z, dict):
            zone_type = z.get("type", "half")
            if zone_type not in ("half", "three-quarters"):
                zone_type = "half"
            cells = z.get("cells")
            from_pos = z.get("from") or z.get("from_pos")
            to_pos = z.get("to") or z.get("to_pos")
            cover_zones.append(
                CoverZone(
                    type=zone_type,
                    cells=cells if isinstance(cells, list) else None,
                    from_pos=from_pos,
                    to_pos=to_pos,
                )
            )
    return Terrain(name=name, cover_zones=cover_zones, description=description)


class TerrainLoader:
    """Load terrain by name from a directory of .md files."""

    def __init__(self, terrain_dir: str = "data/terrain"):
        self.terrain_dir = Path(terrain_dir)

    def load(self, name: str) -> Terrain:
        """Load terrain by name (filename without .md)."""
        if name.endswith(".md"):
            name = name[:-3]
        path = self.terrain_dir / f"{name}.md"
        if not path.exists():
            raise FileNotFoundError(f"Terrain not found: {path}")
        return load_terrain(path)
