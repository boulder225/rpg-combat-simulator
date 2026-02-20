"""Tests for LLM move validator."""

import pytest
from src.agents.llm_validator import validate_move, to_agent_action
from src.agents.llm_parser import LLMResponse
from src.agents.base import AgentAction
from src.domain.creature import Creature, Action, Attack, DamageRoll, AbilityScores
from src.domain.combat_state import CombatState


class TestLLMValidator:
    """Test move legality validation against CombatState."""

    @pytest.fixture
    def basic_state(self):
        """Create minimal CombatState with attacker at E5 and target at D4."""
        # Create scimitar attack
        scimitar = Attack(
            name="Scimitar",
            attack_bonus=4,
            damage=DamageRoll(dice="1d6+2", damage_type="slashing"),
            reach=5
        )

        # Create attacker (goblin at E5)
        attacker = Creature(
            name="Goblin",
            ac=15,
            hp_max=7,
            current_hp=7,
            speed=30,
            team="enemies",
            position="E5",
            creature_id="goblin_0",
            ability_scores=AbilityScores(dex=14),
            actions=[Action(name="Scimitar", attacks=[scimitar])]
        )

        # Create target (fighter at E4 - 5ft away)
        fighter = Creature(
            name="Fighter",
            ac=18,
            hp_max=12,
            current_hp=12,
            speed=30,
            team="party",
            position="E4",
            creature_id="fighter_0",
            ability_scores=AbilityScores()
        )

        creatures = {
            "goblin_0": attacker,
            "fighter_0": fighter
        }

        return CombatState(
            creatures=creatures,
            initiative_order=["goblin_0", "fighter_0"],
            current_turn=0,
            round=1
        )

    def test_valid_melee_attack_in_range(self, basic_state):
        """Valid melee attack on adjacent target should pass."""
        response = LLMResponse(
            thinking="Fighter is adjacent, I'll attack.",
            action="Attack with Scimitar",
            target="Fighter (E4)"
        )

        valid, error = validate_move(response, basic_state, "goblin_0")

        assert valid is True
        assert error == ""

    def test_target_does_not_exist(self, basic_state):
        """Target not in state.creatures should fail."""
        response = LLMResponse(
            thinking="Attack the wizard.",
            action="Attack with Scimitar",
            target="Wizard (C3)"
        )

        valid, error = validate_move(response, basic_state, "goblin_0")

        assert valid is False
        assert "does not exist" in error.lower()

    def test_target_is_dead(self, basic_state):
        """Attack on dead target (0 HP) should fail."""
        # Update fighter to be dead
        dead_state = basic_state.update_creature("fighter_0", current_hp=0)

        response = LLMResponse(
            thinking="Attack the fighter.",
            action="Attack with Scimitar",
            target="Fighter (D4)"
        )

        valid, error = validate_move(response, dead_state, "goblin_0")

        assert valid is False
        assert "already dead" in error.lower()

    def test_movement_exceeds_speed(self, basic_state):
        """Movement beyond speed should fail."""
        response = LLMResponse(
            thinking="Move far away.",
            action="Dodge",
            movement="Z20"  # Way beyond 30ft speed
        )

        valid, error = validate_move(response, basic_state, "goblin_0")

        assert valid is False
        assert "exceeds speed" in error.lower()

    def test_attack_out_of_range(self, basic_state):
        """Melee attack on distant target without movement should fail."""
        # Create distant wizard at A1 (more than 5ft away)
        wizard = Creature(
            name="Wizard",
            ac=12,
            hp_max=8,
            current_hp=8,
            speed=30,
            team="party",
            position="A1",
            creature_id="wizard_0",
            ability_scores=AbilityScores()
        )

        # Create new state with wizard added
        distant_creatures = dict(basic_state.creatures)
        distant_creatures["wizard_0"] = wizard
        distant_state = CombatState(
            creatures=distant_creatures,
            initiative_order=basic_state.initiative_order + ["wizard_0"],
            current_turn=0,
            round=1
        )
        distant_creatures = dict(distant_state.creatures)
        distant_creatures["wizard_0"] = wizard
        distant_state = CombatState(
            creatures=distant_creatures,
            initiative_order=distant_state.initiative_order + ["wizard_0"],
            current_turn=0,
            round=1
        )

        response = LLMResponse(
            thinking="Attack the wizard.",
            action="Attack with Scimitar",
            target="Wizard (A1)"  # Too far for reach 5ft
        )

        valid, error = validate_move(response, distant_state, "goblin_0")

        assert valid is False
        assert "out of range" in error.lower()

    def test_attack_with_movement_into_range(self, basic_state):
        """Attack on distant target WITH movement into range should pass."""
        # Create distant wizard at C5 (10ft from goblin at E5)
        wizard = Creature(
            name="Wizard",
            ac=12,
            hp_max=8,
            current_hp=8,
            speed=30,
            team="party",
            position="C5",
            creature_id="wizard_0",
            ability_scores=AbilityScores()
        )

        distant_creatures = dict(basic_state.creatures)
        distant_creatures["wizard_0"] = wizard
        distant_state = CombatState(
            creatures=distant_creatures,
            initiative_order=basic_state.initiative_order + ["wizard_0"],
            current_turn=0,
            round=1
        )

        response = LLMResponse(
            thinking="Move to wizard and attack.",
            action="Attack with Scimitar",
            target="Wizard (C5)",
            movement="D5"  # Move to D5 (5ft from C5, within reach)
        )

        valid, error = validate_move(response, distant_state, "goblin_0")

        assert valid is True
        assert error == ""

    def test_valid_dodge_action(self, basic_state):
        """Dodge action requires no target and should pass."""
        response = LLMResponse(
            thinking="No good targets, dodge.",
            action="Dodge"
        )

        valid, error = validate_move(response, basic_state, "goblin_0")

        assert valid is True
        assert error == ""

    def test_attack_action_missing_target(self, basic_state):
        """Attack action without target should fail."""
        response = LLMResponse(
            thinking="Attack!",
            action="Attack with Scimitar"
            # Missing target field
        )

        valid, error = validate_move(response, basic_state, "goblin_0")

        assert valid is False
        assert "requires a target" in error.lower()

    def test_to_agent_action_conversion(self, basic_state):
        """Valid response should convert to AgentAction correctly."""
        response = LLMResponse(
            thinking="Attack the fighter.",
            action="Attack with Scimitar",
            target="Fighter (E4)"
        )

        action = to_agent_action(response, basic_state, "goblin_0")

        assert isinstance(action, AgentAction)
        assert action.action_type == "attack"
        assert action.attack_name == "Scimitar"
        assert action.target_id == "fighter_0"
        assert action.move_to is None

    def test_to_agent_action_with_movement(self, basic_state):
        """Response with movement should populate move_to field."""
        response = LLMResponse(
            thinking="Move and attack.",
            action="Attack with Scimitar",
            target="Fighter (E4)",
            movement="E4"
        )

        action = to_agent_action(response, basic_state, "goblin_0")

        assert action.action_type == "move_and_attack"
        assert action.attack_name == "Scimitar"
        assert action.target_id == "fighter_0"
        assert action.move_to == "E4"

    def test_to_agent_action_dodge(self, basic_state):
        """Dodge action should convert to dodge action_type."""
        response = LLMResponse(
            thinking="Dodge.",
            action="Dodge"
        )

        action = to_agent_action(response, basic_state, "goblin_0")

        assert action.action_type == "dodge"
        assert action.attack_name is None
        assert action.target_id is None

    def test_to_agent_action_invalid_move_raises_error(self, basic_state):
        """Invalid move should raise ValueError from to_agent_action."""
        response = LLMResponse(
            thinking="Attack non-existent target.",
            action="Attack with Scimitar",
            target="Dragon (Z99)"
        )

        with pytest.raises(ValueError):
            to_agent_action(response, basic_state, "goblin_0")

    def test_movement_parsing_from_x_to_y(self, basic_state):
        """Parse 'from E5 to D5' format."""
        response = LLMResponse(
            thinking="Move closer.",
            action="Dodge",
            movement="from E5 to D5"
        )

        valid, error = validate_move(response, basic_state, "goblin_0")

        assert valid is True  # 5ft movement within speed
        assert error == ""

    def test_movement_parsing_bare_position(self, basic_state):
        """Parse bare position like 'D5'."""
        response = LLMResponse(
            thinking="Move.",
            action="Dodge",
            movement="D5"
        )

        valid, error = validate_move(response, basic_state, "goblin_0")

        assert valid is True
        assert error == ""

    def test_target_name_resolution_with_position(self, basic_state):
        """Target 'Fighter (E4)' should resolve to 'fighter_0'."""
        response = LLMResponse(
            thinking="Attack.",
            action="Attack with Scimitar",
            target="Fighter (E4)"
        )

        valid, error = validate_move(response, basic_state, "goblin_0")

        assert valid is True
        # Verify it resolves correctly by checking conversion
        action = to_agent_action(response, basic_state, "goblin_0")
        assert action.target_id == "fighter_0"

    def test_target_name_resolution_case_insensitive(self, basic_state):
        """Target matching should be case-insensitive."""
        response = LLMResponse(
            thinking="Attack.",
            action="Attack with Scimitar",
            target="fighter"  # lowercase
        )

        valid, error = validate_move(response, basic_state, "goblin_0")

        assert valid is True
        action = to_agent_action(response, basic_state, "goblin_0")
        assert action.target_id == "fighter_0"

    def test_action_name_fuzzy_matching_multiattack(self, basic_state):
        """Action text containing 'multiattack' should match Multiattack action."""
        # Add multiattack to goblin
        scimitar1 = Attack(
            name="Scimitar",
            attack_bonus=4,
            damage=DamageRoll(dice="1d6+2", damage_type="slashing"),
            reach=5
        )
        scimitar2 = Attack(
            name="Scimitar",
            attack_bonus=4,
            damage=DamageRoll(dice="1d6+2", damage_type="slashing"),
            reach=5
        )
        multiattack_action = Action(
            name="Multiattack",
            description="Two scimitar attacks",
            attacks=[scimitar1, scimitar2]
        )

        goblin = basic_state.creatures["goblin_0"]
        updated_goblin = goblin.model_copy(update={"actions": [multiattack_action]})
        multiattack_state = basic_state.update_creature("goblin_0", actions=[multiattack_action])

        response = LLMResponse(
            thinking="Use multiattack.",
            action="Multiattack with Scimitar",
            target="Fighter (E4)"
        )

        valid, error = validate_move(response, multiattack_state, "goblin_0")

        assert valid is True
        action = to_agent_action(response, multiattack_state, "goblin_0")
        assert action.attack_name == "Multiattack"
