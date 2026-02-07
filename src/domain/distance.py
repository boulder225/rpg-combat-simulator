def manhattan_distance(a: str, b: str) -> int:
    ax, ay = ord(a[0]) - 65, int(a[1]) - 1
    bx, by = ord(b[0]) - 65, int(b[1]) - 1
    return abs(ax - bx) + abs(ay - by)


def distance_in_feet(a: str, b: str) -> int:
    return manhattan_distance(a, b) * 5


def move_toward(a: str, b: str, squares: int) -> str:
    ax, ay = ord(a[0]) - 65, int(a[1]) - 1
    bx, by = ord(b[0]) - 65, int(b[1]) - 1
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
    return f"{chr(ax+65)}{ay+1}"
