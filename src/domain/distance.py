"""Grid system using chess notation (A1, B2, etc.) with Manhattan distance."""


def parse_coordinate(coord: str) -> tuple[int, int]:
    """Parse chess notation coordinate to (x, y) tuple.

    Args:
        coord: Chess notation like "A1", "C4", "Z20"

    Returns:
        Tuple of (x, y) zero-indexed coordinates

    Raises:
        ValueError: If coordinate format is invalid
    """
    if not coord or len(coord) < 2:
        raise ValueError(f"Invalid coordinate format: {coord}")

    file_char = coord[0].upper()
    rank_str = coord[1:]

    if not file_char.isalpha() or not ('A' <= file_char <= 'Z'):
        raise ValueError(f"Invalid file (column): {file_char}")

    try:
        rank = int(rank_str)
    except ValueError:
        raise ValueError(f"Invalid rank (row): {rank_str}")

    if not (1 <= rank <= 99):
        raise ValueError(f"Rank must be 1-99, got: {rank}")

    x = ord(file_char) - ord('A')
    y = rank - 1
    return (x, y)


def to_coordinate(x: int, y: int) -> str:
    """Convert (x, y) tuple to chess notation.

    Args:
        x: Zero-indexed column (0=A, 1=B, etc.)
        y: Zero-indexed row (0=rank 1, 1=rank 2, etc.)

    Returns:
        Chess notation string like "A1", "C4"
    """
    file_char = chr(x + ord('A'))
    rank = y + 1
    return f"{file_char}{rank}"


def manhattan_distance(a: str, b: str) -> int:
    """Calculate Manhattan distance between two positions in grid squares.

    Args:
        a: First position in chess notation
        b: Second position in chess notation

    Returns:
        Distance in grid squares (taxicab distance)
    """
    ax, ay = parse_coordinate(a)
    bx, by = parse_coordinate(b)
    return abs(ax - bx) + abs(ay - by)


def distance_in_feet(a: str, b: str) -> int:
    """Calculate distance in feet (Manhattan distance * 5).

    Args:
        a: First position in chess notation
        b: Second position in chess notation

    Returns:
        Distance in feet
    """
    return manhattan_distance(a, b) * 5


def move_toward(a: str, b: str, squares: int) -> str:
    """Move from position a toward position b up to specified squares.

    Args:
        a: Starting position
        b: Target position
        squares: Maximum movement in squares

    Returns:
        New position after moving toward target
    """
    ax, ay = parse_coordinate(a)
    bx, by = parse_coordinate(b)

    while squares > 0 and (ax != bx or ay != by):
        if ax < bx:
            ax += 1
        elif ax > bx:
            ax -= 1
        elif ay < by:
            ay += 1
        elif ay > by:
            ay -= 1
        squares -= 1

    return to_coordinate(ax, ay)
