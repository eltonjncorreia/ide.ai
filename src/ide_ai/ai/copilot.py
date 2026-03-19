import asyncio
import shutil
from collections.abc import AsyncIterator

from .base import AIProvider


class CopilotProvider(AIProvider):
    """Streams responses from `gh copilot suggest` CLI."""

    @property
    def name(self) -> str:
        return "Copilot"

    async def send(self, message: str, context: list[str] = []) -> AsyncIterator[str]:  # type: ignore[override]
        if not shutil.which("gh"):
            yield "[bold yellow]⚠ gh CLI not found.[/]\nInstall: https://cli.github.com\n"
            return

        full_message = "\n\n".join([*context, message]) if context else message
        proc = await asyncio.create_subprocess_exec(
            "gh", "copilot", "suggest", "-t", "generic", full_message,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        assert proc.stdout
        while True:
            chunk = await proc.stdout.read(256)
            if not chunk:
                break
            yield chunk.decode(errors="replace")
        await proc.wait()

    async def clear_session(self) -> None:
        pass
