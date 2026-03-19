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
    }
    FileTreePanel > #tree-header {
        height: 1;
        padding: 0 1;
        background: $panel-lighten-2;
        color: $foreground-muted;
        text-style: bold;
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
