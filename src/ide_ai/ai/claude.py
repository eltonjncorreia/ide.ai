import asyncio
import shutil
from collections.abc import AsyncIterator

from .base import AIProvider


class ClaudeProvider(AIProvider):
    """Streams responses from the `claude` CLI via asyncio subprocess."""

    @property
    def name(self) -> str:
        return "Claude"

    async def send(self, message: str, context: list[str] = []) -> AsyncIterator[str]:  # type: ignore[override]
        if not shutil.which("claude"):
            async for chunk in _mock_stream(message):
                yield chunk
            return

        full_message = "\n\n".join([*context, message]) if context else message
        proc = await asyncio.create_subprocess_exec(
            "claude", "-p", full_message,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        assert proc.stdout
        assert proc.stderr
        while True:
            chunk = await proc.stdout.read(256)
            if not chunk:
                break
            yield chunk.decode(errors="replace")
        _, stderr_data = await proc.communicate()
        if proc.returncode != 0 and stderr_data:
            yield f"\n[bold red]Error (exit {proc.returncode}):[/] {stderr_data.decode(errors='replace')}\n"

    async def clear_session(self) -> None:
        pass  # stateless per-call


async def _mock_stream(message: str) -> AsyncIterator[str]:
    """Fallback when `claude` CLI is not installed."""
    response = (
        f"[bold yellow]⚠ claude CLI not found.[/]\n\n"
        f"Install with: `npm install -g @anthropic-ai/claude-code`\n\n"
        f"Your message: _{message}_"
    )
    for word in response.split():
        yield word + " "
        await asyncio.sleep(0.02)
