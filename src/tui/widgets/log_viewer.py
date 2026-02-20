"""Scrollable combat log viewer widget for the last simulation run."""

from textual.widgets import RichLog


class CombatLogViewer(RichLog):
    """Displays the combat log for the last run with scrolling."""

    def set_content(self, log_text: str) -> None:
        """Replace current content with the provided log text."""
        self.clear()
        if not log_text:
            return
        for line in log_text.splitlines():
            self.write(line)

