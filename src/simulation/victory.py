def is_combat_over(state) -> bool:
    teams = {}
    for c in state.creatures.values():
        teams.setdefault(c.team, []).append(c)
    for members in teams.values():
        if all(m.current_hp <= 0 for m in members):
            return True
    return False


def get_winner(state):
    teams = {}
    for c in state.creatures.values():
        teams.setdefault(c.team, []).append(c)
    alive = [team for team, members in teams.items() if any(m.current_hp > 0 for m in members)]
    if len(alive) == 1:
        return alive[0]
    return None
