"""
ContextManager — Handle file context for AI interactions.

Allows users to include file contents as context when sending messages to AI.
- Load and cache file contents
- Format files as context (with proper formatting)
- Track which files are included in context
- Display context info in UI
"""

from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ContextFile:
    """Represents a file included in context."""
    path: str
    content: str
    language: str = ""
    file_size: int = 0

    @classmethod
    def from_path(cls, file_path: str) -> ContextFile | None:
        """Load a file and create ContextFile from path."""
        try:
            path = Path(file_path)
            if not path.exists():
                return None

            content = path.read_text(encoding="utf-8", errors="ignore")
            language = cls._detect_language(str(path))
            file_size = len(content)

            return cls(
                path=str(path),
                content=content,
                language=language,
                file_size=file_size,
            )
        except Exception:
            return None

    @staticmethod
    def _detect_language(file_path: str) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".sh": "bash",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".sql": "sql",
            ".md": "markdown",
        }
        ext = Path(file_path).suffix.lower()
        return extension_map.get(ext, "text")

    def format_as_context(self) -> str:
        """Format file as context string for AI."""
        header = f"\n--- File: {self.path} ---"
        if self.language:
            header += f" [{self.language}]"
        
        content = f"\n```{self.language}\n{self.content}\n```"
        return header + content


class ContextManager:
    """Manage file context for AI interactions."""

    def __init__(self) -> None:
        """Initialize context manager."""
        self.context_files: dict[str, ContextFile] = {}
        self.max_context_size: int = 50000  # Max total characters

    def add_file(self, file_path: str) -> bool:
        """Add a file to context by path.
        
        Returns True if file was successfully added, False otherwise.
        """
        file_path = os.path.abspath(file_path)
        
        context_file = ContextFile.from_path(file_path)
        if not context_file:
            return False

        # Check total size
        current_size = sum(f.file_size for f in self.context_files.values())
        if current_size + context_file.file_size > self.max_context_size:
            return False

        self.context_files[file_path] = context_file
        return True

    def remove_file(self, file_path: str) -> bool:
        """Remove a file from context.
        
        Returns True if file was removed, False if not found.
        """
        file_path = os.path.abspath(file_path)
        if file_path in self.context_files:
            del self.context_files[file_path]
            return True
        return False

    def clear_context(self) -> None:
        """Clear all files from context."""
        self.context_files.clear()

    def get_context_string(self) -> str:
        """Get formatted context string with all included files."""
        if not self.context_files:
            return ""

        parts = ["=== CONTEXT ==="]
        for file_path, context_file in self.context_files.items():
            parts.append(context_file.format_as_context())
        parts.append("=== END CONTEXT ===\n")
        
        return "\n".join(parts)

    def get_file_list(self) -> list[str]:
        """Get list of file paths in context."""
        return list(self.context_files.keys())

    def get_context_info(self) -> str:
        """Get human-readable context info (for UI display)."""
        if not self.context_files:
            return "No files in context"

        file_count = len(self.context_files)
        total_size = sum(f.file_size for f in self.context_files.values())
        
        files_summary = ", ".join(
            Path(p).name for p in self.context_files.keys()
        )
        
        return f"{file_count} file(s) • {total_size} chars • {files_summary}"

    def has_context(self) -> bool:
        """Check if any files are in context."""
        return bool(self.context_files)
