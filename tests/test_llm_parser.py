"""Tests for LLM output parser."""

import pytest
from src.agents.llm_parser import parse_llm_output, LLMResponse


class TestLLMParser:
    """Test LLM output parsing with clean, malformed, and edge case inputs."""

    def test_clean_output_parsing(self):
        """Parse well-formed LLM response with all fields."""
        llm_text = """<thinking>Fighter is nearby at D4, 15ft away. I should close distance and attack with my scimitars.</thinking>
ACTION: Multiattack with Scimitar
TARGET: Fighter (D4)
MOVEMENT: from E5 to D5
BONUS: Hide
REACTION: Opportunity attack on anyone leaving reach"""

        response = parse_llm_output(llm_text)

        assert response.thinking == "Fighter is nearby at D4, 15ft away. I should close distance and attack with my scimitars."
        assert response.action == "Multiattack with Scimitar"
        assert response.target == "Fighter (D4)"
        assert response.movement == "from E5 to D5"
        assert response.bonus == "Hide"
        assert response.reaction == "Opportunity attack on anyone leaving reach"

    def test_missing_optional_fields(self):
        """Parse response with only ACTION (no TARGET, MOVEMENT, BONUS, REACTION)."""
        llm_text = """<thinking>No enemies in range, I should dodge.</thinking>
ACTION: Dodge"""

        response = parse_llm_output(llm_text)

        assert response.thinking == "No enemies in range, I should dodge."
        assert response.action == "Dodge"
        assert response.target is None
        assert response.movement is None
        assert response.bonus is None
        assert response.reaction is None

    def test_malformed_thinking_tag(self):
        """Handle missing closing tag or extra whitespace in thinking."""
        llm_text = """<thinking>I need to attack the wizard.

ACTION: Attack with Longsword
TARGET: Wizard (C3)"""

        response = parse_llm_output(llm_text)

        # Should extract thinking content even without closing tag
        assert "I need to attack the wizard." in response.thinking
        assert response.action == "Attack with Longsword"
        assert response.target == "Wizard (C3)"

    def test_extra_preamble_and_markdown_wrapping(self):
        """Ignore preamble and markdown code blocks."""
        llm_text = """Here is my tactical decision:

<thinking>Attack the weakest enemy.</thinking>
ACTION: Attack with Bite
TARGET: Rogue (B2)
MOVEMENT: stay
BONUS: None
REACTION: None"""

        response = parse_llm_output(llm_text)

        assert response.thinking == "Attack the weakest enemy."
        assert response.action == "Attack with Bite"
        assert response.target == "Rogue (B2)"
        # "stay" and "None" should be normalized to None
        assert response.movement is None
        assert response.bonus is None
        assert response.reaction is None

    def test_case_insensitivity(self):
        """Parse keys regardless of case (action:, Action:, ACTION:)."""
        llm_text = """<thinking>Testing case insensitivity.</thinking>
action: Attack with Claw
Target: Wizard (F3)
movement: B2
bonus: Dash
Reaction: None"""

        response = parse_llm_output(llm_text)

        assert response.action == "Attack with Claw"
        assert response.target == "Wizard (F3)"
        assert response.movement == "B2"
        assert response.bonus == "Dash"
        assert response.reaction is None

    def test_null_value_normalization(self):
        """Convert "None", "stay", "N/A", "-", "" to None."""
        llm_text = """<thinking>Testing null values.</thinking>
ACTION: Dodge
TARGET: none
MOVEMENT: stay
BONUS: N/A
REACTION: -"""

        response = parse_llm_output(llm_text)

        assert response.action == "Dodge"
        assert response.target is None
        assert response.movement is None
        assert response.bonus is None
        assert response.reaction is None

    def test_no_thinking_tag(self):
        """Handle LLM output that skips thinking tag entirely."""
        llm_text = """ACTION: Attack with Sword
TARGET: Goblin (A1)"""

        response = parse_llm_output(llm_text)

        # Should have empty thinking
        assert response.thinking == ""
        assert response.action == "Attack with Sword"
        assert response.target == "Goblin (A1)"

    def test_garbage_output_with_no_action(self):
        """Raise error on completely garbage output with no ACTION found."""
        llm_text = """This is just random text with no structure at all.
The LLM completely failed to follow the format."""

        with pytest.raises(ValueError, match="No ACTION found"):
            parse_llm_output(llm_text)

    def test_multiline_thinking_content(self):
        """Handle thinking content with multiple lines and paragraphs."""
        llm_text = """<thinking>
The wizard is at low HP.
I should focus fire on them.
Movement would expose me to attacks of opportunity.
</thinking>
ACTION: Attack with Greatsword
TARGET: Wizard (C3)"""

        response = parse_llm_output(llm_text)

        # Should preserve multiline thinking
        assert "wizard is at low hp" in response.thinking.lower()
        assert "focus fire" in response.thinking.lower()
        assert response.action == "Attack with Greatsword"

    def test_extra_whitespace_handling(self):
        """Handle extra whitespace before/after values."""
        llm_text = """<thinking>  Extra whitespace test.  </thinking>
ACTION:   Dash
TARGET:     Fighter (E5)
MOVEMENT:  D4  """

        response = parse_llm_output(llm_text)

        # Whitespace should be stripped
        assert response.thinking == "Extra whitespace test."
        assert response.action == "Dash"
        assert response.target == "Fighter (E5)"
        assert response.movement == "D4"
