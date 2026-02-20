def test_simulator_runs():
    assert True


def test_opportunity_attack_on_leave_reach():
    """When a creature moves from adjacent to an enemy to out of reach, that enemy gets an opportunity attack."""
    from pathlib import Path
    from src.io.markdown import load_creature
    from src.simulation.simulator import _resolve_opportunity_attacks
    from src.domain.combat_state import CombatState
    from src.io.logger import CombatLogger

    data_dir = Path(__file__).resolve().parent.parent / "data" / "creatures"
    _, fighter = load_creature(data_dir / "fighter.md")
    _, goblin = load_creature(data_dir / "goblin.md")
    fighter = fighter.model_copy(update={"creature_id": "fighter_0", "position": "A1"})
    goblin = goblin.model_copy(update={"creature_id": "goblin_0", "position": "B1"})

    creatures = {"fighter_0": fighter, "goblin_0": goblin}
    initiative_order = ["fighter_0", "goblin_0"]
    state = CombatState(creatures=creatures, initiative_order=initiative_order)
    logger = CombatLogger(verbose=False)

    # Goblin moves from B1 (adjacent to Fighter at A1) to B3 (out of 5 ft reach) -> Fighter gets OA
    new_state = _resolve_opportunity_attacks(state, "goblin_0", "B1", "B3", None, logger)

    assert "fighter_0" in new_state.reaction_used
    assert "opportunity attack" in logger.get_full_log()


def test_aoe_fireball_resolves_damage_in_radius():
    """Fireball AoE damages all creatures within radius (Manhattan)."""
    from pathlib import Path
    from unittest.mock import patch
    from src.io.markdown import load_creature
    from src.simulation.simulator import _resolve_aoe
    from src.domain.combat_state import CombatState
    from src.io.logger import CombatLogger

    data_dir = Path(__file__).resolve().parent.parent / "data" / "creatures"
    _, wizard = load_creature(data_dir / "wizard.md")
    _, goblin = load_creature(data_dir / "goblin.md")
    wizard = wizard.model_copy(update={"creature_id": "wizard_0", "position": "A1"})
    g1 = goblin.model_copy(update={"creature_id": "goblin_1", "position": "C2"})
    g2 = goblin.model_copy(update={"creature_id": "goblin_2", "position": "D4"})
    g3 = goblin.model_copy(update={"creature_id": "goblin_3", "position": "F5"})
    creatures = {"wizard_0": wizard, "goblin_1": g1, "goblin_2": g2, "goblin_3": g3}
    state = CombatState(creatures=creatures, initiative_order=["wizard_0", "goblin_1", "goblin_2", "goblin_3"])
    action = next(a for a in wizard.actions if a.name == "Fireball")
    logger = CombatLogger(verbose=False)

    with patch("src.simulation.simulator.rules.roll_damage_for_attack", return_value=24), patch(
        "src.simulation.simulator.rules.make_saving_throw"
    ) as mock_save:
        mock_save.return_value = type("R", (), {"is_success": False})()
        new_state = _resolve_aoe(state, "wizard_0", action, "C3", None, logger)

    # C2 and D4 are within Manhattan 4 of C3; F5 is 3+2=5 so out
    assert new_state.creatures["goblin_1"].current_hp == max(0, 7 - 24)
    assert new_state.creatures["goblin_2"].current_hp == max(0, 7 - 24)
    assert new_state.creatures["goblin_3"].current_hp == 7
    assert "Fireball" in logger.get_full_log()
