import os

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import DirectoryTree, Static
from textual.containers import Vertical


class FileTreePanel(Vertical):
    """File tree navigator using Textual's DirectoryTree."""

    DEFAULT_CSS = """
    FileTreePanel {
        width: 24;
        height: 1fr;
        border: solid $panel-lighten-1;
        background: $panel-lighten-3 5%;
        color: $text-muted;
        transition: color 200ms, border 200ms, background 200ms;
    }
    FileTreePanel.--focused-box {
        border: solid $accent 50%;
        background: transparent;
        color: $text;
    }
    FileTreePanel > #tree-header {
        height: 1;
        padding: 0 2;
        background: $panel-lighten-2;
        color: $text-muted;
        text-style: bold;
        transition: background 200ms, color 200ms;
    }
    FileTreePanel.--focused-box > #tree-header {
        background: $accent 10%;
        color: $accent;
    }
    FileTreePanel > DirectoryTree {
        height: 1fr;
        scrollbar-gutter: stable;
    }
    """

    class FileOpened(Message):
        """Posted when user selects a file."""

        def __init__(self, path: str) -> None:
            super().__init__()
            self.path = path

    def __init__(self, path: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._root = path or os.getcwd()

    def compose(self) -> ComposeResult:
        root_name = os.path.basename(self._root) or self._root
        yield Static(f"📁 {root_name}", id="tree-header")
        yield DirectoryTree(self._root)

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        self.post_message(FileTreePanel.FileOpened(str(event.path)))

    def set_active(self, active: bool) -> None:
        if active:
            self.add_class("--focused-box")
        else:
            self.remove_class("--focused-box")
