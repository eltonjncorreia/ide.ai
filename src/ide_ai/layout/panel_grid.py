"""
PanelGrid — grade responsiva de ChatBoxes (caixinhas).

Responsividade automática:
 < 80 cols  → 1 coluna
 80-159     → 2 colunas
 160-239    → 3 colunas
 ≥ 240      → 4 colunas
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.events import Resize
from textual.message import Message
from textual.widget import Widget

from ..panels.chat_box import ChatBox

_COLS_THRESHOLDS = [(240, 4), (160, 3), (80, 2), (0, 1)]


def _cols_for_width(width: int) -> int:
    for threshold, cols in _COLS_THRESHOLDS:
        if width >= threshold:
            return cols
    return 1


class PanelGrid(Widget):
    """CSS-grid container. Adjusts columns automatically on resize."""

    DEFAULT_CSS = """
    PanelGrid {
        layout: grid;
        grid-size: 1;
        grid-gutter: 1 1;
        height: 1fr;
        padding: 0 1;
    }
    """

    class ActiveChanged(Message):
        """Posted when the active box changes."""
        def __init__(self, grid: "PanelGrid") -> None:
            super().__init__()
            self.grid = grid

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._counter = 0
        self._active_id: str | None = None
        self._box_ids: list[str] = []

    def compose(self) -> ComposeResult:
        return iter([])

    def on_mount(self) -> None:
        self._add_box()

    def on_resize(self, event: Resize) -> None:
        self.styles.grid_size_columns = _cols_for_width(event.size.width)

    def on_chat_box_focused(self, event: ChatBox.Focused) -> None:
        self._set_active(event.box.id)

    # ── public API ─────────────────────────────────────────────────────────

    @property
    def box_count(self) -> int:
        return len(self._box_ids)

    def add_box(self) -> None:
        self._add_box()

    def close_active(self) -> bool:
        if len(self._box_ids) <= 1:
            return False
        bid = self._active_id
        if bid is None:
            return False
        idx = self._box_ids.index(bid)
        self._box_ids.remove(bid)
        box = self.query_one(f"#{bid}", ChatBox)
        new_id = self._box_ids[max(0, idx - 1)]
        self._set_active(new_id)
        self.query_one(f"#{new_id}", ChatBox).query_one("#chat-input").focus()
        box.remove()
        return True

    def focus_next(self) -> None:
        if not self._box_ids or self._active_id is None:
            return
        idx = (self._box_ids.index(self._active_id) + 1) % len(self._box_ids)
        self._jump(self._box_ids[idx])

    def focus_prev(self) -> None:
        if not self._box_ids or self._active_id is None:
            return
        idx = (self._box_ids.index(self._active_id) - 1) % len(self._box_ids)
        self._jump(self._box_ids[idx])

    def _jump(self, bid: str) -> None:
        self._set_active(bid)
        self.query_one(f"#{bid}", ChatBox).query_one("#chat-input").focus()

    # ── internal ───────────────────────────────────────────────────────────

    def _add_box(self) -> None:
        self._counter += 1
        bid = f"chatbox-{self._counter}"
        box = ChatBox(number=self._counter, id=bid)
        self._box_ids.append(bid)
        self.mount(box)
        self._set_active(bid)
        self.call_after_refresh(self._focus_box, bid)

    def _focus_box(self, bid: str) -> None:
        try:
            self.query_one(f"#{bid}", ChatBox).query_one("#chat-input").focus()
        except Exception:
            pass

    def _set_active(self, bid: str) -> None:
        if self._active_id == bid:
            return
        if self._active_id:
            try:
                self.query_one(f"#{self._active_id}", ChatBox).set_active(False)
            except Exception:
                pass
        self._active_id = bid
        try:
            self.query_one(f"#{bid}", ChatBox).set_active(True)
        except Exception:
            pass
        self.post_message(PanelGrid.ActiveChanged(self))
