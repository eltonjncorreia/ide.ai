from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, RichLog, Static


class TerminalPanel(Vertical):
    """Simple embedded terminal: command input + async subprocess output."""

    DEFAULT_CSS = """
    /* Terminal panel: Inactive state
       - Subtle border and background for visual hierarchy
       - Muted text indicates non-focused state
       - Smooth transitions when focusing
    */
    TerminalPanel {
        height: 1fr;
        border: solid $panel-lighten-1;    /* Fine line structure */
        background: $panel-lighten-3 5%;   /* Very subtle inactive background */
        color: $text-muted;                /* Dimmed text indicates inactive */
        transition: color 200ms, border 200ms, background 200ms;
    }
    
    /* Terminal panel: Focused state
       - Bright accent border for clear focus indication
       - Transparent background to highlight border
       - Full-contrast text
    */
    TerminalPanel.--focused-box {
        border: solid $accent 50%;         /* Bright accent border with transparency */
        background: transparent;           /* Let border stand out */
        color: $text;                      /* Full-contrast text */
    }
    
    /* Terminal header: Inactive state
       - Slightly elevated from panel background
       - Muted text to indicate secondary content
    */
    TerminalPanel > #term-header {
        height: 1;
        padding: 0 2;
        background: $panel-lighten-2;      /* Slightly elevated background */
        color: $text-muted;                /* Muted text for inactive state */
        text-style: bold;
        transition: background 200ms, color 200ms;
    }
    
    /* Terminal header: Focused state
       - Subtle accent tint for visual consistency
       - Accent text color matches focused border
    */
    TerminalPanel.--focused-box > #term-header {
        background: $accent 10%;           /* Subtle accent tint */
        color: $accent;                    /* Accent text for focus indication */
    }
    
    /* Terminal output log: Scrollable content area */
    TerminalPanel > #term-log {
        height: 1fr;
        padding: 1 1;
    }
    
    /* Terminal input bar: Horizontal layout for prompt + input */
    TerminalPanel > #term-input-bar {
        height: 3;
        border-top: solid $panel-lighten-1; /* Fine line separator */
    }
    
    /* Terminal prompt symbol: Shell "$" indicator
       - Success color (green) following terminal convention
    */
    TerminalPanel > #term-input-bar > #term-prompt {
        width: auto;
        padding: 0 1;
        content-align: center middle;
        color: $success;                   /* Success (green) for shell prompt */
    }
    
    /* Terminal input field: Command entry */
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
        yield Static("⌘ Terminal", id="term-header")
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
