from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, RichLog, Static

from ..ai.base import AIProvider
from ..ai.claude import ClaudeProvider
from ..ai.copilot import CopilotProvider
from ..status_indicators import StatusIndicators

_PROVIDERS: list[type[AIProvider]] = [ClaudeProvider, CopilotProvider]


class AIChatPanel(Vertical):
    """AI Chat panel: conversation history + input box."""

    DEFAULT_CSS = """
    /* AIChatPanel: Inactive state
       - Very subtle background for visual hierarchy
       - Muted text indicates non-focused state
       - Smooth transitions when focusing
    */
    AIChatPanel {
        height: 1fr;
        background: $panel-lighten-3 5%;   /* Very subtle inactive background */
        color: $text-muted;                /* Dimmed text indicates inactive */
        transition: color 200ms, background 200ms;
    }
    
    /* AIChatPanel: Focused state
       - Transparent background to highlight border
       - Full-contrast text
    */
    AIChatPanel.--focused-box {
        background: transparent;           /* Let border stand out */
        color: $text;                      /* Full-contrast text */
    }
    
    /* Chat log: Message history area
       - Subtle border in inactive state
       - Bright accent border when focused
    */
    AIChatPanel > #chat-log {
        height: 1fr;
        border: solid $panel-lighten-1;    /* Fine line structure */
        padding: 1 1;
        transition: border 200ms;
    }
    
    AIChatPanel.--focused-box > #chat-log {
        border: solid $accent 50%;         /* Bright accent border with transparency */
    }
    
    /* Chat input bar: Horizontal layout for provider + input */
    AIChatPanel > #chat-input-bar {
        height: 3;
        border-top: solid $panel-lighten-1; /* Fine line separator */
    }
    
    /* Provider label: AI model indicator
       - Accent color for action prompts
    */
    AIChatPanel > #chat-input-bar > #provider-label {
        width: auto;
        padding: 0 1;
        content-align: center middle;
        color: $accent;                    /* Accent color for provider indicator */
    }
    
    /* Chat input field: User message entry */
    AIChatPanel > #chat-input-bar > #chat-input {
        width: 1fr;
        border: none;
    }
    """

    BINDINGS = [
        Binding("ctrl+enter", "send_message", "Send"),
        Binding("ctrl+l", "clear_chat", "Clear", priority=True),
        Binding("ctrl+shift+a", "toggle_provider", "Switch AI"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._providers = [cls() for cls in _PROVIDERS]
        self._provider_index = 0
        self._busy = False

    @property
    def provider(self) -> AIProvider:
        return self._providers[self._provider_index]

    def compose(self) -> ComposeResult:
        yield RichLog(id="chat-log", highlight=True, markup=True, wrap=True)
        with Horizontal(id="chat-input-bar"):
            provider_emoji = "🤖" if "claude" in self.provider.name.lower() else "🐙"
            yield Static(f"{provider_emoji} [{self.provider.name}]", id="provider-label")
            yield Input(placeholder="Ask AI… (Ctrl+Enter to send)", id="chat-input")

    def on_mount(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(
            f"[bold green]ide.ai[/] — AI Chat  "
            f"[dim]provider: {self.provider.name}  "
            f"Ctrl+Enter send · Ctrl+L clear · Ctrl+Shift+A switch AI[/]\n"
        )
        self.query_one("#chat-input", Input).focus()

    def action_send_message(self) -> None:
        inp = self.query_one("#chat-input", Input)
        msg = inp.value.strip()
        if not msg or self._busy:
            return
        inp.value = ""
        self.run_worker(self._stream_response(msg), exclusive=True)

    def action_clear_chat(self) -> None:
        self.query_one("#chat-log", RichLog).clear()

    def action_toggle_provider(self) -> None:
        self._provider_index = (self._provider_index + 1) % len(self._providers)
        label = self.query_one("#provider-label", Static)
        provider_emoji = "🤖" if "claude" in self.provider.name.lower() else "🐙"
        label.update(f"{provider_emoji} [{self.provider.name}]")
        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[dim]— Switched to {self.provider.name} —[/]\n")

    def set_active(self, active: bool) -> None:
        if active:
            self.add_class("--focused-box")
        else:
            self.remove_class("--focused-box")

    async def _stream_response(self, message: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        self._busy = True
        log.write(f"\n[bold cyan]You:[/] {message}\n")
        log.write(f"[bold green]{self.provider.name}:[/] {StatusIndicators.get_streaming()} ")
        try:
            async for chunk in self.provider.send(message):
                log.write(chunk)
            log.write(f" {StatusIndicators.get_success()}\n")
        except Exception as exc:
            log.write(f"\n[bold red]{StatusIndicators.get_error()} Error:[/] {exc}\n")
        finally:
            self._busy = False
