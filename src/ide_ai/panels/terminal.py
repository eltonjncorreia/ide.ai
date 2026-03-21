from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, RichLog, Static


class TerminalPanel(Vertical):
    """Simple embedded terminal: command input + async subprocess output."""

    DEFAULT_CSS = """
    TerminalPanel {
        height: 1fr;
        border: solid $panel-lighten-1;
        background: $panel-lighten-3 5%;
        color: $text-muted;
        transition: color 200ms, border 200ms, background 200ms;
    }
    TerminalPanel.--focused-box {
        border: solid $accent 50%;
        background: transparent;
        color: $text;
    }
    TerminalPanel > #term-header {
        height: 1;
        padding: 0 2;
        background: $panel-lighten-2;
        color: $text-muted;
        text-style: bold;
        transition: background 200ms, color 200ms;
    }
    TerminalPanel.--focused-box > #term-header {
        background: $accent 10%;
        color: $accent;
    }
    TerminalPanel > #term-log {
        height: 1fr;
        padding: 1 1;
    }
    TerminalPanel > #term-input-bar {
        height: 3;
        border-top: solid $panel-lighten-1;
    }
    TerminalPanel > #term-input-bar > #term-prompt {
        width: auto;
        padding: 0 1;
        content-align: center middle;
        color: $success;
    }
    TerminalPanel > #term-input-bar > #term-input {
        width: 1fr;
        border: none;
    }
    """

    BINDINGS = [
        ("ctrl+l", "clear_term", "Clear"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        import os
        self._cwd = os.getcwd()

    def compose(self) -> ComposeResult:
        yield Static("Terminal", id="term-header")
        yield RichLog(id="term-log", highlight=False, markup=False, wrap=True)
        with Horizontal(id="term-input-bar"):
            yield Static("$", id="term-prompt")
            yield Input(placeholder="command…", id="term-input")

    def on_mount(self) -> None:
        log = self.query_one("#term-log", RichLog)
        log.write(f"Terminal — cwd: {self._cwd}\n")
        self.query_one("#term-input", Input).focus()

    def set_active(self, active: bool) -> None:
        if active:
            self.add_class("--focused-box")
        else:
            self.remove_class("--focused-box")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "term-input":
            cmd = event.value.strip()
            event.input.value = ""
            if cmd:
                self.run_worker(self._run_command(cmd), exclusive=False)

    def action_clear_term(self) -> None:
        self.query_one("#term-log", RichLog).clear()

    async def _run_command(self, cmd: str) -> None:
        import asyncio
        log = self.query_one("#term-log", RichLog)
        log.write(f"$ {cmd}\n")
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=self._cwd,
            )
            assert proc.stdout
            while True:
                chunk = await proc.stdout.read(512)
                if not chunk:
                    break
                log.write(chunk.decode(errors="replace"))
            await proc.wait()
            if proc.returncode and proc.returncode != 0:
                log.write(f"[exit {proc.returncode}]\n")
        except Exception as exc:
            log.write(f"Error: {exc}\n")
