"""
ActionBar — Quick action buttons at the bottom right.

Provides quick access to common actions:
- New chat (Ctrl+N)
- Clear chat (Ctrl+L)
- Toggle file tree (Ctrl+E)
- Toggle terminal (Ctrl+`)

Icon Scheme:
  • Files: "📄" — Document icon for file tree
  • Terminal: "▭" — Terminal/window icon
  • New chat: "➕" — Plus icon for new
  • Other indicators:
    - Ready: "✓" — Checkmark for completed/ready state
    - Thinking: "⟳" — Spinner for processing
    - Error: "✗" — X for error/failure
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Static, Button


class ActionBar(Horizontal):
    """Action buttons bar at the bottom right."""

    BINDINGS = [
        Binding("ctrl+n", "new_chat", "New chat", show=True),
        Binding("ctrl+e", "toggle_file_tree", "Files", show=True),
        Binding("ctrl+grave", "toggle_terminal", "Terminal", show=True),
    ]

    class NewChatRequested(Message):
        """Posted when 'New chat' is requested."""
        pass

    class FileTreeToggled(Message):
        """Posted when file tree toggle is requested."""
        pass

    class TerminalToggled(Message):
        """Posted when terminal toggle is requested."""
        pass

    DEFAULT_CSS = """
    ActionBar {
        height: 1;
        background: $panel-lighten-2;
        border-top: solid $panel-lighten-1;
        layout: horizontal;
        padding: 0 1;
        align: right middle;
    }

    ActionBar > Button {
        width: auto;
        margin-right: 1;
        background: $panel;
        color: $text-muted;
        transition: color 200ms, background 200ms;
    }

    ActionBar > Button:hover {
        background: $secondary 10%;
        color: $secondary;
    }

    ActionBar > Button.--active {
        background: $accent 10%;
        color: $accent;
        text-style: bold;
    }

    ActionBar > #spacer {
        width: 1fr;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._file_tree_visible = False
        self._terminal_visible = False

    def compose(self) -> ComposeResult:
        """Compose action buttons."""
        yield Static("", id="spacer")
        yield Button("📄 Files", id="btn-files", tooltip="Toggle file tree (Ctrl+E)")
        yield Button("⌘ Terminal", id="btn-terminal", tooltip="Toggle terminal (Ctrl+`)")
        yield Button("➕ New", id="btn-new", tooltip="New chat (Ctrl+N)")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        button_id = event.button.id or ""

        if button_id == "btn-new":
            self.post_message(self.NewChatRequested())
        elif button_id == "btn-files":
            self._file_tree_visible = not self._file_tree_visible
            self._update_button_state("btn-files", self._file_tree_visible)
            self.post_message(self.FileTreeToggled())
        elif button_id == "btn-terminal":
            self._terminal_visible = not self._terminal_visible
            self._update_button_state("btn-terminal", self._terminal_visible)
            self.post_message(self.TerminalToggled())

    def _update_button_state(self, button_id: str, active: bool) -> None:
        """Update button visual state (active/inactive)."""
        btn = self.query_one(f"#{button_id}", Button)
        if active:
            btn.add_class("--active")
        else:
            btn.remove_class("--active")

    def action_new_chat(self) -> None:
        """Handle new chat action."""
        self.post_message(self.NewChatRequested())

    def action_toggle_file_tree(self) -> None:
        """Handle file tree toggle action."""
        self._file_tree_visible = not self._file_tree_visible
        self._update_button_state("btn-files", self._file_tree_visible)
        self.post_message(self.FileTreeToggled())

    def action_toggle_terminal(self) -> None:
        """Handle terminal toggle action."""
        self._terminal_visible = not self._terminal_visible
        self._update_button_state("btn-terminal", self._terminal_visible)
        self.post_message(self.TerminalToggled())
