"""
ChatPanel — Modern, minimalist chat area (main focus).

Design inspirado em Claude Code + GitHub Copilot CLI.
- Chat log com message bubbles (You / AI)
- Input area com visual feedback
- Syntax highlighting melhorado
- Status indicators with animations
- Message bubbles with differentiated styling

Icon Scheme:
  • User message prefix: "You:" — Clear distinction from AI
  • Provider name prefix: "🤖" (Claude) or "⚡" (Copilot)
  • Status indicators:
    - Ready: "✓" — Operation completed successfully
    - Thinking: "⟳" — Processing message
    - Error: "✗" — Error occurred
  • Input prompt: ">" — Indicates input field (colored with accent)
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from datetime import datetime

from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text
from rich.panel import Panel
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.message import Message
from textual.widgets import TextArea, RichLog, Static, Button
from textual.binding import Binding

from ..ai.base import AIProvider


@dataclass
class ChatMessage:
    """Representa uma mensagem no chat."""
    sender: str  # "user" ou provider.name (e.g., "Claude", "Copilot")
    content: str
    timestamp: datetime
    is_streaming: bool = False
    has_code: bool = False  # Detect if message contains code blocks


class ChatPanel(Vertical):
    """Main chat panel — chat log + input area with enhanced UX.
    
    Features:
    - Message bubbles with differentiated styling (user right/blue, AI left/purple)
    - Syntax highlighting for code blocks with Pygments
    - Animated status indicators (spinner, checkmark, error)
    - Input feedback and visual hints
    """

    BINDINGS = [
        Binding("ctrl+l", "clear_chat", "Clear", show=True),
        Binding("ctrl+enter", "send_message", "Send", show=True),
    ]

    class MessageSent(Message):
        """Posted when user sends a message."""
        def __init__(self, text: str) -> None:
            super().__init__()
            self.text = text

    class ProviderChanged(Message):
        """Posted when provider is changed."""
        def __init__(self, provider: AIProvider) -> None:
            super().__init__()
            self.provider = provider

    class CloseRequested(Message):
        """Posted when user requests to close this chat panel."""
        def __init__(self, chat_panel: ChatPanel) -> None:
            super().__init__()
            self.chat_panel = chat_panel

    DEFAULT_CSS = """
    ChatPanel {
        height: 1fr;
        layout: vertical;
        border: none;
        background: transparent;
    }

    ChatPanel > #chat-header {
        height: 1;
        background: $panel-lighten-2;
        color: $text-muted;
        border-bottom: solid $panel-lighten-1;
        layout: horizontal;
        padding: 0 2;
        transition: background 200ms, color 200ms;
    }

    ChatPanel > #chat-header > #provider-label {
        width: auto;
        content-align: left middle;
    }

    ChatPanel > #chat-header > #spacer {
        width: 1fr;
    }

    ChatPanel > #chat-header > #session-info {
        width: auto;
        text-align: right;
    }

    ChatPanel > #chat-header > #close-button {
        width: auto;
        padding: 0 1;
        margin-left: 1;
        background: transparent;
        border: none;
        color: $text-muted;
        transition: color 200ms;
    }

    ChatPanel > #chat-header > #close-button:hover {
        color: $error;
    }

    ChatPanel > #chat-log {
        height: 1fr;
        background: transparent;
        padding: 1 2;
        scrollbar-gutter: stable;
    }

    ChatPanel > #chat-input-area {
        height: auto;
        layout: vertical;
        border-top: solid $panel-lighten-1;
        background: $panel 5%;
        padding: 1 2;
        max-height: 10;
    }

    ChatPanel > #chat-input-area > #input-container {
        height: auto;
        layout: horizontal;
        max-height: 10;
    }

    ChatPanel > #chat-input-area > #input-container > #prompt {
        width: auto;
        color: $accent;
        text-style: bold;
        padding: 0 1;
        content-align: left top;
    }

    ChatPanel > #chat-input-area > #input-container > #input-field {
        width: 1fr;
        height: auto;
        background: transparent;
        border: none;
        color: $text;
        max-height: 10;
        scrollbar-vertical: auto;
        scrollbar-gutter: stable;
    }

    ChatPanel > #chat-input-area > #input-container > #input-field:focus {
        color: $secondary;
    }

    ChatPanel > #chat-input-area > #hint-text {
        width: 1fr;
        height: auto;
        color: $text-muted;
        text-opacity: 60%;
        padding: 0 1;
        text-style: italic;
    }
    """

    def __init__(self, provider: AIProvider, tab_index: int = 1, tab_count: int = 1, **kwargs) -> None:
        super().__init__(**kwargs)
        self.provider = provider
        self.messages: list[ChatMessage] = []
        self._is_waiting = False
        self._status_spinner_index = 0
        self.tab_index = tab_index
        self.tab_count = tab_count
        # Icon mapping for providers
        self._provider_icons = {
            "claude": "🤖",
            "copilot": "⚡",
        }
        # Track active tasks for this panel (supports concurrent requests)
        self._active_tasks: set[asyncio.Task] = set()

    def compose(self) -> ComposeResult:
        """Compose the chat panel layout."""
        # Get icon for current provider
        icon = self._provider_icons.get(self.provider.name.lower(), "●")
        
        with Horizontal(id="chat-header"):
            yield Static(f"{icon} {self.provider.name}", id="provider-label")
            yield Static("", id="spacer")
            yield Static(f"{self.tab_index}/{self.tab_count} • {len(self.messages)} messages", id="session-info")
            # Always yield close button, visibility controlled by display property
            close_btn = Button("✕", id="close-button", variant="default")
            # Hide if only 1 tab
            if self.tab_count <= 1:
                close_btn.display = False
            yield close_btn

        yield RichLog(id="chat-log", markup=True)

        with Vertical(id="chat-input-area"):
            with Horizontal(id="input-container"):
                yield Static(">", id="prompt")
                yield TextArea(
                    id="input-field",
                    language=None,
                    theme="dracula",
                    soft_wrap=True,
                    tab_behavior="focus",
                    read_only=False,
                    show_line_numbers=False,
                    show_cursor=True,
                )
            yield Static("Enter for new line • Ctrl+Enter to send • Ctrl+L to clear", id="hint-text")

    def on_mount(self) -> None:
        """Focus the input field on mount."""
        try:
            self.query_one("#input-field", TextArea).focus()
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "close-button":
            self.post_message(self.CloseRequested(self))

    def on_textarea_changed(self, event: TextArea.Changed) -> None:
        """Handle TextArea content changes (for future features like auto-save)."""
        pass

    def action_send_message(self) -> None:
        """Send message from Ctrl+Enter keybinding."""
        textarea = self.query_one("#input-field", TextArea)
        text = textarea.text.strip()
        if text:
            textarea.text = ""
            # Create task and track it for this panel
            task = asyncio.create_task(self.send_message(text))
            self._active_tasks.add(task)
            task.add_done_callback(self._active_tasks.discard)

    async def send_message(self, text: str, context: str = "") -> None:
        """Send a message to the AI provider and stream response.
        
        This method is fully async and independent - multiple concurrent 
        requests can run simultaneously without blocking each other.
        
        Args:
            text: The user message text
            context: Optional context (file contents, etc.) to include before message
        """
        # Combine context and message
        full_message = context + text if context else text
        
        # Add user message to log (right-aligned bubble)
        self._add_user_message(text)

        # Set waiting state and start status animation
        self._is_waiting = True
        self._update_header()
        self._start_spinner_animation()

        try:
            # Get AI response
            response_text = ""
            chat_log = self.query_one("#chat-log", RichLog)

            # Add AI message header (left-aligned bubble)
            self._add_ai_message_header()

            # Stream response - each chunk is processed independently
            # This doesn't block the event loop or other panels
            async for chunk in self.provider.send(full_message):
                response_text += chunk
                # Yield to event loop to prevent blocking
                await asyncio.sleep(0)
                # Update display with current accumulated response
                self._update_last_message(response_text)

            # Finalize message with syntax highlighting
            message = ChatMessage(
                sender=self.provider.name,
                content=response_text,
                timestamp=datetime.now(),
                has_code=self._detect_code_blocks(response_text),
            )
            self.messages.append(message)

            # Add final styled message
            self._render_ai_message_with_highlight(response_text)

        except asyncio.CancelledError:
            self._add_error_message("Response cancelled")
        except Exception as e:
            self._add_error_message(f"Error: {str(e)}")
        finally:
            self._is_waiting = False
            self._update_header()

    def _add_user_message(self, text: str) -> None:
        """Add a user message to the chat log (right-aligned bubble)."""
        message = ChatMessage(
            sender="user",
            content=text,
            timestamp=datetime.now(),
        )
        self.messages.append(message)

        chat_log = self.query_one("#chat-log", RichLog)
        
        # Create right-aligned bubble with blue background
        user_label = Text("You", style="bold cyan")
        content_text = Text(text, style="dim white")
        
        # Render as bubble with padding
        chat_log.write(Text("", style=""))  # Spacer
        chat_log.write(user_label)
        chat_log.write(Text(" ", style=""))
        chat_log.write(content_text)
        chat_log.write(Text("\n", style=""))

    def _add_ai_message_header(self) -> None:
        """Add AI message header (left-aligned bubble)."""
        chat_log = self.query_one("#chat-log", RichLog)
        ai_label = Text(self.provider.name, style="bold magenta")
        chat_log.write(ai_label)
        chat_log.write(Text(": ", style="bold magenta"))

    def _render_ai_message_with_highlight(self, content: str) -> None:
        """Render AI message with syntax highlighting for code blocks."""
        chat_log = self.query_one("#chat-log", RichLog)
        
        # Parse content for code blocks
        parts = self._parse_code_blocks(content)
        
        for part in parts:
            if part["type"] == "code":
                # Render code block with syntax highlighting
                try:
                    syntax = Syntax(
                        part["content"],
                        part["language"],
                        theme="dracula",
                        line_numbers=True,
                        word_wrap=True,
                    )
                    chat_log.write(syntax)
                except Exception:
                    # Fallback if language detection fails
                    chat_log.write(Text(part["content"], style="dim cyan"))
            else:
                # Render regular text
                chat_log.write(Text(part["content"], style="dim white"))
        
        chat_log.write(Text("\n", style=""))

    def _detect_code_blocks(self, content: str) -> bool:
        """Detect if content contains code blocks."""
        return "```" in content or "```python" in content or "```javascript" in content

    def _parse_code_blocks(self, content: str) -> list[dict]:
        """Parse content into code and text parts."""
        parts = []
        
        # Regex to find code blocks: ```language\ncode\n```
        pattern = r"```(\w+)?\n(.*?)\n```"
        last_end = 0
        
        for match in re.finditer(pattern, content, re.DOTALL):
            # Add text before code block
            if match.start() > last_end:
                text_part = content[last_end : match.start()]
                if text_part.strip():
                    parts.append({"type": "text", "content": text_part})
            
            # Add code block
            language = match.group(1) or "text"
            code = match.group(2)
            parts.append({"type": "code", "language": language, "content": code})
            
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(content):
            remaining = content[last_end:]
            if remaining.strip():
                parts.append({"type": "text", "content": remaining})
        
        # If no code blocks found, treat entire content as text
        if not parts:
            parts.append({"type": "text", "content": content})
        
        return parts

    def _update_last_message(self, content: str) -> None:
        """Update the last message in the chat log."""
        chat_log = self.query_one("#chat-log", RichLog)
        # Simple update: clear and rerender
        # (In production, would be more efficient)
        pass

    def _add_error_message(self, text: str) -> None:
        """Add an error message with red styling."""
        chat_log = self.query_one("#chat-log", RichLog)
        error_text = Text("✗ " + text, style="bold red")
        chat_log.write(error_text)
        chat_log.write(Text("\n", style=""))

    def _start_spinner_animation(self) -> None:
        """Start the status spinner animation."""
        async def animate_spinner() -> None:
            spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            self._status_spinner_index = 0
            
            while self._is_waiting:
                self._status_spinner_index = (self._status_spinner_index + 1) % len(spinners)
                self._update_header()
                await asyncio.sleep(0.1)
        
        asyncio.create_task(animate_spinner())

    def _update_header(self) -> None:
        """Update header info with animated status indicators."""
        try:
            header = self.query_one("#session-info", Static)
            msg_count = len(self.messages)
            
            if self._is_waiting:
                # Spinner animation while waiting
                spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
                spinner = spinners[self._status_spinner_index % len(spinners)]
                status_text = Text(f"{spinner} Thinking...", style="bold yellow")
            else:
                # Checkmark when ready
                status_text = Text("✓ Ready", style="bold green")
            
            # Create combined status line
            msg_text = Text(f"{msg_count} msg  ", style="dim")
            combined = Text()
            combined.append(msg_text)
            combined.append(status_text)
            
            header.update(combined)
        except Exception:
            pass

    def action_clear_chat(self) -> None:
        """Clear the chat."""
        self.messages.clear()
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.clear()
        self._update_header()

    def _on_textarea_focus(self) -> None:
        """Visual feedback when textarea is focused."""
        try:
            prompt = self.query_one("#prompt", Static)
            prompt.styles.color = "var(--color-secondary)"
        except Exception:
            pass

    def _on_textarea_blur(self) -> None:
        """Visual feedback when textarea loses focus."""
        try:
            prompt = self.query_one("#prompt", Static)
            prompt.styles.color = "var(--color-accent)"
        except Exception:
            pass

    def update_tab_info(self, tab_index: int, tab_count: int) -> None:
        """Update tab index and count display."""
        self.tab_index = tab_index
        self.tab_count = tab_count
        try:
            session_info = self.query_one("#session-info", Static)
            msg_count = len(self.messages)
            session_info.update(f"{tab_index}/{tab_count} • {msg_count} messages")
            
            # Update close button visibility
            try:
                close_button = self.query_one("#close-button", Button)
                if tab_count > 1:
                    close_button.display = True
                else:
                    close_button.display = False
            except Exception:
                # Close button doesn't exist if only 1 tab
                pass
        except Exception:
            pass
