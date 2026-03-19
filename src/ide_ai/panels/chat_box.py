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

from textual.app import ComposeResult
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
        border: round $panel-lighten-2;
        padding: 0;
    }
    ChatBox.--focused-box {
        border: round $accent;
    }
    ChatBox > #box-header {
        height: 1;
        background: $panel-lighten-2;
        layout: horizontal;
        padding: 0 1;
    }
    ChatBox.--focused-box > #box-header {
        background: $accent 20%;
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
        ("ctrl+enter", "send_message", "Send"),
        ("ctrl+l", "clear_chat", "Clear"),
        ("ctrl+y", "toggle_provider", "Switch AI"),
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
        with Horizontal(id="chat-input-row"):
            yield Static(">", id="input-prompt")
            yield Input(placeholder="Ask AI… (or /claude, /copilot)", id="chat-input")

    def on_mount(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(f"[dim]Session {self.number} · {self.provider.name} · Ctrl+Enter send[/]\n")

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
        busy = self.query_one("#box-busy", Static)
        self._busy = True
        busy.update("⏳")
        log.write(f"\n[bold cyan]You:[/] {message}\n[bold green]{self.provider.name}:[/] ")
        try:
            async for chunk in self.provider.send(message):
                log.write(chunk)
                log.scroll_end(animate=False)
        except Exception as exc:
            log.write(f"\n[bold red]Error:[/] {exc}\n")
        finally:
            log.write("\n")
            self._busy = False
            busy.update("")
