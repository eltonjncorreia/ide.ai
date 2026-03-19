import asyncio
import json
import shutil
from collections.abc import AsyncIterator

from .base import AIProvider


class CopilotProvider(AIProvider):
    """Streams responses from the standalone `copilot` CLI (GitHub Copilot CLI)."""

    @property
    def name(self) -> str:
        return "Copilot"

    async def send(self, message: str, context: list[str] = []) -> AsyncIterator[str]:  # type: ignore[override]
        if not shutil.which("copilot"):
            yield "[bold yellow]⚠ copilot CLI not found.[/]\nInstall: https://github.com/github/copilot-cli\n"
            return

        full_message = "\n\n".join([*context, message]) if context else message
        proc = await asyncio.create_subprocess_exec(
            "copilot", "--prompt", full_message, "--output-format", "json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        assert proc.stdout
        async for raw_line in proc.stdout:
            line = raw_line.decode(errors="replace").strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "assistant.message_delta":
                delta = event.get("data", {}).get("deltaContent", "")
                if delta:
                    yield delta
        await proc.wait()

    async def clear_session(self) -> None:
        pass
