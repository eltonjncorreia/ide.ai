"""
ChatBox — a single "caixinha" de AI chat.

Aparência quando 3 caixinhas na tela:
╭─ [1] Claude ─────╮ ╭─ [2] Copilot ────╮ ╭─ [3] Claude ─────╮
│ You: hello       │ │                  │ │                  │
│ Claude: Hi! ...  │ │                  │ │                  │
│                  │ │                  │ │                  │
│ > _              │ │ > _              │ │ > _              │
╰──────────────────╯ ╰──────────────────╯ ╰──────────────────╯
"""

from __future__ import annotations

import asyncio

from rich.markup import escape
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Input, RichLog, Select, Static

from ..ai.claude import ClaudeProvider
from ..ai.copilot import CopilotProvider
from ..ai.base import AIProvider

_PROVIDERS: list[type[AIProvider]] = [ClaudeProvider, CopilotProvider]


class ChatBox(Vertical):
    """Self-contained AI chat panel — one 'caixinha'."""

    DEFAULT_CSS = """
    ChatBox {
        height: 1fr;
        border: solid $panel-lighten-1;
        padding: 0;
    }
    ChatBox.--focused-box {
        border: solid $accent 50%;
    }
    ChatBox > #box-header {
        height: 1;
        background: $panel-lighten-2;
        layout: horizontal;
        padding: 0 1;
    }
    ChatBox.--focused-box > #box-header {
        background: $accent 10%;
    }
    ChatBox > #box-header > #box-title {
        width: 1fr;
        color: $text-muted;
    }
    ChatBox.--focused-box > #box-header > #box-title {
        color: $accent;
        text-style: bold;
    }
    ChatBox > #box-header > #box-busy {
        width: auto;
        color: $warning;
    }
    ChatBox > #box-header > #provider-select {
        width: auto;
        min-width: 12;
        height: 1;
        border: none;
        background: transparent;
        padding: 0;
    }
    ChatBox > #chat-log {
        height: 1fr;
        padding: 0 1;
    }
    ChatBox > #stream-preview {
        height: auto;
        min-height: 1;
        padding: 0 1;
        color: $text;
    }
    ChatBox > #chat-input-row {
        height: 3;
        layout: horizontal;
        border-top: solid $panel-lighten-1;
    }
    ChatBox > #chat-input-row > #input-prompt {
        width: auto;
        padding: 0 1;
        content-align: center middle;
        color: $accent;
    }
    ChatBox > #chat-input-row > #chat-input {
        width: 1fr;
        border: none;
    }
    """

    BINDINGS = [
        Binding("ctrl+enter", "send_message", "Send"),
        Binding("ctrl+l", "clear_chat", "Clear", priority=True),
        Binding("ctrl+y", "toggle_provider", "Switch AI"),
        Binding("ctrl+shift+c", "copy_response", "Copy last response"),
        Binding("ctrl+shift+a", "copy_conversation", "Copy all"),
    ]

    class Focused(Message):
        """Posted when box is clicked/focused."""
        def __init__(self, box: "ChatBox") -> None:
            super().__init__()
            self.box = box

    def __init__(self, number: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.number = number
        self._providers = [cls() for cls in _PROVIDERS]
        self._provider_index = 0
        self._busy = False
        self._last_response: str = ""
        self._conversation: list[str] = []  # plain-text lines for copy

    @property
    def provider(self) -> AIProvider:
        return self._providers[self._provider_index]

    def compose(self) -> ComposeResult:
        _options = [(cls().name, i) for i, cls in enumerate(_PROVIDERS)]
        with Horizontal(id="box-header"):
            yield Static(self._title_markup(), id="box-title")
            yield Select(_options, value=0, id="provider-select", allow_blank=False)
            yield Static("", id="box-busy")
        yield RichLog(id="chat-log", highlight=True, markup=True, wrap=True)
        yield Static("", id="stream-preview")
        with Horizontal(id="chat-input-row"):
            yield Static(">", id="input-prompt")
            yield Input(placeholder="Ask AI… (or /claude, /copilot)", id="chat-input")

    def on_mount(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(
            f"[dim]Session {self.number} · {self.provider.name} · "
            f"Ctrl+Enter send · Ctrl+Shift+C copy response · Ctrl+Shift+A copy all[/]\n"
        )

    def on_focus(self) -> None:
        self.post_message(ChatBox.Focused(self))

    def on_descendant_focus(self) -> None:
        self.post_message(ChatBox.Focused(self))

    def on_click(self) -> None:
        self.query_one("#chat-input", Input).focus()

    def on_input_focus(self, event: Input.Focus) -> None:
        pass  # handled by on_descendant_focus

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Send message when user presses Enter in the chat input."""
        self.action_send_message()

    def set_active(self, active: bool) -> None:
        if active:
            self.add_class("--focused-box")
        else:
            self.remove_class("--focused-box")
        self._update_header()

    def _title_markup(self) -> str:
        return f"[{self.number}] {self.provider.name}"

    def _update_header(self) -> None:
        self.query_one("#box-title", Static).update(self._title_markup())

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "provider-select" and event.value is not Select.BLANK:
            self._provider_index = int(event.value)
            self._update_header()
            log = self.query_one("#chat-log", RichLog)
            log.write(f"\n[dim]— switched to {self.provider.name} —[/]\n")

    # ── actions ────────────────────────────────────────────────────────────

    def action_send_message(self) -> None:
        inp = self.query_one("#chat-input", Input)
        msg = inp.value.strip()
        if not msg or self._busy:
            return

        # slash commands: /claude  /copilot
        lower = msg.lower()
        for i, cls in enumerate(_PROVIDERS):
            if lower == f"/{cls().name.lower()}":
                inp.value = ""
                self._provider_index = i
                self._update_header()
                sel = self.query_one("#provider-select", Select)
                sel.value = i
                log = self.query_one("#chat-log", RichLog)
                log.write(f"\n[dim]— switched to {self.provider.name} —[/]\n")
                return

        inp.value = ""
        self.run_worker(self._stream(msg), exclusive=True, name=f"box-{self.id}")

    def action_clear_chat(self) -> None:
        self.query_one("#chat-log", RichLog).clear()
        self._last_response = ""
        self._conversation.clear()

    def action_copy_response(self) -> None:
        if not self._last_response:
            self.app.notify("No response to copy yet.", severity="warning")
            return
        self.app.copy_to_clipboard(self._last_response)
        self.app.notify("Last response copied to clipboard.", timeout=2)

    def action_copy_conversation(self) -> None:
        if not self._conversation:
            self.app.notify("Nothing to copy yet.", severity="warning")
            return
        self.app.copy_to_clipboard("\n".join(self._conversation))
        self.app.notify("Conversation copied to clipboard.", timeout=2)

    def action_toggle_provider(self) -> None:
        self._provider_index = (self._provider_index + 1) % len(self._providers)
        sel = self.query_one("#provider-select", Select)
        sel.value = self._provider_index
        self._update_header()
        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[dim]— {self.provider.name} —[/]\n")

    # ── streaming ──────────────────────────────────────────────────────────

    async def _stream(self, message: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        preview = self.query_one("#stream-preview", Static)
        busy = self.query_one("#box-busy", Static)
        self._busy = True
        self._last_response = ""
        busy.update("⏳")
        log.write(f"[bold cyan]You:[/] {escape(message)}")
        self._conversation.append(f"You: {message}")
        response_buf: list[str] = []
        provider_name = self.provider.name
        accumulated = ""
        last_flush = asyncio.get_event_loop().time()
        try:
            async for chunk in self.provider.send(message):
                accumulated += chunk
                response_buf.append(chunk)
                now = asyncio.get_event_loop().time()
                if now - last_flush >= 0.05:  # atualiza preview a cada 50 ms
                    preview.update(f"[bold green]{provider_name}:[/] {escape(accumulated)}")
                    log.scroll_end(animate=False)
                    last_flush = now
        except Exception as exc:
            preview.update(f"[bold red]Error:[/] {escape(str(exc))}")
        finally:
            self._last_response = accumulated
            if self._last_response:
                log.write(f"[bold green]{provider_name}:[/] {escape(self._last_response)}")
                self._conversation.append(f"{provider_name}: {self._last_response}")
            preview.update("")
            log.scroll_end(animate=False)
            self._busy = False
            busy.update("")
