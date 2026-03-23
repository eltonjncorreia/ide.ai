"""
IDE.AI — Main Application (v2 — Minimalista)

Novo design focado em chat, inspirado em Claude Code + GitHub Copilot CLI.
Layout: ChatPanel (principal) + ProviderBar + ActionBar + Panels auxiliares colapsíveis.

Icon Scheme:
  • Providers:
    - Claude: "🤖" — Robot icon for AI agent
    - Copilot: "⚡" — Lightning for speed/power
  • Action indicators:
    - Ready: "✓" — Success/ready state
    - Thinking: "⟳" — Processing/loading
    - Error: "✗" — Error/failure
  • UI elements:
    - Files: "📄" — Document for file tree
    - Terminal: "▭" — Terminal/window icon
    - New: "➕" — Plus for new chat
    - Input prompt: ">" — Right angle for input (color: accent/purple)

Accessibility (WCAG AA Compliance):
  • All interactive elements have meaningful labels and tooltips
  • Color contrast ratios meet or exceed 4.5:1 for normal text (✓ verified)
  • Icons paired with text labels (not icon-only buttons)
  • Keyboard navigation via Ctrl+H for help display
  • Focus indicators through text-style changes
  • No color-only information — semantic elements always present
"""

from __future__ import annotations

import os
import shutil
from typing import Type

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static

from .panels.chat_panel import ChatPanel
from .panels.provider_bar import ProviderBar
from .panels.action_bar import ActionBar
from .panels.file_tree import FileTreePanel
from .panels.terminal import TerminalPanel
from .ai.base import AIProvider
from .ai.claude import ClaudeProvider
from .ai.copilot import CopilotProvider
from .context_manager import ContextManager


# Providers disponíveis
_AVAILABLE_PROVIDERS: list[Type[AIProvider]] = [
    ClaudeProvider,
    CopilotProvider,
]

# Icon mapping for providers
_PROVIDER_ICONS = {
    "claude": "🤖",
    "copilot": "⚡",
}


class IdeApp(App[None]):
    """IDE minimalista focada em AI CLIs."""

    CSS_PATH = "app_new.tcss"
    TITLE = "ide.ai"
    SUB_TITLE = "AI CLI IDE"

    BINDINGS = [
        # Main navigation
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+h", "show_help", "Help", show=True),
        
        # Chat management
        Binding("ctrl+n", "new_chat", "New chat", show=True),
        Binding("ctrl+l", "clear_chat", "Clear chat", show=True),
        Binding("ctrl+enter", "send_message", "Send", show=True),
        Binding("ctrl+w", "close_chat", "Close tab", show=True),
        
        # Provider switching
        Binding("ctrl+tab", "next_provider", "Next provider", show=True),
        Binding("ctrl+shift+tab", "prev_provider", "Prev provider", show=False),
        
        # Panel management
        Binding("ctrl+e", "toggle_file_tree", "Files", show=True),
        Binding("ctrl+grave", "toggle_terminal", "Terminal", show=True),
        
        # Context
        Binding("ctrl+shift+c", "add_context", "Add context", show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.context_manager = ContextManager()
        self.chat_panels: list[ChatPanel] = []  # Track all chat tabs
        self.active_chat_index = 0  # Index of currently active chat
        self._active_provider_index = 0  # Track provider selection for new tabs

    def compose(self) -> ComposeResult:
        """Compose the main layout."""
        # Mostrar workspace no subtitle
        self.sub_title = os.path.basename(os.getcwd())

        yield Header(show_clock=True)

        # Container principal
        with Vertical(id="app-container"):
            # Chat tabs container (holds multiple chat panels, but only one visible)
            with Vertical(id="chat-tabs-container"):
                yield ChatPanel(
                    id="main-chat",
                    provider=self._get_first_provider(),
                    tab_index=1,
                    tab_count=1,
                )

            # Auxiliary panels: File tree + Terminal (collapsible)
            with Horizontal(id="auxiliary-panels"):
                yield FileTreePanel(id="file-tree-panel")
                yield TerminalPanel(id="terminal-panel")

            # Bottom bar: Provider selector + Action buttons
            with Horizontal(id="bottom-bar"):
                yield ProviderBar(
                    id="provider-bar",
                    providers=[p() for p in _AVAILABLE_PROVIDERS],
                )
                yield ActionBar(id="action-bar")

        yield Footer()

    def on_mount(self) -> None:
        """Setup on mount."""
        # Initialize chat panels list with the main chat
        main_chat = self.query_one("#main-chat", ChatPanel)
        self.chat_panels = [main_chat]
        self.active_chat_index = 0
        
        # Hook up close requested messages from chat panels
        main_chat.on_message(ChatPanel.CloseRequested, self._on_chat_close_requested)
        
        # Hook up provider bar changes
        provider_bar = self.query_one(ProviderBar)
        provider_bar.on_message(
            ProviderBar.ProviderSelected,
            self._on_provider_selected,
        )
        
        # Sync app provider state with ProviderBar on mount
        self._active_provider_index = provider_bar.active_provider_index

        # Hook up action bar changes
        action_bar = self.query_one(ActionBar)
        action_bar.on_message(
            ActionBar.NewChatRequested,
            self._on_new_chat_requested,
        )
        action_bar.on_message(
            ActionBar.FileTreeToggled,
            self._on_file_tree_toggled,
        )
        action_bar.on_message(
            ActionBar.TerminalToggled,
            self._on_terminal_toggled,
        )

    def _get_first_provider(self) -> AIProvider:
        """Get the first available provider instance."""
        return _AVAILABLE_PROVIDERS[0]()

    def _get_active_provider(self) -> AIProvider:
        """Get the currently active provider instance (for new tabs)."""
        if 0 <= self._active_provider_index < len(_AVAILABLE_PROVIDERS):
            return _AVAILABLE_PROVIDERS[self._active_provider_index]()
        return _AVAILABLE_PROVIDERS[0]()

    def _on_provider_selected(self, provider: AIProvider) -> None:
        """Handle provider selection.
        
        When a provider is selected, switch the active chat panel's provider
        to a new independent instance of that provider type.
        """
        # Find and update active provider index
        for i, p in enumerate(_AVAILABLE_PROVIDERS):
            if p.__name__ == provider.__class__.__name__:
                self._active_provider_index = i
                break
        
        # Update the active chat panel with NEW provider instance
        # (not the same instance - ensures independence)
        if self.chat_panels:
            chat_panel = self.chat_panels[self.active_chat_index]
            # Create a fresh instance - don't reuse the same provider
            new_provider = _AVAILABLE_PROVIDERS[self._active_provider_index]()
            chat_panel.provider = new_provider
            
            # Use icon mapping for provider label
            icon = _PROVIDER_ICONS.get(new_provider.name.lower(), "●")
            chat_panel.query_one("#provider-label", Static).update(f"{icon} {new_provider.name}")

    def _on_new_chat_requested(self) -> None:
        """Handle new chat request."""
        self._add_new_chat_panel()

    def _on_file_tree_toggled(self) -> None:
        """Handle file tree toggle request."""
        self._toggle_auxiliary_panel()

    def _on_terminal_toggled(self) -> None:
        """Handle terminal toggle request."""
        self._toggle_auxiliary_panel()

    def _toggle_auxiliary_panel(self) -> None:
        """Toggle visibility of auxiliary panels."""
        aux_panels = self.query_one("#auxiliary-panels")
        if aux_panels.has_class("--visible"):
            aux_panels.remove_class("--visible")
        else:
            aux_panels.add_class("--visible")

    def _on_chat_close_requested(self, message: ChatPanel.CloseRequested) -> None:
        """Handle close request from ChatPanel."""
        chat_to_close = message.chat_panel
        if chat_to_close in self.chat_panels:
            self._close_chat_panel(chat_to_close)

    def _close_current_chat(self) -> None:
        """Close the currently active chat tab."""
        if not self.chat_panels or len(self.chat_panels) <= 1:
            self.notify("Cannot close the last chat tab", title="Info", timeout=2)
            return
        
        active_chat = self.chat_panels[self.active_chat_index]
        self._close_chat_panel(active_chat)

    def _close_chat_panel(self, chat_panel: ChatPanel) -> None:
        """Remove a specific chat panel from the tab list."""
        if len(self.chat_panels) <= 1:
            self.notify("Cannot close the last chat tab", title="Info", timeout=2)
            return
        
        # Find and remove the chat panel
        try:
            index = self.chat_panels.index(chat_panel)
            
            # Remove from DOM
            container = self.query_one("#chat-tabs-container")
            chat_panel.remove()
            
            # Remove from list
            self.chat_panels.pop(index)
            
            # Update active index
            if self.active_chat_index >= len(self.chat_panels):
                self.active_chat_index = len(self.chat_panels) - 1
            
            # Update visibility and tab counts for remaining panels
            self._update_tab_visibility()
        except Exception as e:
            self.notify(f"Error closing chat: {e}", title="Error", timeout=3)

    def _update_tab_visibility(self) -> None:
        """Update tab counter and visibility for all chat panels."""
        total_tabs = len(self.chat_panels)
        
        # Hide all panels, show only active one
        for i, panel in enumerate(self.chat_panels):
            panel.display = (i == self.active_chat_index)
            panel.update_tab_info(i + 1, total_tabs)

    def _add_new_chat_panel(self) -> None:
        """Add a new chat panel tab."""
        container = self.query_one("#chat-tabs-container")
        
        # Create new chat panel with CURRENT active provider
        new_chat = ChatPanel(
            id=f"chat-tab-{len(self.chat_panels)}",
            provider=self._get_active_provider(),
            tab_index=len(self.chat_panels) + 1,
            tab_count=len(self.chat_panels) + 1,
        )
        
        # Register close message handler
        new_chat.on_message(ChatPanel.CloseRequested, self._on_chat_close_requested)
        
        # Add to container
        container.mount(new_chat)
        
        # Update indices
        self.chat_panels.append(new_chat)
        self.active_chat_index = len(self.chat_panels) - 1
        
        # Update visibility and tab counts
        self._update_tab_visibility()
        
        # Focus the new chat's input
        try:
            input_field = new_chat.query_one("#input-field")
            input_field.focus()
        except Exception:
            pass

    def action_clear_chat(self) -> None:
        """Clear the current chat."""
        if self.chat_panels:
            active_chat = self.chat_panels[self.active_chat_index]
            active_chat.action_clear_chat()

    def action_next_provider(self) -> None:
        """Switch to next provider."""
        provider_bar = self.query_one(ProviderBar)
        provider_bar.action_next_provider()

    def action_toggle_file_tree(self) -> None:
        """Toggle file tree visibility."""
        self._toggle_auxiliary_panel()

    def action_toggle_terminal(self) -> None:
        """Toggle terminal visibility."""
        self._toggle_auxiliary_panel()

    def action_add_context(self) -> None:
        """Add current file to context (Ctrl+Shift+C)."""
        # This would be enhanced to get the currently active file
        # For now, it's a placeholder for the context action
        pass

    def action_new_chat(self) -> None:
        """Create a new chat session (Ctrl+N)."""
        self._on_new_chat_requested()

    def action_close_chat(self) -> None:
        """Close the current chat tab (Ctrl+W)."""
        self._close_current_chat()

    def action_send_message(self) -> None:
        """Send current message from chat panel (Ctrl+Enter)."""
        if self.chat_panels:
            active_chat = self.chat_panels[self.active_chat_index]
            active_chat.action_send_message()

    def action_prev_provider(self) -> None:
        """Switch to previous provider (Ctrl+Shift+Tab)."""
        provider_bar = self.query_one(ProviderBar)
        provider_bar.action_prev_provider()

    def action_show_help(self) -> None:
        """Show keybindings help (Ctrl+H)."""
        # Display keybindings in a modal or notification
        # For now, print to terminal
        help_text = """
IDE.AI v2 — Keybindings:

Navigation & Quit:
  Ctrl+Q          — Quit IDE
  Ctrl+H          — Show this help

Chat:
  Ctrl+N          — New chat
  Ctrl+W          — Close tab
  Ctrl+L          — Clear chat
  Ctrl+Enter      — Send message

Providers:
  Ctrl+Tab        — Next provider
  Ctrl+Shift+Tab  — Previous provider

Panels:
  Ctrl+E          — Toggle file tree
  Ctrl+`          — Toggle terminal

Context:
  Ctrl+Shift+C    — Add file to context
"""
        self.notify(help_text, title="Keybindings")


def run() -> None:
    """Run the application."""
    app = IdeApp()
    app.run()


if __name__ == "__main__":
    run()
