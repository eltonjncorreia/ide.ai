"""
ProviderBar — AI provider selector at the bottom.

Displays available AI providers (Claude, Copilot, etc.)
with visual indication of the active provider.

Icon Scheme:
  • Claude: "🤖" — Robot icon represents AI agent
  • Copilot: "⚡" — Lightning icon represents GitHub Copilot's speed
  • Active indicator: "●" (dot) — Shows provider is active
  • Separators: "│" — Divides provider tabs
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Static, Button

from ..ai.base import AIProvider


class ProviderBar(Horizontal):
    """Provider selector bar at the bottom left."""

    BINDINGS = [
        Binding("ctrl+tab", "next_provider", "Next provider", show=False),
        Binding("ctrl+shift+tab", "prev_provider", "Prev provider", show=False),
    ]

    class ProviderSelected(Message):
        """Posted when a provider is selected."""
        def __init__(self, provider: AIProvider) -> None:
            super().__init__()
            self.provider = provider

    DEFAULT_CSS = """
    ProviderBar {
        height: 1;
        background: $panel-lighten-2;
        border-top: solid $panel-lighten-1;
        layout: horizontal;
        padding: 0 1;
    }

    ProviderBar > .provider-tab {
        width: auto;
        padding: 0 2;
        color: $text-muted;
        text-style: none;
        transition: color 200ms, text-style 200ms, background 200ms;
        background: transparent;
    }

    ProviderBar > .provider-tab:hover {
        color: $secondary;
    }

    ProviderBar > .provider-tab.--active {
        color: $accent;
        text-style: bold;
        background: $accent 5%;
    }

    ProviderBar > #spacer {
        width: 1fr;
    }
    """

    def __init__(self, providers: list[AIProvider], **kwargs) -> None:
        super().__init__(**kwargs)
        self.providers = providers
        self._active_index = 0
        # Icon mapping for providers
        self._provider_icons = {
            "claude": "🤖",
            "copilot": "⚡",
        }

    def compose(self) -> ComposeResult:
        """Compose provider tabs."""
        for i, provider in enumerate(self.providers):
            is_active = i == self._active_index
            classes = "provider-tab --active" if is_active else "provider-tab"
            
            # Get icon for provider
            icon = self._provider_icons.get(provider.name.lower(), "●")
            
            yield Button(
                f"{icon} {provider.name}",
                id=f"provider-{i}",
                classes=classes,
            )

        # Spacer
        yield Static("", id="spacer")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle provider button press."""
        button_id = event.button.id or ""
        if button_id.startswith("provider-"):
            index = int(button_id.split("-")[1])
            self._select_provider(index)

    def _select_provider(self, index: int) -> None:
        """Select a provider by index."""
        if 0 <= index < len(self.providers):
            # Clear active class from all
            for btn in self.query(".provider-tab"):
                btn.remove_class("--active")

            # Set active class on selected
            selected_btn = self.query_one(f"#provider-{index}", Button)
            selected_btn.add_class("--active")

            # Update internal state
            self._active_index = index

            # Post message
            self.post_message(self.ProviderSelected(self.providers[index]))

    def action_next_provider(self) -> None:
        """Switch to next provider."""
        next_index = (self._active_index + 1) % len(self.providers)
        self._select_provider(next_index)

    def action_prev_provider(self) -> None:
        """Switch to previous provider."""
        prev_index = (self._active_index - 1) % len(self.providers)
        self._select_provider(prev_index)

    @property
    def active_provider(self) -> AIProvider:
        """Get the currently active provider."""
        return self.providers[self._active_index]

    @property
    def active_provider_index(self) -> int:
        """Get the currently active provider index."""
        return self._active_index
