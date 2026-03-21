import os

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import DirectoryTree, Static
from textual.containers import Vertical


class FileTreePanel(Vertical):
    """File tree navigator using Textual's DirectoryTree."""

    DEFAULT_CSS = """
    /* File tree panel: Inactive state
       - Subtle border and background for visual hierarchy
       - Muted text indicates non-focused state
       - Smooth transitions when focusing
    */
    FileTreePanel {
        width: 24;
        height: 1fr;
        border: solid $panel-lighten-1;    /* Fine line structure */
        background: $panel-lighten-3 5%;   /* Very subtle inactive background */
        color: $text-muted;                /* Dimmed text indicates inactive */
        transition: color 200ms, border 200ms, background 200ms;
    }
    
    /* File tree panel: Focused state
       - Bright accent border for clear focus indication
       - Transparent background to highlight border
       - Full-contrast text
    */
    FileTreePanel.--focused-box {
        border: solid $accent 50%;         /* Bright accent border with transparency */
        background: transparent;           /* Let border stand out */
        color: $text;                      /* Full-contrast text */
    }
    
    /* File tree header: Inactive state
       - Slightly elevated from panel background
       - Muted text to match inactive panel
    */
    FileTreePanel > #tree-header {
        height: 1;
        padding: 0 2;
        background: $panel-lighten-2;      /* Slightly elevated background */
        color: $text-muted;                /* Muted text for inactive state */
        text-style: bold;
        transition: background 200ms, color 200ms;
    }
    
    /* File tree header: Focused state
       - Subtle accent tint for visual consistency
       - Accent text color matches focused border
    */
    FileTreePanel.--focused-box > #tree-header {
        background: $accent 10%;           /* Subtle accent tint */
        color: $accent;                    /* Accent text for focus indication */
    }
    
    /* Directory tree: Scrollable content area */
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
