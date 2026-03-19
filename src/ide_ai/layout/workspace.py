"""
Workspace management — Termux-inspired multi-screen switcher.

Layout:
┌──────────────────────────────────────────────────────────┐
│  [main content area — ContentSwitcher]                   │
├──────────────────────────────────────────────────────────┤
│ ❯1:chat  2:dev  3:term  [+]             Ctrl+1-9 switch  │  <- WorkspaceBar
└──────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, HorizontalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import ContentSwitcher, Static

from ..panels.ai_chat import AIChatPanel
from ..panels.file_tree import FileTreePanel
from ..panels.terminal import TerminalPanel

WorkspaceKind = Literal["chat", "dev", "term"]


@dataclass
class WorkspaceInfo:
    id: str
    kind: WorkspaceKind
    label: str


def _make_chat_workspace(ws_id: str) -> Widget:
    return AIChatPanel(id=ws_id)


def _make_dev_workspace(ws_id: str) -> Widget:
    """3-column layout: FileTree | AIChat | Terminal (bottom)."""

    class DevLayout(Vertical):
        DEFAULT_CSS = """
        DevLayout {
            height: 1fr;
        }
        DevLayout > #dev-top {
            height: 2fr;
            layout: horizontal;
        }
        DevLayout > #dev-top > FileTreePanel {
            width: 26;
        }
        DevLayout > #dev-top > AIChatPanel {
            width: 1fr;
        }
        DevLayout > TerminalPanel {
            height: 1fr;
            max-height: 14;
        }
        """

        def compose(self) -> ComposeResult:
            with Horizontal(id="dev-top"):
                yield FileTreePanel()
                yield AIChatPanel()
            yield TerminalPanel()

    return DevLayout(id=ws_id)


def _make_term_workspace(ws_id: str) -> Widget:
    return TerminalPanel(id=ws_id)


_BUILDERS = {
    "chat": _make_chat_workspace,
    "dev": _make_dev_workspace,
    "term": _make_term_workspace,
}

_KIND_EMOJI = {"chat": "💬", "dev": "🛠", "term": "⚡"}


class WorkspaceBar(Widget):
    """
    Bottom bar showing numbered workspaces — Termux-style.
    Displays: ❯1:chat  2:dev  3:term
    """

    DEFAULT_CSS = """
    WorkspaceBar {
        height: 1;
        background: $panel-lighten-2;
        layout: horizontal;
        dock: bottom;
    }
    WorkspaceBar > #ws-slots {
        width: 1fr;
        height: 1;
    }
    WorkspaceBar > #ws-hint {
        width: auto;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("", id="ws-slots")
        yield Static("Ctrl+1-9 · Ctrl+T new · Ctrl+W close", id="ws-hint")

    def refresh_slots(self, workspaces: list[WorkspaceInfo], active_id: str) -> None:
        parts: list[str] = []
        for i, ws in enumerate(workspaces, 1):
            label = f" {i}:{ws.kind} "
            if ws.id == active_id:
                parts.append(f"[bold reverse]{label}[/]")
            else:
                parts.append(label)
        self.query_one("#ws-slots", Static).update("  ".join(parts))


class WorkspaceManager(Vertical):
    """
    Manages multiple workspaces and the bottom WorkspaceBar.
    Workspaces are like Termux sessions — numbered, switchable, persistent.
    """

    DEFAULT_CSS = """
    WorkspaceManager {
        height: 1fr;
    }
    WorkspaceManager > ContentSwitcher {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("ctrl+t", "new_workspace", "New workspace", show=False),
        Binding("ctrl+w", "close_workspace", "Close workspace", show=False),
        Binding("ctrl+1", "goto_workspace(1)", "Workspace 1", show=False),
        Binding("ctrl+2", "goto_workspace(2)", "Workspace 2", show=False),
        Binding("ctrl+3", "goto_workspace(3)", "Workspace 3", show=False),
        Binding("ctrl+4", "goto_workspace(4)", "Workspace 4", show=False),
        Binding("ctrl+5", "goto_workspace(5)", "Workspace 5", show=False),
        Binding("ctrl+6", "goto_workspace(6)", "Workspace 6", show=False),
        Binding("ctrl+7", "goto_workspace(7)", "Workspace 7", show=False),
        Binding("ctrl+8", "goto_workspace(8)", "Workspace 8", show=False),
        Binding("ctrl+9", "goto_workspace(9)", "Workspace 9", show=False),
    ]

    _workspaces: list[WorkspaceInfo]
    _active_id: str

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._workspaces = []
        self._active_id = ""
        self._counter = 0

    # ── lifecycle ──────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield ContentSwitcher()
        yield WorkspaceBar()

    def on_mount(self) -> None:
        self._add_workspace("chat")  # start with one chat workspace

    # ── public API ─────────────────────────────────────────────────────────

    def add_workspace(self, kind: WorkspaceKind = "chat") -> None:
        self._add_workspace(kind)

    def close_current(self) -> None:
        if len(self._workspaces) <= 1:
            self.app.notify("Can't close the last workspace", severity="warning")
            return
        idx = self._index_of(self._active_id)
        info = self._workspaces.pop(idx)
        switcher = self.query_one(ContentSwitcher)
        widget = switcher.query_one(f"#{info.id}")
        # Switch to neighbour before removing
        new_idx = max(0, idx - 1)
        new_info = self._workspaces[new_idx]
        self._activate(new_info.id)
        widget.remove()
        self._refresh_bar()

    def goto(self, n: int) -> None:
        """Go to 1-based workspace number."""
        idx = n - 1
        if 0 <= idx < len(self._workspaces):
            self._activate(self._workspaces[idx].id)

    # ── actions ────────────────────────────────────────────────────────────

    def action_new_workspace(self) -> None:
        self._add_workspace("chat")

    def action_close_workspace(self) -> None:
        self.close_current()

    def action_goto_workspace(self, n: int) -> None:
        self.goto(n)

    # ── internal ───────────────────────────────────────────────────────────

    def _add_workspace(self, kind: WorkspaceKind) -> None:
        self._counter += 1
        ws_id = f"ws-{self._counter}"
        info = WorkspaceInfo(id=ws_id, kind=kind, label=f"{kind} {self._counter}")
        self._workspaces.append(info)

        widget = _BUILDERS[kind](ws_id)
        switcher = self.query_one(ContentSwitcher)
        switcher.mount(widget)

        self._activate(ws_id)

    def _activate(self, ws_id: str) -> None:
        self._active_id = ws_id
        self.query_one(ContentSwitcher).current = ws_id
        self._refresh_bar()

    def _refresh_bar(self) -> None:
        self.query_one(WorkspaceBar).refresh_slots(self._workspaces, self._active_id)

    def _index_of(self, ws_id: str) -> int:
        return next(i for i, ws in enumerate(self._workspaces) if ws.id == ws_id)
