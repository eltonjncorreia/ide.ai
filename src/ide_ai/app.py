import os

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Static

from .layout.panel_grid import PanelGrid


class IdeApp(App[None]):
    """ide.ai — múltiplas caixinhas de AI chat no terminal."""

    CSS_PATH = "app.tcss"
    TITLE = "ide.ai"

    BINDINGS = [
        Binding("ctrl+n", "new_box", "New chat", show=True),
        Binding("ctrl+w", "close_box", "Close", show=True),
        Binding("ctrl+right_square_bracket", "next_box", "Next panel", show=True),
        Binding("ctrl+left_square_bracket", "prev_box", "Prev panel", show=False),
        Binding("q", "quit", "Quit", show=True),
    ]

    def compose(self) -> ComposeResult:
        self.sub_title = os.path.basename(os.getcwd())
        yield Header(show_clock=True)
        yield PanelGrid(id="panel-grid")
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_status()

    def on_panel_grid_active_changed(self, event: PanelGrid.ActiveChanged) -> None:
        self._refresh_status()

    def _refresh_status(self) -> None:
        try:
            grid = self.query_one(PanelGrid)
            n = grid.box_count
            hint = "[dim]Ctrl+N new · Ctrl+W close · Tab next[/]"
            boxes_hint = f"[bold]{n}[/] {'chat' if n == 1 else 'chats'}"
            self.query_one("#status-bar", Static).update(f" {boxes_hint}  {hint}")
        except Exception:
            pass

    # ── actions ────────────────────────────────────────────────────────────

    def action_new_box(self) -> None:
        self.query_one(PanelGrid).add_box()
        self._refresh_status()

    def action_close_box(self) -> None:
        grid = self.query_one(PanelGrid)
        if not grid.close_active():
            self.notify("Última caixinha — não pode fechar.", severity="warning")
        self._refresh_status()

    def action_next_box(self) -> None:
        self.query_one(PanelGrid).focus_next()

    def action_prev_box(self) -> None:
        self.query_one(PanelGrid).focus_prev()


def run() -> None:
    IdeApp().run()


if __name__ == "__main__":
    run()
